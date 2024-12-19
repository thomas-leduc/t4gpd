'''
Created on 27 sep. 2024

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
from geopandas import GeoDataFrame
from numpy import radians
from pandas import DataFrame, concat
from shapely import Point
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.proj.AEProjectionLib import AEProjectionLib
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class STSatelliteOnSiteProjection(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, sensors, gid="gid", timestamp="timeUTC",
                 proj="Stereographic", size=1):
        '''
        Constructor
        '''
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(
                sensors, "GeoDataFrame")
        self.sensors = sensors
        self.gid, self.timestamp = gid, timestamp
        self.prj = AEProjectionLib.projection_switch(proj)
        self.size = size

    def __prj_aux(self, row):
        result = []
        for i in range(SatelliteLib.NSAT):
            az, el = row[f"sat_{i}_az"], row[f"sat_{i}_el"]
            if (az is None) or (el is None):
                result.append(None)
            else:
                az = AngleLib.northCW2eastCCW(az, degree=True)
                az, el = radians(az), radians(el)
                pp = Point(self.prj(row.geometry, az, el, self.size))
                sr = row[f"sat_{i}_sr"]
                pp = GeomLib.forceZCoordinateToZ0(pp, z0=sr)
                result.append(pp)
        return result

    def __prj(self):
        left = self.sensors.loc[:, [self.gid, self.timestamp, "geometry"]]
        left.reset_index(drop=True, inplace=True)

        right = self.sensors.apply(
            lambda row: self.__prj_aux(row),
            axis=1)
        right = right.to_frame(name="satellites")
        right = DataFrame(right.satellites.to_list(), columns=[
            f"sat_{i}" for i in range(SatelliteLib.NSAT)])

        df = concat([left, right], axis=1)
        df.dropna(axis=1, how="all", inplace=True)
        return df

    @ staticmethod
    def radar(sat, gid, constellations=["GPS", "Galileo", "GLONASS"], size=1, ofile=None):
        def __label_radar(geom):
            from shapely import get_num_points
            if 2 == get_num_points(geom):
                return 1
            return 52

        def __color_satellite(satName):
            match satName[0]:
                case "R":
                    return "red"
                case "E":
                    return "blue"
                case "G":
                    return "green"
            raise Exception("Unreachable instruction!")

        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from numpy import linspace
        from shapely import LineString, get_point
        from shapely.affinity import rotate, translate
        from shapely.wkt import loads

        df = sat.loc[sat[sat.gid == gid].index]
        df.reset_index(inplace=True)

        vp = loads(df.loc[0, "viewpoint"])

        xaxis = LineString(
            [translate(vp, xoff=-size), translate(vp, xoff=size)])
        axes = GeoDataFrame([{
            "geometry": rotate(xaxis, angle=angle, origin=vp, use_radians=False),
            "label1": f"{270-angle}°",
            "label2": f"{AngleLib.northCW2eastCCW(angle, degree=True)}°"
        } for angle in range(0, 180, 30)])
        circles = GeoDataFrame([{
            "geometry": vp.buffer(size*buffdist/90).boundary,
            "label1": "",
            "label2": int(90 - buffdist)
        } for buffdist in linspace(15, 90, 6)])
        radar = concat([axes, circles])
        radar.reset_index(inplace=True)

        my_cmap = ListedColormap(["red", "green", "blue"])
        fig, ax = plt.subplots(figsize=(8.26, 8.26))
        radar.plot(ax=ax, color="grey", linestyle="dotted", linewidth=0.3)
        radar.apply(lambda x: ax.annotate(
            text=x.label1, xy=get_point(x.geometry, 0).coords[0],
            color="grey", size=10, ha="center", va="center"), axis=1)
        radar.apply(lambda x: ax.annotate(
            text=x.label2, xy=get_point(
                x.geometry, __label_radar(x.geometry)).coords[0],
            color="grey", size=10, ha="center"), axis=1)
        df.plot(ax=ax, marker="o", column="constellation", cmap=my_cmap)
        df.apply(lambda x: ax.annotate(
            text=x.satellite, xy=x.geometry.coords[0][:2],
            color=__color_satellite(x.satellite), size=12, ha="left"), axis=1)
        ax.axis("off")
        if ofile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

        return df, radar

    def run(self):
        df = self.__prj()
        df = df.melt(id_vars=[self.gid, self.timestamp, "geometry"])
        df["viewpoint"] = df.geometry.apply(lambda g: g.wkt)
        df.drop(columns=["geometry"], inplace=True)
        df.rename(columns={"variable": "satName",
                           "value": "geometry"}, inplace=True)
        df["satellite"] = df.satName.apply(
            lambda v: SatelliteLib.get_satellite_name(int(v[4:])))
        df["constellation"] = df.satellite.apply(
            lambda v: SatelliteLib.constellation(v))
        df = df.loc[df[df.geometry.apply(lambda g: g.is_valid)].index]
        df = df.set_crs(self.sensors.crs, allow_override=True)

        return df


"""
from datetime import timezone
from t4gpd.resilientgaia.STECEF2AERSatelliteReader import STECEF2AERSatelliteReader

ifile = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data/20240917_parcours_timestamp.csv"
aersat = STECEF2AERSatelliteReader(ifile, timestampFieldName="timeUTC").run()
aersat["gid"] = range(len(aersat))
aersat = aersat.set_index("timeUTC").tz_convert(timezone.utc).reset_index()
gids = [959]
aersat = aersat.loc[aersat[aersat.gid.isin(gids)].index]

# %run t4gpd/resilientgaia/STSatelliteOnSiteProjection.py
prjsat = STSatelliteOnSiteProjection(aersat, gid="gid",
                                     timestamp="timeUTC", proj="Stereographic", size=1).run()

STSatelliteOnSiteProjection.radar(prjsat, gids[0])
"""
