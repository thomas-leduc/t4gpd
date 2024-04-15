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
from shapely import MultiLineString, Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STRoadNeighborhood import STRoadNeighborhood


class STRoadNeighborhoodTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.simpleUrbanGraph(choice=4)
        self.fromPointsAndMaxDists = GeoDataFrame([
            {"geometry": Point((2, 2)), "maxDist": 2.5},
            {"geometry": Point((3, 6)), "maxDist": 4.0},
        ], crs=self.roads.crs)

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.fromPointsAndMaxDists.plot(ax=ax, color="red", marker="o")
        self.roads.plot(ax=ax, color="lightgrey", linewidth=3.2)
        result.plot(ax=ax, column="gid", linewidth=1.2)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STRoadNeighborhood(
            self.roads, self.fromPointsAndMaxDists, "maxDist").run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(2, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")
        for gid, row in result.iterrows():
            self.assertEqual(gid, row["gid"], "Test attribute value (1)")
            self.assertEqual(
                self.fromPointsAndMaxDists.geometry[gid].wkt,
                row["fromPoint"], "Test attribute value (2)")
            self.assertIsInstance(
                row["geometry"], MultiLineString, "Test geometry type")
            if (0 == gid):
                self.assertAlmostEqual(13, row.geometry.length, None,
                                       "Test attribute value (3)", 1e-6)
            elif (1 == gid):
                self.assertEqual(7, row.geometry.length,
                                 "Test attribute value (3)")
        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
