'''
Created on 5 feb 2024

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
import unittest
from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely import box
from t4gpd.commons.CartesianProductLib import CartesianProductLib
from t4gpd.morph.STGrid import STGrid


class CartesianProductLibTest(unittest.TestCase):

    def setUp(self):
        gdf = GeoDataFrame([{"geometry": box(0, 0, 100, 100)}])
        self.gdf1 = STGrid(gdf, dx=50, dy=None, indoor=None, intoPoint=True,
                           encode=True, withDist=False).run()
        self.gdf2 = STGrid(gdf, dx=2, dy=None, indoor=None, intoPoint=True,
                           encode=True, withDist=False).run()

    def tearDown(self):
        pass

    def __plot(self, actual):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1*8.26, 1*8.26))
        self.gdf1.plot(ax=ax, marker="v")
        self.gdf2.plot(ax=ax, marker="+")
        actual.plot(ax=ax, marker=".")
        plt.show()
        plt.close(fig)

    def testProduct(self):
        df1 = DataFrame([f"a{i}" for i in range(1, 4)], columns=["chpA"])
        df2 = DataFrame([(f"b{i}", i)
                        for i in range(1, 3)], columns=["chpA", "chpB"])
        actual = CartesianProductLib.product(df1, df2)

        expected = DataFrame([
            ["a1", "b1", 1],
            ["a1", "b2", 2],
            ["a2", "b1", 1],
            ["a2", "b2", 2],
            ["a3", "b1", 1],
            ["a3", "b2", 2],
        ], columns=["chpA_x", "chpA_y", "chpB"])

        self.assertIsInstance(actual, DataFrame, "Is a DataFrame")
        self.assertEqual(6, len(actual), "Count rows")
        self.assertEqual(3, len(actual.columns), "Count columns")
        self.assertTrue(actual.equals(expected), "Test DataFrame content")

    def testProduct_within_distance(self):
        actual = CartesianProductLib.product_within_distance(
            self.gdf1, self.gdf2, distance=5)

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(84, len(actual), "Count rows")
        self.assertEqual(12, len(actual.columns), "Count columns")

        # actual.rename(columns={"geometry_y": "geometry"}, inplace=True)
        # self.__plot(actual)

    def testProduct_within_distance2(self):
        actual2 = CartesianProductLib.product_within_distance2(
            self.gdf1, self.gdf2, distance=5)

        self.assertIsInstance(actual2, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(84, len(actual2), "Count rows")
        self.assertEqual(12, len(actual2.columns), "Count columns")

        actual = CartesianProductLib.product_within_distance(
            self.gdf1, self.gdf2, distance=5)
        self.assertTrue(actual.equals(actual2), "Test GeoDataFrames equality")

        # actual2.rename(columns={"geometry_y": "geometry"}, inplace=True)
        # self.__plot(actual2)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
