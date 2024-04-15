'''
Created on 31 oct 2023

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
from numpy import array
from shapely import Polygon
from shapely.wkt import loads
from t4gpd.commons.ConcaveLib import ConcaveLib


class ConcaveLibTest(unittest.TestCase):

    def setUp(self):
        self.polygon = loads(
            "POLYGON ((-3 1, -1 1, -1 3, 1 3, 1 1, 3 1, 3 -1, 1 -1, 1 -3, -1 -3, -1 -1, -3 -1, -3 1))")
        self.mls = loads(
            "MULTILINESTRING ((1.5 1.5, 3 3), (-1.5 -1.5, -3 -3))")

    def tearDown(self):
        pass

    def __plot(self, polygon, result):
        import matplotlib.pyplot as plt

        polygon = GeoDataFrame({"geometry": [polygon]})
        mls = GeoDataFrame({"geometry": [self.mls]})
        result = GeoDataFrame({"geometry": [result]})
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        polygon.boundary.plot(ax=ax, color="black", hatch=".")
        mls.plot(ax=ax, color="red")
        result.boundary.plot(ax=ax, color="blue", hatch="/")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testFillInTheConcavities1(self):
        result = ConcaveLib.fillInTheConcavities(self.polygon, self.mls)
        self.assertIsInstance(result, Polygon, "Is a Polygon")
        self.assertEqual(24, result.area, "Check Polygon area")
        # self.__plot(self.polygon, result)

    def testFillInTheConcavities2(self):
        polygon = loads(
            "POLYGON ((-1 -1, -1 1, 1 1, 1 -1, -1 -1))")
        result = ConcaveLib.fillInTheConcavities(polygon, self.mls)
        self.assertIsInstance(result, Polygon, "Is a Polygon")
        self.assertEqual(4, result.area, "Check Polygon area")
        # self.__plot(polygon, result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
