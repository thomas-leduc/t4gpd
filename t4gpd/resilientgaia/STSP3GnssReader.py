"""
Created on 2 jul. 2025

@author: tleduc

Copyright 2020-2025 Thomas Leduc

This file is part of t4gpd.

t4gpd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

t4gpd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with t4gpd.  If not, see <https://www.gnu.org/licenses/>.
"""

import gzip
from datetime import datetime
from geopandas import GeoDataFrame
from glob import glob
from os.path import isdir, isfile
from pandas import DataFrame, Timedelta, Timestamp, concat, date_range, merge_asof
from pandas.core.common import flatten
from pymap3d import Ellipsoid
from pymap3d.aer import ecef2aer
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class STSP3GnssReader(GeoProcess):
    """
    classdocs
    """

    def __init__(
        self, sensors, dtFieldName, sp3_files_or_dirname, freq=None, filter=None
    ):
        """
        Constructor
        """
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        self.sensors = sensors

        if not dtFieldName in sensors.columns:
            raise IllegalArgumentTypeException(
                dtFieldName, "dtFieldName must be a column name in sensors"
            )
        self.dtFieldName = dtFieldName
        self.sp3_files_or_dirname = sp3_files_or_dirname
        self.freq = freq  # "5min", "1h"
        self.filter = filter

    @staticmethod
    def __read_aux(sp3_filename):
        with gzip.open(sp3_filename, "rt") as f:
            lines = f.readlines()

        # Lecture des positions satellites dans le SP3
        sat_positions = []
        for line in lines:
            if line.startswith("*"):
                dt = " ".join(line[1:-3].split())
                dt = Timestamp(datetime.strptime(dt, "%Y %m %d %H %M %S.%f"))
            elif line.startswith("P"):
                satname, x, y, z, clock_corr = line[1:].split()[:5]
                # Convertir les coordonnées de kilomètres en mètres
                x, y, z = 1e3 * float(x), 1e3 * float(y), 1e3 * float(z)

                sat_positions.append(
                    {
                        "sat_dt": dt,
                        "sat_name": satname,
                        "x": x,
                        "y": y,
                        "z": z,
                    }
                )
        sat_positions = DataFrame(sat_positions)
        sat_positions.sat_dt = sat_positions.sat_dt.dt.tz_localize("UTC")
        return sat_positions

    @staticmethod
    def _read(sp3_files_or_dirname, freq=None, filter=None):
        if isinstance(sp3_files_or_dirname, (list, tuple)):
            sp3 = []
            for sp3_filename in sp3_files_or_dirname:
                if isfile(sp3_filename):
                    _sp3 = STSP3GnssReader.__read_aux(sp3_filename)
                sp3.append(_sp3)
            sp3 = concat(sp3, ignore_index=True)

        elif isfile(sp3_files_or_dirname):
            sp3 = STSP3GnssReader.__read_aux(sp3_files_or_dirname)

        elif isdir(sp3_files_or_dirname):
            sp3 = []
            for sp3_filename in glob(f"{sp3_files_or_dirname}/*.SP3.gz"):
                _sp3 = STSP3GnssReader.__read_aux(sp3_filename)
                sp3.append(_sp3)
            sp3 = concat(sp3, ignore_index=True)

        else:
            raise IllegalArgumentTypeException(
                sp3_files_or_dirname, "filename, list of filenames or dirname"
            )

        if not freq is None:
            dt0, dt1 = sp3.sat_dt.min(), sp3.sat_dt.max()
            dts = date_range(start=dt0, end=dt1, freq=freq)
            sp3 = sp3.query("sat_dt.isin(@dts)").copy(deep=True)

        if not filter is None:
            sp3 = sp3.query(filter).copy(deep=True)

        sp3.sort_values(by="sat_dt", inplace=True)
        return sp3

    @staticmethod
    def _merge_asof(sat_positions, sensors, timestampFieldName):
        joinTable = merge_asof(
            sensors[[timestampFieldName, "geometry"]],
            sat_positions[["sat_dt"]],
            left_on=timestampFieldName,
            right_on="sat_dt",
            tolerance=Timedelta("5min"),
            direction="nearest",
        )

        gdfs = []
        for _, row in joinTable.iterrows():
            dtViewpoint, geometry = row[timestampFieldName], row["geometry"]
            dtSat = row["sat_dt"]
            gdf = concat(
                [
                    DataFrame(columns=[timestampFieldName, "geometry"]),
                    sat_positions.query("sat_dt == @dtSat").copy(deep=True),
                ]
            )
            gdf[timestampFieldName] = dtViewpoint
            gdf.geometry = geometry
            gdfs.append(gdf)

        gdfs = GeoDataFrame(concat(gdfs, ignore_index=True), crs=sensors.crs)
        return gdfs

    @staticmethod
    def _ecef_to_aer(ecef_positions, h0):
        """Convert ECEF coordinates to AER (azimuth, elevation, slant range)"""

        def __ecef2aer_row(row, h0, ell):
            # https://geospace-code.github.io/pymap3d/aer.html#pymap3d.aer.ecef2aer
            lat0, lon0 = row.geometry.y, row.geometry.x
            az, el, srange = ecef2aer(
                row.x, row.y, row.z, lat0, lon0, h0, ell=ell, deg=True
            )
            return lat0, lon0, h0, az, el, srange

        ell = Ellipsoid.from_name("wgs84")

        aer_positions = ecef_positions.to_crs("epsg:4326").copy(deep=True)
        _df = DataFrame(
            aer_positions.apply(
                lambda row: __ecef2aer_row(row, h0, ell=ell), axis=1
            ).to_list(),
            columns=["lat0", "lon0", "h0", "az", "el", "sr"],
        )
        aer_positions = concat([aer_positions.reset_index(drop=True), _df], axis=1)
        aer_positions = GeoDataFrame(aer_positions, crs="epsg:4326").to_crs(
            ecef_positions.crs
        )
        aer_positions = aer_positions.drop(
            index=aer_positions[aer_positions.el < 0].index
        )
        return aer_positions

    @staticmethod
    def _transform_wide(aer_positions, timestampFieldName):
        columns = list(
            flatten(
                ["gid", timestampFieldName, "geometry"]
                + [
                    (
                        f"satcoordX_{sat}",
                        f"satcoordY_{sat}",
                        f"satcoordZ_{sat}",
                        f"{sat}_az",
                        f"{sat}_el",
                        f"{sat}_sr",
                    )
                    for sat in SatelliteLib.get_satellite_names(version=2)
                ]
            )
        )
        ht = {}
        for _, row in aer_positions.iterrows():
            key, sat = row[timestampFieldName], row["sat_name"]
            if not key in ht:
                ht[key] = {"timeUTC": key, "geometry": row["geometry"]}

            ht[key][f"{sat}_az"] = row["az"]
            ht[key][f"{sat}_el"] = row["el"]
            ht[key][f"{sat}_sr"] = row["sr"]

        rows = []
        for gid, (k, v) in enumerate(ht.items()):
            v.update({"gid": gid})
            rows.append(v)
        return GeoDataFrame(
            rows, columns=columns, geometry="geometry", crs=aer_positions.crs
        )

    def run(self):
        sat_positions = STSP3GnssReader._read(
            self.sp3_files_or_dirname, self.freq, self.filter
        )
        ecef_positions = STSP3GnssReader._merge_asof(
            sat_positions, self.sensors, self.dtFieldName
        )
        aer_positions = STSP3GnssReader._ecef_to_aer(ecef_positions, h0=0.0)
        aer_positions = STSP3GnssReader._transform_wide(aer_positions, self.dtFieldName)
        return aer_positions

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from pytz import timezone
        from t4gpd.resilientgaia.STECEF2AERSatelliteReader import (
            STECEF2AERSatelliteReader,
        )
        from t4gpd.resilientgaia.STSatelliteOnSiteProjection import (
            STSatelliteOnSiteProjection,
        )

        sp3file = "/home/tleduc/sDrive_cnrs/crenau/q_ReSilientGAIA/ephemerides/COD0OPSULT_20243530000_02D_05M_ORB.SP3.gz"
        vpfile = "/home/tleduc/prj/hdr/diaporama/dev/data/berlin_segment_1_escooter_gnss_uliss.csv"

        viewpoints = STECEF2AERSatelliteReader(
            vpfile,
            lat="ref_lat",
            lon="ref_lon",
            alt="ref_alt",
            sep=",",
            decimal=".",
            iepsg="epsg:4326",
            oepsg="epsg:2154",
            timestampFieldName="timeUTC",
            tzinfo=timezone("Europe/Paris"),
        ).run()

        sp3 = STSP3GnssReader(viewpoints, "timeUTC", sp3file, freq=None).run()

        prjsat = STSatelliteOnSiteProjection(
            sp3, gid="gid", timestamp="timeUTC", proj="Stereographic", size=1
        ).run()

        dt0 = viewpoints.sample().timeUTC.squeeze()
        vp = viewpoints.query("timeUTC == @dt0").copy(deep=True)
        buff = vp.copy(deep=True)
        buff.geometry = buff.geometry.buffer(1)
        psat = prjsat.query("timeUTC == @dt0").copy(deep=True)

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))
        buff.boundary.plot(ax=ax, color="black")
        vp.plot(ax=ax, color="black", marker="P", label="Viewpoint")
        psat.plot(ax=ax, color="red", markersize=10, label="Satellite")
        psat.apply(
            lambda x: ax.annotate(
                text=x.satName,
                xy=x.geometry.coords[0][:2],
                color="black",
                size=12,
                ha="center",
            ),
            axis=1,
        )

        ax.legend()
        ax.axis("off")
        ax.set_aspect("equal")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def test2():
        from os.path import basename
        from t4gpd.commons.LatLonLib import LatLonLib
        from t4gpd.resilientgaia.STSatelliteOnSiteProjection import (
            STSatelliteOnSiteProjection,
        )

        sp3file = "/home/tleduc/sDrive_cnrs/crenau/q_ReSilientGAIA/ephemerides/COD0OPSULT_20243530000_02D_05M_ORB.SP3.gz"
        dts = STSP3GnssReader._read(sp3file, freq="5min").sat_dt.unique()

        site = LatLonLib.AVIGNON
        site = LatLonLib.LILLE
        site = LatLonLib.NANTES

        viewpoints = GeoDataFrame(columns=["timeUTC", "geometry"], crs="epsg:4326")
        viewpoints["timeUTC"] = dts
        viewpoints["geometry"] = site.loc[0, "geometry"]
        viewpoints = viewpoints.to_crs("epsg:2154")

        buff = viewpoints.head(1).copy(deep=True)
        buff.geometry = buff.geometry.buffer(1)

        sp3 = STSP3GnssReader(viewpoints, "timeUTC", sp3file).run()
        prjsat = STSatelliteOnSiteProjection(
            sp3, gid="gid", timestamp="timeUTC", proj="Stereographic", size=1
        ).run()

        # MAPPING
        dt0, dt1 = prjsat.timeUTC.min(), prjsat.timeUTC.max()

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_title(
            f"""Satellite positions from SP3 file {basename(sp3file)}
between {dt0} and {dt1}
{LatLonLib.latlon_to_str(site)}"""
        )
        buff.boundary.plot(ax=ax, color="black")
        viewpoints.head(1).plot(
            ax=ax, color="black", marker="P", markersize=110, label="Viewpoint"
        )

        duos = [("GPS", "blue"), ("GLONASS", "red"), ("Galileo", "green")]
        for constellation, color in duos:
            prjsat.query("constellation == @constellation").plot(
                ax=ax, color=color, markersize=2, label=constellation
            )

        ax.legend()
        ax.axis("off")
        ax.set_aspect("equal")
        fig.tight_layout()
        plt.savefig("sp3_satellite_positions.pdf", dpi=300, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        return prjsat


# STSP3GnssReader.test()
# STSP3GnssReader.test2()
