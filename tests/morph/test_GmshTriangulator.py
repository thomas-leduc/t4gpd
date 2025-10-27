"""
Created on 17 juin 2020

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
import unittest

from geopandas import GeoDataFrame
from shapely import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.GmshTriangulator import GmshTriangulator


class GmshTriangulatorTest(unittest.TestCase):
    def setUp(self):
        self.buildings = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        self.buildings = None

    def __plot(self, result):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=ax, color="lightgrey")
        result.boundary.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testRun(self):
        result = GmshTriangulator(self.buildings, characteristicLength=10.0).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(595, len(result), "Count rows")
        self.assertEqual(2, len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Is a GeoDataFrame of Polygons"
            )
            self.assertEqual(
                0, len(row.geometry.interiors), "Is a GeoDataFrame of no-hole polygons"
            )
            self.assertEqual(
                4, len(row.geometry.exterior.coords), "Is a GeoDataFrame of triangles"
            )

        self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
