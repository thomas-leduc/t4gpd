'''
Created on 2 mai 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from t4gpd.commons.RayCasting3Lib import RayCasting3Lib


class RayCasting3LibTest(unittest.TestCase):

    def setUp(self):
        self.masks = GeoDataFrame([
            { 'geometry': loads('POLYGON ((50 80, 60 80, 60 70, 50 70, 50 80))') },
            { 'geometry': loads('POLYGON ((0 100, 10 100, 10 10, 90 10, 90 30, 60 30, 60 60, 70 60, 70 40, 90 40, 90 90, 80 90, 80 80, 70 80, 70 90, 30 90, 30 50, 20 50, 20 100, 100 100, 100 0, 0 0, 0 100))') },
            ])

    def tearDown(self):
        pass

    def __plot1(self, label, ptA, ptB, covisible):
        points = GeoDataFrame([ {'geometry': ptA}, {'geometry': ptB} ])
        segment = GeoDataFrame([ {'geometry': LineString([ptA, ptB])} ])

        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        basemap.set_title(label, fontsize=24)
        self.masks.boundary.plot(ax=basemap, color='grey', edgecolor='grey', hatch='/')
        color = 'green' if covisible else 'red'
        points.plot(ax=basemap, color=color)
        segment.plot(ax=basemap, color=color)
        plt.show()
        plt.close(fig)

    def __plot2(self, label, viewPoint, rays, hitPoints):
        points = GeoDataFrame([ {'geometry': viewPoint} ])
        hitPoints = GeoDataFrame([ {'geometry': hitPoint} for hitPoint in hitPoints])
        rays = GeoDataFrame([ {'geometry': ray, 'length': ray.length} for ray in rays.geoms])

        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        basemap.set_title(label, fontsize=24)
        self.masks.boundary.plot(ax=basemap, color='grey', edgecolor='grey', hatch='/')
        rays.plot(ax=basemap, column='length', legend=True)
        points.plot(ax=basemap, color='red')
        hitPoints.plot(ax=basemap, color='red', marker='+')
        plt.show()
        plt.close(fig)

    def __plot3(self, label, pairs):
        origin = GeoDataFrame([ {'geometry': Point([0, 0])} ])
        unitCircle = GeoDataFrame([ {'geometry': Point([0, 0]).buffer(1.0)} ])
        axes = GeoDataFrame([ 
            {'geometry': LineString([(-1, 0), (1, 0)])},
            {'geometry': LineString([(0, -1), (0, 1)])}
            ])
        points = GeoDataFrame([ {'geometry': Point(pair)}  for pair in pairs])

        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        basemap.set_title(label, fontsize=24)
        origin.plot(ax=basemap, color='blue')
        axes.plot(ax=basemap, color='black', linewidth=0.1)
        unitCircle.boundary.plot(ax=basemap, color='black', linewidth=0.1)
        points.plot(ax=basemap, color='red', marker='+')
        plt.show()
        plt.close(fig)

    def testAreCovisibleIn2D(self):
        for ptA, ptB in [
            (Point([0, 0]), Point(10, 10)),
            (Point([0, 0]), Point(100, 100)),
            (Point([30, 70]), Point(90, 70)),
            (Point([40, 90]), Point(60, 50)),
            (Point([50, 50]), Point(80, 50)),
            ]:
            result = RayCasting3Lib.areCovisibleIn2D(ptA, ptB, self.masks)
            self.assertFalse(result, f'Bug with Test: {ptA.wkt} and {ptB.wkt} not covisible')
            # self.__plot1('Not covisible in 2D', ptA, ptB, result)

        for ptA, ptB in [
            (Point([20, 20]), Point(80, 20)),
            (Point([30, 80]), Point(50, 70)),
            (Point([30, 50]), Point(90, 80)),
            (Point([40, 90]), Point(60, 20)),
            ]:
            result = RayCasting3Lib.areCovisibleIn2D(ptA, ptB, self.masks)
            self.assertTrue(result, f'Bug with Test: {ptA.wkt} and {ptB.wkt} covisible')
            # self.__plot1('Covisible in 2D', ptA, ptB, result)

    def testAreCovisibleIn3D(self):
        h, epsilon = 10.0, 1e-3
        self.masks['HAUTEUR'] = h - 1.0

        for ptA, ptB in [
            (Point([0, 0, h]), Point(10, 10, h)),
            (Point([0, 0, h]), Point(100, 100, h)),
            (Point([30, 70, h]), Point(90, 70, h)),
            (Point([40, 90, h]), Point(60, 50, h)),
            (Point([50, 50, h]), Point(80, 50, h)),
            (Point([30, 50, 0]), Point(70, 90, 2 * (h - 1.0) + epsilon)),
            (Point([30, 50, 0]), Point(100, 50, (7 / 3) * (h - 1.0) + epsilon)),
            ]:
            result = RayCasting3Lib.areCovisibleIn3D(ptA, ptB, self.masks, 'HAUTEUR')
            self.assertTrue(result, f'Bug with Test: {ptA.wkt} and {ptB.wkt} covisible in 3D')
            # self.__plot1('Covisible in 3D', ptA, ptB, result)

        for ptA, ptB in [
            (Point([30, 50, 0]), Point(70, 90, 2 * (h - 1.0))),
            (Point([30, 50, 0]), Point(100, 50, (7 / 3) * (h - 1.0))),
            ]:
            result, _ = RayCasting3Lib.areCovisibleIn3D(ptA, ptB, self.masks, 'HAUTEUR')
            self.assertFalse(result, f'Bug with Test: {ptA.wkt} and {ptB.wkt} not covisible in 3D')
            # self.__plot1('Not covisible in 3D', ptA, ptB, result)

    def testOutdoorSingleRayCast2D(self):
        shootingDirs = RayCasting3Lib.preparePanopticRays(nRays=36)
        pairs = [
            (Point([10, 10]), shootingDirs[9]),
            (Point([20, 50]), shootingDirs[9]),
            (Point([30, 50]), shootingDirs[9]),
            (Point([50, 70]), shootingDirs[9]),
            ]
        for viewPoint, shootingDir in pairs:
            ray, hitPoint, hitDist = RayCasting3Lib.outdoorSingleRayCast2D(
                self.masks, viewPoint, shootingDir, rayLength=100.0)
            self.assertEqual(LineString([viewPoint, viewPoint]), ray, 'Test ray value')
            self.assertEqual(viewPoint, hitPoint, 'Test ray value')
            self.assertEqual(0.0, hitDist, 'Test hitDist value')

    def testOutdoorMultipleRayCast2D(self):
        nonNul = lambda dist: (0.0 < dist)
        nRays, rayLength = 36, 100
        shootingDirs = RayCasting3Lib.preparePanopticRays(nRays)

        pairs = [ (Point([10, 10]), 8), (Point([60, 60]), 26), (Point([80, 80]), 26) ]
        for viewPoint, actualNRays in pairs:
            rays, hitPoints, hitDists = RayCasting3Lib.outdoorMultipleRayCast2D(self.masks, viewPoint, shootingDirs, rayLength)
            self.assertEqual(actualNRays, len(list(filter(nonNul, hitDists))), 'Test hitDists values')
            # self.__plot2('MultipleRayCast2D', viewPoint, rays, hitPoints)

    def testPreparePanopticRays(self):
        for nRays in [1, 2, 3, 4, 6, 8, 12, 16, 64, randint(17, 64)]:
            result = RayCasting3Lib.preparePanopticRays(nRays)
            self.assertIsInstance(result, list, 'Test preparePanopticRays (1)')
            self.assertEqual(nRays, len(result), 'Test preparePanopticRays (2)')
            for x, y in result:
                self.assertAlmostEqual(1.0, x ** 2 + y ** 2, None, 'Test preparePanopticRays (3)', 1e-6)
            # self.__plot3(f'preparePanopticRays({nRays})', result)

                
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
