"""
Created on 30 jan. 2024

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
from pandas import merge
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class CartesianProductLib(object):
    """
    classdocs
    """

    @staticmethod
    def product(df1, df2):
        return merge(df1, df2, how="cross")

    @staticmethod
    def product_within_distance(gdf1, gdf2, distance):
        if not isinstance(gdf1, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf1, "GeoDataFrame")
        if not isinstance(gdf2, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf2, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(gdf1, gdf2):
            raise Exception(
                "Illegal argument: gdf1 and gdf2 are expected to share the same crs!"
            )
        result = CartesianProductLib.product(gdf1, gdf2)
        result = result.loc[
            result.apply(lambda row: row.geometry_x.distance(row.geometry_y), axis=1)
            <= distance
        ]
        result.reset_index(drop=True, inplace=True)
        return result

    @staticmethod
    def product_within_distance2(gdf1, gdf2, distance):
        # product_within_distance2(...) is more efficient for large data volumes
        if not isinstance(gdf1, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf1, "GeoDataFrame")
        if not isinstance(gdf2, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf2, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(gdf1, gdf2):
            raise Exception(
                "Illegal argument: gdf1 and gdf2 are expected to share the same crs!"
            )

        _gdf1 = gdf1.copy(deep=True)
        _gdf1["geometry_x"] = _gdf1.geometry

        _gdf2 = gdf2.copy(deep=True)
        _gdf2["geometry_y"] = _gdf2.geometry
        _gdf2.geometry = _gdf2.geometry.apply(lambda g: g.buffer(distance))
        _gdf1 = overlay(_gdf1, _gdf2, how="intersection", keep_geom_type=True)

        args = {}
        for fieldname in gdf1.columns:
            if fieldname in gdf2.columns:
                args.update(
                    {
                        f"{fieldname}_1": f"{fieldname}_x",
                        f"{fieldname}_2": f"{fieldname}_y",
                    }
                )

        _gdf1.rename(columns=args, inplace=True)
        _gdf1.drop(columns="geometry", inplace=True)
        return _gdf1

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.morph.STGrid import STGrid
        from shapely import box

        gdf = GeoDataFrame([{"geometry": box(0, 0, 100, 100)}])
        gdf1 = STGrid(
            gdf,
            dx=50,
            dy=None,
            indoor=None,
            intoPoint=True,
            encode=True,
            withDist=False,
        ).run()
        gdf2 = STGrid(
            gdf, dx=2, dy=None, indoor=None, intoPoint=True, encode=True, withDist=False
        ).run()

        actual1 = CartesianProductLib.product_within_distance(gdf1, gdf2, distance=5)
        actual1.rename(columns={"geometry_y": "geometry"}, inplace=True)

        actual2 = CartesianProductLib.product_within_distance2(gdf1, gdf2, distance=5)
        actual2.rename(columns={"geometry_y": "geometry"}, inplace=True)

        """
        gdf1 = STGrid(..., dx=5, ...)

        %timeit actual1 = CartesianProductLib.product_within_distance(gdf1, gdf2, distance=5)
        7.44 s ± 80.2 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

        %timeit actual2 = CartesianProductLib.product_within_distance2(gdf1, gdf2, distance=5)
        117 ms ± 374 μs per loop (mean ± std. dev. of 7 runs, 10 loops each)
        """

        assert actual1.equals(actual2), "BIG BUG"

        fig, axes = plt.subplots(ncols=2, figsize=(1.9 * 8.26, 1 * 8.26), squeeze=False)

        ax = axes[0, 0]
        ax.set_title("product_within_distance(...)")
        gdf1.plot(ax=ax, marker="o", color="red")
        gdf2.plot(ax=ax, marker=".", color="lightgrey")
        actual1.plot(ax=ax, marker="+", color="green")

        ax = axes[0, 1]

        ax.set_title("product_within_distance2(...)")
        gdf1.plot(ax=ax, marker="o", color="red")
        gdf2.plot(ax=ax, marker=".", color="lightgrey")
        actual2.plot(ax=ax, marker="+", color="green")

        fig.tight_layout()
        plt.show()
        plt.close(fig)


# CartesianProductLib.test()
