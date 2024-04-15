'''
Created on 17 juin 2020

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
from numpy import sqrt
from shapely import LineString
from t4gpd.commons.LineStringCuttingLib import LineStringCuttingLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STToRoadsSections import STToRoadsSections


class STToRoadsSectionsTest(unittest.TestCase):

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
            text=x.gid, xy=x.geometry.interpolate(
                0.5, normalized=True).coords[0],
            color="black", size=16, ha="center", va="center"), axis=1)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRunWithCulDeSac(self):
        result = STToRoadsSections(self.roads, withoutCulDeSac=False).run()
        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(11, len(result), "Count rows")
        self.assertEqual(3, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString,
                                  "Is a GeoDataFrame of LineStrings")
            self.assertTrue(1 <= row["distance"] <= 15 + sqrt(2),
                            "distance attribute values")
        # self.__plot(result)

    def testRunWithoutCulDeSac(self):
        result = STToRoadsSections(self.roads, withoutCulDeSac=True).run()
        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(10, len(result), "Count rows")
        self.assertEqual(3, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString,
                                  "Is a GeoDataFrame of LineStrings")
            self.assertTrue(1 <= row["distance"] < 15 + sqrt(2),
                            "distance attribute values")
        # self.__plot(result)
        # result.to_file("/tmp/xxx.shp")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
