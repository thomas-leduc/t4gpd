"""
Created on 31 mars 2021

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
from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
from t4gpd.commons.grid.FastGridLib import FastGridLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class PointsInPolygonsLibTest(unittest.TestCase):
    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.points = FastGridLib.grid(
            self.buildings, dx=10, intoPoint=True, withRowsCols=False
        )

    def tearDown(self):
        pass

    def __plot(self, buildings, grid, title=None):
        import matplotlib.pyplot as plt
        from shapely.geometry import box

        bbox = GeoDataFrame([{"geometry": box(*buildings.total_bounds)}])
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        if title is not None:
            ax.set_title(title, fontsize=20)
        buildings.plot(ax=ax, color="lightgrey")
        bbox.boundary.plot(ax=ax, color="red", linewidth=0.2)

        if "indoor" in grid.columns:
            grid.plot(ax=ax, column="indoor", marker="P", legend=True)
        else:
            grid.plot(ax=ax, color="blue", marker="P")

        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testIn_or_outdoors1(self):
        actual = PointsInPolygonsLib.in_or_outdoors(
            self.points, self.buildings, deepCopy=False
        )

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.points), len(actual), "Count rows")
        self.assertEqual(len(self.points.columns), len(actual.columns), "Count columns")
        # self.__plot(self.buildings, actual, title="testIn_or_outdoors1")

    def testIn_or_outdoors2(self):
        actual = PointsInPolygonsLib.in_or_outdoors(
            self.points, self.buildings, deepCopy=True
        )

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.points), len(actual), "Count rows")
        self.assertEqual(
            len(self.points.columns) + 1, len(actual.columns), "Count columns"
        )
        self.assertTrue(
            actual.drop(columns="indoor").equals(self.points), "Check other columns"
        )
        # self.__plot(self.buildings, actual, title="testIn_or_outdoors2")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
