'''
Created on 25 july 2023

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
from numpy.random import randint
from shapely.geometry import LineString, Point
from shapely.wkt import loads
from t4gpd.commons.RayCasting4Lib import RayCasting4Lib


class RayCasting4LibTest(unittest.TestCase):

    def setUp(self):
        self.masks = GeoDataFrame([
            {"geometry": loads(
                "POLYGON ((50 80, 60 80, 60 70, 50 70, 50 80))")},
            {"geometry": loads(
                "POLYGON ((0 100, 10 100, 10 10, 90 10, 90 30, 60 30, 60 60, 70 60, 70 40, 90 40, 90 90, 80 90, 80 80, 70 80, 70 90, 30 90, 30 50, 20 50, 20 100, 100 100, 100 0, 0 0, 0 100))")},
        ])

    def tearDown(self):
        pass

    def __plot(self, label, viewPoint, rays):
        points = GeoDataFrame([{"geometry": viewPoint}])

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        ax.set_title(label, fontsize=24)
        self.masks.boundary.plot(
            ax=ax, color="lightgrey", edgecolor="grey", hatch=".")
        rays.plot(ax=ax, color="red", linewidth=1.0)
        points.plot(ax=ax, color="blue")
        plt.show()
        plt.close(fig)

    def testGet2DPanopticRaysGeoDataFrame(self):
        nRays, rayLength = 36, 100

        for viewPoint in [Point([10, 10]), Point([60, 60])]:
            sensors = GeoDataFrame([{"geometry": viewPoint}])
            rays = RayCasting4Lib.get2DPanopticRaysGeoDataFrame(
                sensors, rayLength, nRays)
            self.assertEqual(nRays, len(rays), "Test nb of rays")

    def testMultipleRayCast2D(self):
        def nonNul(ray): return (0.0 < ray.length)

        nRays, rayLength = 36, 100

        pairs = [(Point([10, 10]), 9), (Point([60, 60]), 27),
                 (Point([80, 80]), 26)]
        for viewPoint, actualNRays in pairs:

            sensors = GeoDataFrame([{"geometry": viewPoint}])
            rays = RayCasting4Lib.get2DPanopticRaysGeoDataFrame(
                sensors, rayLength, nRays)
            isovRaysField = RayCasting4Lib.multipleRayCast2D(self.masks, rays)

            self.assertEqual(actualNRays, len(list(filter(
                nonNul, isovRaysField.loc[0, "geometry"].geoms))), "Test nb of rays")
            self.assertEqual(actualNRays, len(
                isovRaysField.loc[0, "geometry"].geoms), "Test nb of rays (2)")
            self.__plot("MultipleRayCast2D", viewPoint, isovRaysField)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
