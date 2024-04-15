'''
Created on 16 nov. 2020

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from pandas import concat
from shapely import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STShortestPath import STShortestPath


class STShortestPathTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.simpleUrbanGraph(choice=4)
        self.fromPoints = GeoDataFrame(
            [{"geometry": Point((2, -1))}], crs=self.roads.crs)
        self.toPoints = GeoDataFrame(
            [{"geometry": Point((2, 4.54))}], crs=self.roads.crs)
        self.EXPECTED_PATH_LENGTH = 10.46

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.roads.plot(ax=ax, color="grey", linewidth=4.2)
        result.plot(ax=ax, color="red", linewidth=1.2)
        self.fromPoints.plot(ax=ax, color="blue")
        self.toPoints.plot(ax=ax, color="green")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun1(self):
        result = STShortestPath(
            self.roads, self.fromPoints, self.toPoints).run()
        gid, pathLen, fromPoint, toPoint = result[[
            "gid", "pathLen", "fromPoint", "toPoint"]].squeeze()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(1, len(result), "Count rows")
        self.assertEqual(6, len(result.columns), "Count columns")
        self.assertEqual(0, gid, "Test attribute (1)")
        self.assertEqual(pathLen, result.length.squeeze(),
                         "Test path length (1)")
        self.assertEqual(
            fromPoint, self.fromPoints.geometry.squeeze().wkt, "Test attribute (2)")
        self.assertEqual(
            toPoint, self.toPoints.geometry.squeeze().wkt, "Test attribute (3)")
        self.assertEqual(self.EXPECTED_PATH_LENGTH,
                         result.geometry.length.squeeze(), "Test path length (2)")
        # self.__plot(result)

    def testRun2(self):
        result = STShortestPath(
            self.roads, self.fromPoints.geometry.squeeze(), self.toPoints).run()
        gid, pathLen, fromPoint, toPoint = result[[
            "gid", "pathLen", "fromPoint", "toPoint"]].squeeze()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(1, len(result), "Count rows")
        self.assertEqual(6, len(result.columns), "Count columns")
        self.assertEqual(0, gid, "Test attribute (1)")
        self.assertEqual(pathLen, result.length.squeeze(),
                         "Test path length (1)")
        self.assertEqual(
            fromPoint, self.fromPoints.geometry.squeeze().wkt, "Test attribute (2)")
        self.assertEqual(
            toPoint, self.toPoints.geometry.squeeze().wkt, "Test attribute (3)")
        self.assertEqual(self.EXPECTED_PATH_LENGTH,
                         result.geometry.length.squeeze(), "Test path length (2)")
        # self.__plot(result)

    def testRun3(self):
        result = STShortestPath(
            self.roads, self.fromPoints, self.toPoints.geometry.squeeze()).run()
        gid, pathLen, fromPoint, toPoint = result[[
            "gid", "pathLen", "fromPoint", "toPoint"]].squeeze()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(1, len(result), "Count rows")
        self.assertEqual(6, len(result.columns), "Count columns")
        self.assertEqual(0, gid, "Test attribute (1)")
        self.assertEqual(pathLen, result.length.squeeze(),
                         "Test path length (1)")
        self.assertEqual(
            fromPoint, self.fromPoints.geometry.squeeze().wkt, "Test attribute (2)")
        self.assertEqual(
            toPoint, self.toPoints.geometry.squeeze().wkt, "Test attribute (3)")
        self.assertEqual(self.EXPECTED_PATH_LENGTH,
                         result.geometry.length.squeeze(), "Test path length (2)")
        # self.__plot(result)

    def testRun4(self):
        result = STShortestPath(self.roads, self.fromPoints.geometry.squeeze(
        ), self.toPoints.geometry.squeeze()).run()
        gid, pathLen, fromPoint, toPoint = result[[
            "gid", "pathLen", "fromPoint", "toPoint"]].squeeze()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(1, len(result), "Count rows")
        self.assertEqual(6, len(result.columns), "Count columns")
        self.assertEqual(0, gid, "Test attribute (1)")
        self.assertEqual(pathLen, result.length.squeeze(),
                         "Test path length (1)")
        self.assertEqual(
            fromPoint, self.fromPoints.geometry.squeeze().wkt, "Test attribute (2)")
        self.assertEqual(
            toPoint, self.toPoints.geometry.squeeze().wkt, "Test attribute (3)")
        self.assertEqual(self.EXPECTED_PATH_LENGTH,
                         result.geometry.length.squeeze(), "Test path length (2)")
        # self.__plot(result)

    def testRun5(self):
        fromToPoints = concat([self.fromPoints, self.toPoints])

        result = STShortestPath(self.roads, fromToPoints, fromToPoints).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(2, len(result), "Count rows")
        self.assertEqual(6, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            if row.fromPoint == row.toPoint:
                self.assertEqual(0.0, row.pathLen, "Test path emptiness (1)")
                self.assertEqual(0.0, row.geometry.length,
                                 "Test path emptiness (2)")
            else:
                self.assertEqual(self.EXPECTED_PATH_LENGTH,
                                 row.pathLen, "Test path length (1)")
                self.assertEqual(self.EXPECTED_PATH_LENGTH,
                                 row.geometry.length, "Test path length (2)")
        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
