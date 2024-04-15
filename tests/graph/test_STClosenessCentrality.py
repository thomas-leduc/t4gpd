'''
Created on 26 oct 2023

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
from shapely import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STClosenessCentrality import STClosenessCentrality


class STClosenessCentralityTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.simpleUrbanGraph()

    def tearDown(self):
        self.roads = None

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        result.plot(ax=ax, color="red", marker="o", markersize=100)
        result.apply(lambda x: ax.annotate(
            text=f"{x.gid} ({x.valency})\n{x.closeness:.3f}", xy=x.geometry.coords[0], color="black",
            size=16, ha="right", va="top"), axis=1)
        self.roads.plot(ax=ax, color="lightgrey", linewidth=3)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STClosenessCentrality(self.roads).run()
        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(16, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point,
                                  "Is a GeoDataFrame of Point")
            self.assertIn(row["valency"], [1, 2, 3, 6],
                          "Test valency attribute values")
            self.assertTrue(0 <= row["closeness"] <= 1,
                            "closeness attribute values")
        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
