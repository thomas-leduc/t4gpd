"""
Created on 14 Apr. 2025

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

from geopandas import GeoDataFrame
from numpy import deg2rad
from pandas import Timestamp, concat, merge
from shapely import LinearRing, Point
from shapely.affinity import translate
from shapely.geometry import LineString
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.TimestampLib import TimestampLib
from t4gpd.commons.proj.AEProjectionLib import AEProjectionLib
from t4gpd.commons.sun.SunModel import SunModel


class STSunMap(GeoProcess):
    """
    classdocs
    """

    def __init__(
        self,
        sensors,
        dts,
        size=4.0,
        projectionName="Stereographic",
        model="pvlib",
    ):
        """
        Constructor
        """
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        self.sensors = sensors
        self.size = size
        self.proj = AEProjectionLib.projection_switch(projectionName)
        self.sunModel = SunModel(gdf=sensors, altitude=0, model=model)

        self.immutable = GeoDataFrame(
            concat(
                [
                    self.__framework(),
                    self.__analemma(hours=range(6, 19, 2)),
                    self.__parallels(months=[3, 6, 12]),
                    self.__other(dts),
                ]
            ),
            crs=sensors.crs,
        )
        self.immutable["__projection_name__"] = projectionName

    def __commons(self, dts):
        origin = Point(0, 0)
        sunpos = self.sunModel.positions(dts)
        sunpos.drop(index=sunpos[sunpos.apparent_elevation <= 0].index, inplace=True)
        sunpos["azimuth_rad"] = deg2rad(
            AngleLib.eastCCW2northCW(sunpos["azimuth"], degree=True)
        )
        sunpos["apparent_elevation_rad"] = deg2rad(sunpos["apparent_elevation"])
        sunpos["geometry"] = sunpos.apply(
            lambda row: self.proj(
                origin, row.azimuth_rad, row.apparent_elevation_rad, self.size
            ),
            axis=1,
        )
        return sunpos

    def __analemma(self, hours):
        dts = [
            Timestamp(f"2025-{month}-{day} {hour}:00:00", tz="UTC")
            for hour in hours
            for month in range(1, 13)
            for day in (1, 11, 21)
            # for day in (1, 6, 11, 16, 21, 26)
        ]
        sunpos = self.__commons(dts)
        sunpos["__date__"] = sunpos.index.hour
        sunpos = sunpos.groupby(by=["__date__"]).agg(
            {"__date__": "first", "geometry": list}
        )
        sunpos["geometry"] = sunpos.geometry.apply(lambda geom: LinearRing(geom))
        sunpos["__label__"] = "analemma"
        sunpos = GeoDataFrame(sunpos, crs=self.sensors.crs)
        return sunpos

    def __framework(self):
        origin = Point(0, 0)
        east = translate(origin, xoff=-self.size)
        west = translate(origin, xoff=self.size)
        north = translate(origin, yoff=self.size)
        south = translate(origin, yoff=-self.size)

        gdf = GeoDataFrame(
            [
                {
                    "geometry": origin.buffer(self.size).exterior,
                    "__label__": "circle",
                    "__date__": None,
                },
                {
                    "geometry": LineString([east, west]),
                    "__label__": "axis",
                    "__date__": None,
                },
                {
                    "geometry": LineString([south, north]),
                    "__label__": "axis",
                    "__date__": None,
                },
            ],
            crs=self.sensors.crs,
        )
        return gdf

    def __other(self, dts):
        if dts is None:
            return GeoDataFrame(
                columns=["__label__", "__date__", "geometry"], crs=self.sensors.crs
            )
        sunpos = self.__commons(dts)
        sunpos["__date__"] = sunpos.index
        sunpos["geometry"] = sunpos.geometry.apply(lambda geom: Point(geom))
        sunpos["__label__"] = "other"
        sunpos = GeoDataFrame(sunpos, crs=self.sensors.crs)
        return sunpos

    def __parallels(self, months):
        dts = [Timestamp(f"2025-{month}-21", tz="UTC") for month in months]
        dts = TimestampLib.from_sunrise_to_sunset(self.sensors, dts, freq="15min")
        sunpos = self.__commons(dts)
        sunpos["__date__"] = sunpos.index.month
        sunpos = sunpos.groupby(by=["__date__"]).agg(
            {"__date__": "first", "geometry": list}
        )
        sunpos["geometry"] = sunpos.geometry.apply(lambda geom: LineString(geom))
        sunpos["__label__"] = "parallel"
        sunpos = GeoDataFrame(sunpos, crs=self.sensors.crs)
        return sunpos

    @staticmethod
    def plot(sensors, sunmaps=None, buildings=None, skymaps=None, roi=None):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        if not buildings is None:
            buildings.plot(ax=ax, color="darkgrey", edgecolor="dimgrey")
        if not skymaps is None:
            skymaps.plot(ax=ax, color="lightgrey")

        sensors.plot(ax=ax, marker="+")

        if not sunmaps is None:
            projectionName = sunmaps["__projection_name__"].iloc[0]
            ax.set_title(f"Sky + Sun Maps ({projectionName})", fontsize=16)

            _other = sunmaps.query("__label__ == 'other'")
            linestyle = "dashdot" if 0 < len(_other) else "solid"

            sunmaps.query("__label__ == 'circle'").plot(
                ax=ax, color="dimgrey", linewidth=0.5
            )
            sunmaps.query("__label__ == 'axis'").plot(
                ax=ax, color="dimgrey", linestyle="dashdot", linewidth=0.5
            )
            sunmaps.query("__label__ == 'analemma'").plot(
                ax=ax, color="brown", linestyle=linestyle, linewidth=0.5
            )
            for month, color in [(3, "green"), (6, "red"), (12, "blue")]:
                sunmaps.query(
                    f"(__label__ == 'parallel') and (__date__ == {month})"
                ).plot(ax=ax, color=color, linestyle=linestyle, linewidth=0.5)

            if 0 < len(_other):
                _other.plot(ax=ax, color="orange", marker="P")

        if not roi is None:
            if isinstance(roi, GeoDataFrame):
                minx, miny, maxx, maxy = roi.total_bounds
            else:
                minx, miny, maxx, maxy = roi.bounds
            ax.axis([minx, maxx, miny, maxy])

        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def run(self):
        sunmaps = merge(self.sensors, self.immutable, how="cross")
        sunmaps["geometry"] = sunmaps.apply(
            lambda row: translate(
                row.geometry_y, xoff=row.geometry_x.x, yoff=row.geometry_x.y
            ),
            axis=1,
        )
        sunmaps.drop(columns=["geometry_y"], inplace=True)
        sunmaps.rename(columns={"geometry_x": "viewpoint"}, inplace=True)
        return sunmaps

    @staticmethod
    def test():
        from pandas import date_range
        from shapely import Point, box
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        buildings.fillna({"HAUTEUR": 3.33}, inplace=True)
        sensors = GeoDataFrame(
            [
                {"gid": 1, "geometry": Point((355143.0, 6689359.4))},
                # {"gid": 2, "geometry": Point((355166.0, 6689328.0))},
            ],
            crs=buildings.crs,
        )

        # projectionName = "isoaire"
        # projectionName = "polar"
        # projectionName = "orthogonal"
        projectionName = "Stereographic"

        skymaps = STSkyMap25D(
            buildings,
            sensors,
            nRays=180,
            rayLength=100.0,
            elevationFieldname="HAUTEUR",
            h0=0,
            size=6.0,
            epsilon=0.01,
            projectionName=projectionName,
        ).run()

        dts = date_range(
            start="2025-02-15 08:00",
            end="2025-02-15 16:00",
            freq="30min",
            inclusive="both",
            tz="UTC",
        )

        sunmaps = STSunMap(
            sensors,
            dts,
            size=6.0,
            projectionName=projectionName,
            model="pvlib",
        ).run()

        STSunMap.plot(
            sensors=sensors,
            sunmaps=sunmaps,
            buildings=buildings,
            skymaps=skymaps,
            roi=box(*skymaps.total_bounds).buffer(8.0),
        )
        return sunmaps


# sunmaps = STSunMap.test()
