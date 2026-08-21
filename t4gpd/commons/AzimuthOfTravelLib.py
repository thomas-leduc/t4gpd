"""
Created on 7 Jan. 2026

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
from numpy import arctan2, array, pi, rad2deg
from shapely import STRtree
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class AzimuthOfTravelLib(object):
    """
    classdocs
    """

    @staticmethod
    def add_ccw_azimuth_of_travel(gdf, ofieldname="azimuth", degree=False):
        def __azimuth(prev, curr, succ):
            prev = curr if prev is None else prev
            succ = curr if succ is None else succ
            rdir = [succ.x - prev.x, succ.y - prev.y]
            azim = AngleLib.angleBetweenNodes([1, 0], [0, 0], rdir)
            return rad2deg(azim) if degree else azim

        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if not gdf.crs.is_projected:
            raise IllegalArgumentTypeException(
                gdf, "GeoDataFrame must have a projected CRS."
            )
        if ofieldname in gdf:
            raise Exception(f"{ofieldname} is already a GeoDataFrame field name. !")

        prev = DataFrameLib.getNewColumnName(gdf)
        gdf[prev] = gdf.geometry.shift(1)
        succ = DataFrameLib.getNewColumnName(gdf)
        gdf[succ] = gdf.geometry.shift(-1)

        gdf[ofieldname] = gdf.apply(
            lambda row: __azimuth(row[prev], row.geometry, row[succ]), axis=1
        )
        gdf.drop(columns=[prev, succ], inplace=True)
        return gdf

    @staticmethod
    def add_ccw_azimuth_of_nearest_road(
        sensors, roads, ofieldname="azimuth", degree=False
    ):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if not sensors.crs.is_projected:
            raise IllegalArgumentTypeException(
                sensors, "GeoDataFrame must have a projected CRS."
            )
        if ofieldname in sensors:
            raise Exception(f"{ofieldname} is already a sensors field name. !")
        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(sensors, roads):
            raise Exception(
                "sensors and roads must share the same CRS.",
            )

        lines = roads.geometry.explode(ignore_index=True).values
        # ── Vectorized pre-computation of orientations ──────────────────────────────
        coords_start = array([line.coords[0] for line in lines])  # (n, 2)
        coords_end = array([line.coords[-1] for line in lines])  # (n, 2)

        dx = coords_end[:, 0] - coords_start[:, 0]
        dy = coords_end[:, 1] - coords_start[:, 1]
        orientations = arctan2(dy, dx) % pi  # (n,)
        orientations = rad2deg(orientations) if degree else orientations

        # ── Spatial indexing ────────────────────────────────────────────────────────
        tree = STRtree(lines)

        # ── Vectorized pre-computation of orientations ──────────────────────────────
        idxs = tree.nearest(sensors.geometry.values)  # (m,)

        result = sensors.copy()
        result[ofieldname] = orientations[idxs]
        result["dist_to_line"] = [
            p.distance(lines[i]) for p, i in zip(sensors.geometry.values, idxs)
        ]
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STPointsDensifier import STPointsDensifier

        path = GeoDataFrameDemos.coursCambronneInNantesPath()
        gdf = STPointsDensifier(path, distance=10).run()
        # gdf = gdf.loc[:, ["gid", "node_id", "geometry"]]
        result = AzimuthOfTravelLib.add_ccw_azimuth_of_travel(gdf, degree=True)

        fig, ax = plt.subplots(figsize=(1.3 * 8.26, 8.26))
        result.plot(ax=ax, column="azimuth", legend=True)
        result.apply(
            lambda x: ax.annotate(
                text=f"{x.azimuth:.1f}°",
                xy=x.geometry.coords[0],
                color="black",
                size=12,
                ha="center",
            ),
            axis=1,
        )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return gdf

    @staticmethod
    def test2():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        roads = GeoDataFrameDemos.ensaNantesRoads()
        sensors = GeoDataFrameDemos.ensaNantesTrees()

        sensors2 = AzimuthOfTravelLib.add_ccw_azimuth_of_nearest_road(
            sensors, roads, ofieldname="azimuth", degree=True
        )

        fig, ax = plt.subplots(figsize=(1.3 * 8.26, 8.26))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="black")
        roads.plot(ax=ax, color="black", linewidth=0.5)
        sensors2.plot(
            ax=ax, column="azimuth", marker="+", markersize=50, cmap="hsv", legend=True
        )
        sensors2.apply(
            lambda x: ax.annotate(
                text=f"{x.azimuth:.1f}°",
                xy=x.geometry.coords[0],
                color="black",
                size=9,
                ha="center",
            ),
            axis=1,
        )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return sensors2


# gdf = AzimuthOfTravelLib.test()
# gdf = AzimuthOfTravelLib.test2()
