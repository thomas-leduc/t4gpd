'''
Created on 24 sep. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
'''
from datetime import datetime
from numpy import isnan
from pandas import DataFrame, concat
from pymap3d.aer import ecef2aer
from pytz import timezone
from shapely import Point
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.io.CSVReader import CSVReader
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class STECEF2AERSatelliteReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, ifile, lat="lat", lon="lon", alt="alt", sep=",", decimal=".",
                 iepsg="epsg:4326", oepsg="epsg:2154", timestampFieldName=None,
                 tzinfo=timezone("Europe/Paris")):
        '''
        Constructor
        '''
        self.sensors = CSVReader(ifile, xFieldName=lon, yFieldName=lat,
                                 fieldSep=sep, srcEpsgCode=iepsg, dstEpsgCode=oepsg,
                                 decimalSep=decimal).run()
        self.lat, self.lon, self.alt = lat, lon, alt
        self.timestampFieldName = timestampFieldName
        self.tzinfo = tzinfo

    def __ecef2aer(self, row, h0, ell=SatelliteLib.WGS84):
        # ECEF: earth-centered, earth-fixed frame
        # AER: azimuth, elevation, slant range
        # ECEF -> AER
        vp, lat0, lon0 = row.geometry, row[self.lat], row[self.lon]

        nsat, rows = 0, []
        for i in range(SatelliteLib.NSAT):
            x = row[f"satcoordX_{i}"]
            y = row[f"satcoordY_{i}"]
            z = row[f"satcoordZ_{i}"]

            az, el, srange, satpos = None, None, None, Point()
            if not (isnan(x) or isnan(y) or isnan(z)):
                nsat += 1
                # https://geospace-code.github.io/pymap3d/aer.html#pymap3d.aer.ecef2aer
                az, el, srange = ecef2aer(
                    x, y, z, lat0, lon0, h0, ell=ell, deg=True)
            rows.extend([az, el, srange])

        rows.append(nsat)
        return rows

    @staticmethod
    def __get_colname(i):
        if (3 * SatelliteLib.NSAT == i):
            return "nsat"
        match i % 3:
            case 0:
                return f"sat_{i//3}_az"
            case 1:
                return f"sat_{i//3}_el"
            case 2:
                return f"sat_{i//3}_sr"
            case 3:
                return f"sat_{i//3}"

    @staticmethod
    def rename_satellites(sat):
        columns = {}
        for i in range(SatelliteLib.NSAT):
            satName = SatelliteLib.get_satellite_name(i)
            columns.update({
                f"sat_{i}_az": f"{satName}_az",
                f"sat_{i}_el": f"{satName}_el",
                f"sat_{i}_sr": f"{satName}_sr",
            })
        return sat.rename(columns=columns)

    @staticmethod
    def polarPlot(sat, gid, constellations=["GPS", "Galileo", "GLONASS"], title=None, odir=None):
        import matplotlib.pyplot as plt
        from numpy import degrees, linspace, pi, radians

        colors = {"GPS": "green", "Galileo": "blue", "GLONASS": "red"}

        df = STECEF2AERSatelliteReader.rename_satellites(sat)
        df = df.loc[df[df.gid == gid].index]
        df.dropna(axis=1, how="all", inplace=True)

        azims = df.loc[:, [c for c in df.columns if c.endswith("_az")]]
        elevs = df.loc[:, [c for c in df.columns if c.endswith("_el")]]
        labels = [c[:-3] for c in azims.columns]
        constellation = [SatelliteLib.constellation(label) for label in labels]

        azims = radians(azims.to_numpy()).reshape(-1)
        elevs = elevs.to_numpy().reshape(-1)

        df = DataFrame({"constellation": constellation, "labels": labels,
                        "azims": azims, "elevs": elevs
                        })
        groups = df.groupby(by="constellation")

        fig, ax = plt.subplots(
            figsize=(1.4 * 8.26, 2 * 8.26), subplot_kw={"projection": "polar"})
        if title is not None:
            ax.set_title(title, fontsize=24)
        # Set the offset for the location of 0 in radians
        # ax.set_theta_offset(0)
        # clockwise -1, counterclockwise 1
        ax.set_theta_direction(-1)
        # Set the location of theta's zero
        ax.set_theta_zero_location(loc="N")
        ax.set_rlim(bottom=0, top=90)
        ax.set_xticks(ticks=radians(linspace(0, 360, 12, endpoint=False)))
        ax.set_yticks(ticks=range(0, 90, 15))
        ax.invert_yaxis()
        ax.tick_params(axis="both", colors="lightgrey",
                       grid_color="lightgrey", grid_linewidth=1,
                       grid_linestyle="dotted", which="both")
        # ax.set_thetamin(45)
        # ax.set_thetamax(135)
        for constellation, _df in groups:
            if (constellations is None) or (constellation in constellations):
                ax.scatter(_df.azims, _df.elevs, color=colors[constellation],
                           label=constellation, marker="o")
                for azim, elev, label in zip(_df.azims, _df.elevs, _df.labels):
                    ax.text(azim, elev, label, color=colors[constellation])
        ax.legend()
        if odir is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(f"{odir}/polarplot_{gid}.pdf", bbox_inches="tight")
        plt.close(fig)

    """
    @staticmethod
    def polarPlotTraj(sat, constellations=["GPS", "Galileo", "GLONASS"], title=None, odir=None):
        import matplotlib.pyplot as plt
        from numpy import degrees, linspace, pi, radians

        colors = {"GPS": "green", "Galileo": "blue", "GLONASS": "red"}

        df = STECEF2AERSatelliteReader.rename_satellites(sat)
        df.dropna(axis=1, how="all", inplace=True)

        azims = df.loc[:, [c for c in df.columns if c.endswith("_az")]]
        elevs = df.loc[:, [c for c in df.columns if c.endswith("_el")]]
        # labels = [c[:-3] for c in azims.columns]
        # constellation = [SatelliteLib.constellation(label[0])
        #                  for label in labels]

        # azims = radians(azims.to_numpy()).reshape(-1)
        # elevs = elevs.to_numpy().reshape(-1)
        # return df, constellation, labels, azims, elevs
        # df = DataFrame({"constellation": constellation, "labels": labels,
        #                 "azims": azims, "elevs": elevs
        #                 })
        # groups = df.groupby(by="constellation")

        fig, ax = plt.subplots(
            figsize=(1.4 * 8.26, 2 * 8.26), subplot_kw={"projection": "polar"})
        if title is not None:
            ax.set_title(title, fontsize=24)
        # Set the offset for the location of 0 in radians
        # ax.set_theta_offset(0)
        # clockwise -1, counterclockwise 1
        ax.set_theta_direction(-1)
        # Set the location of theta's zero
        ax.set_theta_zero_location(loc="N")
        ax.set_rlim(bottom=0, top=90)
        ax.set_xticks(ticks=radians(linspace(0, 360, 12, endpoint=False)))
        ax.set_yticks(ticks=range(0, 90, 15))
        ax.invert_yaxis()
        ax.tick_params(axis="both", colors="lightgrey",
                       grid_color="lightgrey", grid_linewidth=1,
                       grid_linestyle="dotted", which="both")
        # ax.set_thetamin(45)
        # ax.set_thetamax(135)
        for i in range(SatelliteLib.NSAT):
        # for i in [7]:
            colname = f"E{i:02d}_az"
            if colname in azims:
                _azims = azims.loc[:, colname]
                _elevs = elevs.loc[:, f"E{i:02d}_el"]
                constellation = "GPS"
                constellation = "Galileo"
                ax.scatter(_azims, _elevs, color=colors[constellation],
                           label=constellation, marker="o")
                # for azim, elev, label in zip(_azims, _elevs, _labels):
                #     ax.text(azim, elev, label, color=colors[constellation])


        # for constellation, _df in groups:
        #     if (constellations is None) or (constellation in constellations):
        #         ax.scatter(_df.azims, _df.elevs, color=colors[constellation],
        #                    label=constellation, marker="o")
        #         for azim, elev, label in zip(_df.azims, _df.elevs, _df.labels):
        #             ax.text(azim, elev, label, color=colors[constellation])
        ax.legend()
        if odir is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(f"{odir}/polarplot_{gid}.png", bbox_inches="tight")
        plt.close(fig)
    """

    def run(self):
        h0 = self.sensors.loc[0, self.alt]
        df = self.sensors.apply(lambda row: self.__ecef2aer(row, h0), axis=1)
        df = df.to_frame(name="satellites")
        df = DataFrame(df.satellites.to_list(), columns=[
                       STECEF2AERSatelliteReader.__get_colname(i)
                       for i in range(1+3*SatelliteLib.NSAT)])
        df = concat([self.sensors, df], axis=1)

        if not self.timestampFieldName is None:
            df[self.timestampFieldName] = df[self.timestampFieldName].apply(
                lambda v: datetime.fromtimestamp(v, self.tzinfo))

        return df
