"""
Created on 20 Oct. 2025

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
from numpy import pi
from shapely import Polygon
from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
from t4gpd.commons.encoding.IsovistBuilder import IsovistBuilder
from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
from t4gpd.commons.grid.FastGridLib import FastGridLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class IsovistBuilderTest(unittest.TestCase):
    def setUp(self):
        dx = 100
        self.rayLength, self.nRays = 45, 64

        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.sensors = FastGridLib.grid(
            self.buildings, dx, intoPoint=True, withRowsCols=False
        )
        self.sensors = PointsInPolygonsLib.outdoors(self.sensors, self.buildings)

        self.urbenc = SensorBasedEncodingLib.encode2D(
            self.sensors, self.buildings, self.rayLength, self.nRays
        )

    def tearDown(self):
        pass

    def __plot(self, isov):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=ax, color="grey")
        self.sensors.plot(ax=ax, color="red", marker="P")
        isov.plot(ax=ax, alpha=0.3, color="yellow", edgecolor="orange", linewidth=0.5)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    def testBuild(self):
        actual = IsovistBuilder.build(self.urbenc, "raylen2D", copy=True)

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.urbenc), len(actual), "Count rows")
        self.assertEqual(len(self.urbenc.columns), len(actual.columns), "Count columns")

        areaMax = pi * self.rayLength ** 2
        for _, row in actual.iterrows():
            self.assertIsInstance(
                row.geometry, Polygon, "Is a GeoDataFrame of Polygons"
            )
            self.assertTrue(areaMax >= row.geometry.area >= 0, "Check isovist area")

        # self.__plot(actual)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
