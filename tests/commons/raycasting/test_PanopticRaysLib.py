'''
Created on 10 nov 2023

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
from shapely.geometry import LineString, Point
from t4gpd.commons.raycasting.PanopticRaysLib import PanopticRaysLib


class PanopticRaysLibTest(unittest.TestCase):

    def setUp(self):
        self.nRays, self.rayLength = 8, 100
        self.sensors = GeoDataFrame([
            {"gid": 1, "geometry": Point([0, 0])},
            {"gid": 200, "geometry": Point([200, 200])},
        ])

    def tearDown(self):
        pass

    def __plot(self, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.sensors.plot(ax=ax, color="red", marker="o")
        # result.plot(ax=ax, color="black", linestyle="dotted", linewidth=0.5)
        result.plot(ax=ax, column="__RAY_ID__",
                    linestyle="solid", linewidth=0.5)
        plt.show()
        plt.close(fig)

    def testGet2DGeoDataFrame(self):
        result = PanopticRaysLib.get2DGeoDataFrame(
            self.sensors, self.rayLength, self.nRays)

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(self.nRays * len(self.sensors),
                         len(result), "Count rows")
        self.assertEqual(len(self.sensors.columns)+3,
                         len(result.columns), "Count columns")

        self.assertTrue(all(result.geometry.apply(lambda g: isinstance(
            g, LineString))), "Is a GeoDataFrame of LineString")
        self.assertFalse(all(result.geometry.apply(
            lambda g: g.has_z)), "Is a GeoDataFrame of 2D LineString")
        self.assertTrue(all(result.geometry.apply(
            lambda g: abs(self.rayLength - g.length) < 1e-6)), "Is a GeoDataFrame of LineString of same lengths")

        self.assertTrue(all(result.dissolve(
            by="__VPT_ID__", aggfunc={"__RAY_ID__": "count"}).__RAY_ID__.apply(lambda v: self.nRays == v)),
            "Is a GeoDataFrame of same nb of LineStrings")

        # self.__plot(result)

    def testGet25DGeoDataFrame(self):
        result = PanopticRaysLib.get25DGeoDataFrame(
            self.sensors, self.rayLength, self.nRays)

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(self.nRays * len(self.sensors),
                         len(result), "Count rows")
        self.assertEqual(len(self.sensors.columns)+3,
                         len(result.columns), "Count columns")

        self.assertTrue(all(result.geometry.apply(lambda g: isinstance(
            g, LineString))), "Is a GeoDataFrame of LineString")
        self.assertTrue(all(result.geometry.apply(
            lambda g: g.has_z)), "Is a GeoDataFrame of 2.5D LineString")

        # self.__plot(result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
