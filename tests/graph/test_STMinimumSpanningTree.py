'''
Created on 26 oct. 2023

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
from shapely import LineString
from t4gpd.commons.LineStringCuttingLib import LineStringCuttingLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STMinimumSpanningTree import STMinimumSpanningTree


class STMinimumSpanningTreeTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.simpleUrbanGraph()

    def tearDown(self):
        self.roads = None

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.roads.plot(ax=ax, color="lightgrey", linewidth=8)
        # self.roads.plot(ax=ax, column="gid", linewidth=8, legend=True)
        result = LineStringCuttingLib.lineStringShortener(
            result, start_dist=0.05, end_dist=0.95, normalized=True)
        result.plot(ax=ax, color="red", linestyle="dashed", linewidth=1)
        result.apply(lambda x: ax.annotate(
            text=f"{x['from']} -> {x.to}", xy=x.geometry.interpolate(
                0.5, normalized=True).coords[0],
            color="black", size=16, ha="center", va="center"), axis=1)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = STMinimumSpanningTree(self.roads).run()
        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(15, len(result), "Count rows")
        self.assertEqual(4, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString,
                                  "Is a GeoDataFrame of LineStrings")
            self.assertEqual(row.geometry.length, row.weight,
                             "Check 'weight' attr. values")
            self.assertIn(row["from"], range(16), "Check 'from' attr. values")
            self.assertIn(row["to"], range(16), "Check 'to' attr. values")

        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
