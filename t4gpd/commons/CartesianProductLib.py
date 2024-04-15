'''
Created on 30 jan. 2024

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
from geopandas import GeoDataFrame, overlay
from numpy.random import default_rng
from pandas import DataFrame, merge
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class CartesianProductLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def product(df1, df2):
        if not isinstance(df1, DataFrame):
            raise IllegalArgumentTypeException(df1, "DataFrame")
        if not isinstance(df2, DataFrame):
            raise IllegalArgumentTypeException(df2, "DataFrame")

        _df1, _df2 = df1.copy(deep=True), df2.copy(deep=True)
        rng = default_rng()

        while True:
            fieldname = str(rng.integers(low=0, high=1e12, size=1)[0])
            if (not (fieldname in df1) and not (fieldname in df2)):
                _df1[fieldname] = 0
                _df2[fieldname] = 0
                result = merge(_df1, _df2, on=fieldname)
                result.drop(columns=[fieldname], inplace=True)
                return result

    @staticmethod
    def product_within_distance(gdf1, gdf2, distance):
        if not isinstance(gdf1, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf1, "GeoDataFrame")
        if not isinstance(gdf2, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf2, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(gdf1, gdf2):
            raise Exception(
                "Illegal argument: gdf1 and gdf2 must share shames CRS!")
        result = CartesianProductLib.product(gdf1, gdf2)
        result = result.loc[result.apply(
            lambda row: row.geometry_x.distance(row.geometry_y), axis=1) <= distance]
        result.reset_index(drop=True, inplace=True)
        return result

    @staticmethod
    def product_within_distance2(gdf1, gdf2, distance):
        if not isinstance(gdf1, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf1, "GeoDataFrame")
        if not isinstance(gdf2, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf2, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(gdf1, gdf2):
            raise Exception(
                "Illegal argument: gdf1 and gdf2 must share shames CRS!")

        _gdf1 = gdf1.copy(deep=True)
        _gdf1["geometry_x"] = _gdf1.geometry

        _gdf2 = gdf2.copy(deep=True)
        _gdf2["geometry_y"] = _gdf2.geometry
        _gdf2.geometry = _gdf2.geometry.apply(lambda g: g.buffer(distance))
        _gdf1 = overlay(_gdf1, _gdf2, how="intersection", keep_geom_type=True)

        args = {}
        for fieldname in gdf1.columns:
            if (fieldname in gdf2.columns):
                args.update({f"{fieldname}_1": f"{fieldname}_x",
                             f"{fieldname}_2": f"{fieldname}_y"})

        _gdf1.rename(columns=args, inplace=True)
        _gdf1.drop(columns="geometry", inplace=True)
        return _gdf1


"""
from t4gpd.morph.STGrid import STGrid
from shapely import box

gdf = GeoDataFrame([{"geometry": box(0, 0, 100, 100)}])
gdf1 = STGrid(gdf, dx=50, dy=None, indoor=None, intoPoint=True,
              encode=True, withDist=False).run()
gdf2 = STGrid(gdf, dx=2, dy=None, indoor=None, intoPoint=True,
              encode=True, withDist=False).run()
actual = CartesianProductLib.product_within_distance(gdf1, gdf2, distance=5)
# actual.rename(columns={"geometry_y": "geometry"}, inplace=True)

actual2 = CartesianProductLib.product_within_distance2(gdf1, gdf2, distance=5)
# actual2.rename(columns={"geometry_y": "geometry"}, inplace=True)

actual.to_csv("/tmp/1.csv", index=False, sep=";")
actual2.to_csv("/tmp/2.csv", index=False, sep=";")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(1*8.26, 1*8.26))
gdf1.plot(ax=ax, marker="v")
gdf2.plot(ax=ax, marker="+")
actual.plot(ax=ax, marker=".")
plt.show()
plt.close(fig)

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(1*8.26, 1*8.26))
gdf1.plot(ax=ax, marker="v")
gdf2.plot(ax=ax, marker="+")
actual2.plot(ax=ax, marker=".")
plt.show()
plt.close(fig)
"""

"""
a = DataFrame(["a%d" % i for i in range(1, 4)], columns=["chpA"])
b = DataFrame(["b%d" % i for i in range(1, 3)], columns=["chpB"])
c = CartesianProductLib.product(a, b)
print(f"{a}\n{b}\n\n{c}")
"""
