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

from geopandas import GeoDataFrame
from pandas import Series
from shapely import STRtree
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PointsInPolygonsLib(object):
    """
    classdocs
    """

    @staticmethod
    def __commons(points, polygons):
        if not isinstance(points, GeoDataFrame):
            raise IllegalArgumentTypeException(points, "GeoDataFrame")
        if not isinstance(polygons, GeoDataFrame):
            raise IllegalArgumentTypeException(polygons, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(points, polygons):
            raise Exception(
                "Illegal argument: gdf1 and gdf2 are expected to share the same crs!"
            )

        polys = polygons.geometry.values
        tree = STRtree(polygons.geometry.values)

        # Creating a Boolean mask: True if the point is contained within a polygon
        mask_inside = [
            any(polys[poly_idx].contains(pt) for poly_idx in tree.query(pt))
            for pt in points.geometry
        ]
        # Robust against non-trivial indices
        return Series(mask_inside, index=points.index)
        # return mask_inside

    @staticmethod
    def indoors(points, polygons):
        mask_inside = PointsInPolygonsLib.__commons(points, polygons)
        points_outside = points.loc[mask_inside]
        return points_outside

    @staticmethod
    def in_or_outdoors(points, polygons, deepCopy=False):
        mask_inside = PointsInPolygonsLib.__commons(points, polygons)
        _points = points.copy(deep=True) if deepCopy else points
        _points["indoor"] = False
        _points.loc[mask_inside, "indoor"] = True
        return _points

    @staticmethod
    def outdoors(points, polygons):
        mask_inside = PointsInPolygonsLib.__commons(points, polygons)
        points_outside = points.loc[~mask_inside]
        return points_outside

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox

        # buildings = GeoDataFrameDemos.singleBuildingInNantes()
        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        bbox = STBBox(buildings, 0).run()

        grid1 = FastGridLib.grid(buildings, dx=10, intoPoint=False, withRowsCols=True)
        grid2 = PointsInPolygonsLib.outdoors(grid1, buildings)
        grid3 = PointsInPolygonsLib.indoors(grid1, buildings)
        grid4 = PointsInPolygonsLib.in_or_outdoors(grid1, buildings, deepCopy=True)

        assert len(grid1) == len(grid2) + len(grid3)
        assert len(grid1) == len(grid4)

        # MAPPING
        fig, axes = plt.subplots(ncols=2, figsize=(14, 7), squeeze=False)

        ax = axes[0, 0]
        bbox.boundary.plot(ax=ax, color="black", linewidth=0.1)
        buildings.boundary.plot(ax=ax, color="grey")
        # grid1.plot(ax=ax, color="red", marker="P")
        grid2.plot(ax=ax, color="green", marker="P")
        grid3.plot(ax=ax, color="blue", marker="P")
        ax.axis("off")

        # -----
        ax = axes[0, 1]
        bbox.boundary.plot(ax=ax, color="black", linewidth=0.1)
        buildings.boundary.plot(ax=ax, color="grey")
        grid4.plot(ax=ax, column="indoor", marker="P", legend=True)
        ax.axis("off")

        # grid1.apply(
        #     lambda x: ax.annotate(
        #         text=f"{x.gid}\n({x.row},{x.column})",
        #         xy=x.geometry.bounds[:2],
        #         color="black",
        #         size=12,
        #         ha="left",
        #     ),
        #     axis=1,
        # )
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# PointsInPolygonsLib.test()
