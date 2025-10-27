"""
Created on 15 Oct. 2025

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

from geopandas import GeoDataFrame, overlay
from numpy import unique
from pandas import DataFrame, concat
from shapely import STRtree, intersection
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class OverlayLib(object):
    """
    classdocs
    """

    @staticmethod
    def __commons(gdf1, gdf2):
        if not isinstance(gdf1, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf1, "GeoDataFrame")
        if not isinstance(gdf2, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf2, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(gdf1, gdf2):
            raise Exception(
                "Illegal argument: gdf1 and gdf2 are expected to share the same crs!"
            )

    @staticmethod
    def intersection1(gdf1, gdf2, keep_geom_type=None, make_valid=True):
        OverlayLib.__commons(gdf1, gdf2)

        # --- Step 1: Spatial pre-filtering via STRtree
        tree = STRtree(gdf2.geometry.values)
        idx1, idx2 = tree.query(gdf1.geometry.values, predicate="intersects")

        # ---  Step 2: Unique subsets
        sub1 = gdf1.iloc[unique(idx1)]
        sub2 = gdf2.iloc[unique(idx2)]

        # --- Step 3: Geospatial overlay
        return overlay(
            sub1,
            sub2,
            how="intersection",
            keep_geom_type=keep_geom_type,
            make_valid=make_valid,
        )

    @staticmethod
    def intersection2(gdf1, gdf2):
        OverlayLib.__commons(gdf1, gdf2)

        # --- Step 1: Spatial pre-filtering via STRtree
        tree = STRtree(gdf2.geometry.values)
        idx1, idx2 = tree.query(gdf1.geometry.values, predicate="intersects")

        # ---  Step 2: Element-by-element vectorized intersection
        inter_geoms = intersection(
            gdf1.geometry.values[idx1], gdf2.geometry.values[idx2]
        )

        # --- Step 3: Concatenation
        return GeoDataFrame(
            concat(
                [
                    gdf1.iloc[idx1].drop(columns=["geometry"]).reset_index(drop=True),
                    gdf2.iloc[idx2].drop(columns=["geometry"]).reset_index(drop=True),
                    DataFrame({"geometry": inter_geoms}),
                ],
                axis=1,
            ),
            geometry="geometry",
            crs=gdf1.crs,
        )

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.commons.raycasting.PanopticRaysLib import PanopticRaysLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.demos.NantesBDT import NantesBDT

        dx, rayLength, nRays = 100, 45, 16

        buildings = NantesBDT.buildings()
        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        buildings = buildings.loc[:, ["geometry", "HAUTEUR"]]

        sensors = FastGridLib.grid(buildings, dx, intoPoint=True, withRowsCols=False)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)

        irays = PanopticRaysLib.get2DGeoDataFrame(sensors, rayLength, nRays)

        # Overlay: Intersection
        ref = overlay(buildings, irays, how="intersection", keep_geom_type=False)
        orays1 = OverlayLib.intersection1(buildings, irays, keep_geom_type=False)
        orays2 = OverlayLib.intersection2(buildings, irays)
        assert ref.equals(orays1)
        assert DataFrameLib.equals(ref, orays2)

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))

        ax.set_title("Overlay: Intersection", fontsize=28)
        buildings.plot(ax=ax, color="lightgrey")
        sensors.plot(ax=ax, color="black", marker="P")
        irays.plot(ax=ax, color="red", linewidth=0.25)
        orays1.plot(ax=ax, color="blue", linewidth=2.5)
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)


# OverlayLib.test()
