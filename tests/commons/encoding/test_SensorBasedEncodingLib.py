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
from numpy import arctan, round
from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
from t4gpd.commons.encoding.IsovistBuilder import IsovistBuilder
from t4gpd.commons.encoding.SensorBasedEncodingLib import SensorBasedEncodingLib
from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
from t4gpd.commons.grid.FastGridLib import FastGridLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class SensorBasedEncodingLibTest(unittest.TestCase):
    def setUp(self):
        dx = 100
        self.rayLength, self.nRays = 45, 64

        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.sensors = FastGridLib.grid(
            self.buildings, dx, intoPoint=True, withRowsCols=False
        )
        self.sensors = PointsInPolygonsLib.outdoors(self.sensors, self.buildings)

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

    def testEncode2D_1(self):
        actual = SensorBasedEncodingLib.encode2D(
            self.sensors, self.buildings, self.rayLength, self.nRays
        )

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.sensors), len(actual), "Count rows")
        self.assertEqual(
            len(self.sensors.columns) + 1, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            self.assertEqual(
                self.nRays, len(row.raylen2D), "Check raylen2D columns (1)"
            )
            self.assertTrue(
                self.rayLength >= max(row.raylen2D) >= 0, "Check raylen2D columns (2)"
            )

        isov = IsovistBuilder.build(actual, "raylen2D", copy=True)
        # self.__plot(isov)

    def testEncode2D_2(self):
        self.sensors["raylen"] = [10, 20, 25, 35, 45]
        actual = SensorBasedEncodingLib.encode2D(
            self.sensors, self.buildings, "raylen", self.nRays
        )

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.sensors), len(actual), "Count rows")
        self.assertEqual(
            len(self.sensors.columns) + 1, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            self.assertEqual(
                self.nRays, len(row.raylen2D), "Check raylen2D columns (1)"
            )
            self.assertTrue(
                self.sensors.raylen.max() >= max(row.raylen2D) >= 0,
                "Check raylen2D columns (2)",
            )

        isov = IsovistBuilder.build(actual, "raylen2D", copy=True)
        # self.__plot(isov)

    def testEncode25D_1(self):
        actual = SensorBasedEncodingLib.encode25D(
            self.sensors,
            self.buildings,
            elevationFieldname="HAUTEUR",
            h0=0,
            rayLength=self.rayLength,
            nRays=self.nRays,
        )

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.sensors), len(actual), "Count rows")
        self.assertEqual(
            len(self.sensors.columns) + 4, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            self.assertEqual(
                self.nRays, len(row.raylen25D), "Check raylen25D columns (1)"
            )
            self.assertTrue(
                self.rayLength >= max(row.raylen25D) >= 0, "Check raylen25D columns (2)"
            )
            self.assertListEqual(
                row.h_over_w,
                [h / w for h, w in zip(row.HAUTEUR, row.raylen25D)],
                "Check h_over_w columns",
            )
            ndecimals = 9
            self.assertListEqual(
                round(arctan(row.h_over_w), ndecimals).tolist(),
                round(row.angles, ndecimals).tolist(),
                "Check angles columns",
            )

        smap = SkymapBuilder.build(
            actual, "angles", proj="Stereographic", size=10, epsilon=0.1, copy=True
        )
        # self.__plot(smap)

    def testEncode25D_2(self):
        self.sensors["raylen"] = [10, 20, 25, 35, 45]
        actual = SensorBasedEncodingLib.encode25D(
            self.sensors,
            self.buildings,
            elevationFieldname="HAUTEUR",
            h0=0,
            rayLength="raylen",
            nRays=self.nRays,
        )

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.sensors), len(actual), "Count rows")
        self.assertEqual(
            len(self.sensors.columns) + 4, len(actual.columns), "Count columns"
        )
        for _, row in actual.iterrows():
            self.assertEqual(
                self.nRays, len(row.raylen25D), "Check raylen25D columns (1)"
            )
            self.assertTrue(
                self.sensors.raylen.max() >= max(row.raylen25D) >= 0,
                "Check raylen25D columns (2)",
            )
            self.assertListEqual(
                row.h_over_w,
                [h / w for h, w in zip(row.HAUTEUR, row.raylen25D)],
                "Check h_over_w columns",
            )
            ndecimals = 9
            self.assertListEqual(
                round(arctan(row.h_over_w), ndecimals).tolist(),
                round(row.angles, ndecimals).tolist(),
                "Check angles columns",
            )

        smap = SkymapBuilder.build(
            actual, "angles", proj="Stereographic", size=10, epsilon=0.1, copy=True
        )
        # self.__plot(smap)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
