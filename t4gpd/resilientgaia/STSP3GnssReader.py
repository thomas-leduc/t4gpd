"""
Created on 2 jul. 2025

@author: tleduc

Copyright 2020-2026 Thomas Leduc

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

from geopandas import GeoDataFrame
from pandas import Timedelta, concat, merge_asof
from pandas.core.common import flatten
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib
from t4gpd.resilientgaia.STSP3GnssRawReader import STSP3GnssRawReader


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

        if dtFieldName not in sensors.columns:
            raise IllegalArgumentTypeException(
                dtFieldName, "dtFieldName must be a column name in sensors"
            )
        self.dtFieldName = dtFieldName
        self.sp3_files_or_dirname = sp3_files_or_dirname
        self.freq = freq  # "5min", "1h"
        self.filter = filter

    def run(self):
        sat_positions = STSP3GnssRawReader(
            self.sp3_files_or_dirname, self.freq, self.filter, format="wide"
        ).run()

        ecef = merge_asof(
            self.sensors[[self.dtFieldName, "geometry"]],
            sat_positions,
            left_on=self.dtFieldName,
            right_on="sat_dt",
            tolerance=Timedelta("5min"),
            direction="nearest",
        )
        ecef.drop(columns=["sat_dt"], inplace=True)

        aer = SatelliteLib.gdf_ecef_to_aer(ecef, h0=0)

        gdf = GeoDataFrame(concat([ecef, aer], axis=1), crs=self.sensors.crs)
        # ADD "gid" COLUMN
        gdf.insert(0, "gid", range(len(gdf)))
        # EXPLICIT ORDERING COLUMNS
        all_cols = ["gid", self.dtFieldName, "geometry"] + list(
            flatten(
                [
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
        gdf = gdf.reindex(columns=all_cols)
        return gdf

    @staticmethod
    def test(ofile=None):
        import matplotlib.pyplot as plt
        from pytz import timezone
        from t4gpd.resilientgaia.STECEF2AERSatelliteReader import (
            STECEF2AERSatelliteReader,
        )
        from t4gpd.resilientgaia.STSatelliteOnSiteProjection import (
            STSatelliteOnSiteProjection,
        )

        sp3file = "/home/tleduc/prj/anr_resilientgaia_2024-2028/cddis/2024/COD0OPSULT_20243530000_02D_05M_ORB.SP3.gz"
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
        if ofile:
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)
        return prjsat

    def test2(ofile=None):
        from os.path import basename
        from t4gpd.commons.LatLonLib import LatLonLib
        from t4gpd.resilientgaia.STSatelliteOnSiteProjection import (
            STSatelliteOnSiteProjection,
        )

        sp3file = "/home/tleduc/prj/anr_resilientgaia_2024-2028/cddis/2024/COD0OPSULT_20243530000_02D_05M_ORB.SP3.gz"
        dts = (
            STSP3GnssRawReader(sp3file, freq="5min", filter=None, format="long")
            .run()
            .sat_dt.unique()
        )

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
        if ofile:
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)
        return prjsat


# STSP3GnssReader.test(ofile="STSP3GnssReader_test_1.png")
# STSP3GnssReader.test2(ofile="STSP3GnssReader_test_2.png")
