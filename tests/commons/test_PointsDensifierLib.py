'''
Created on 20 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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

from shapely.geometry import LineString, Point
from t4gpd.commons.ArrayCoding import ArrayCoding

from t4gpd.commons.PointsDensifierLib import PointsDensifierLib


class PointsDensifierLibTest(unittest.TestCase):

    def setUp(self):
        self.geom1 = LineString(((0, 0), (100, 0)))
        self.geom2 = LineString()

    def tearDown(self):
        pass

    def testDensifyByDistance1(self):
        result = PointsDensifierLib.densifyByDistance(
            self.geom1, distance=10.0, blockid=0, adjustableDist=True)

        self.assertIsInstance(result, list, 'Is a list')
        for i, _dict in enumerate(result):
            self.assertIsInstance(_dict, dict, 'Is a list of dict')

            self.assertEqual([0, 0, i], ArrayCoding.decode(_dict['node_id']), 'Test node_id value')
            self.assertEqual([1, 0], ArrayCoding.decode(_dict['motion_dir']), 'Test motion_dir value')
            self.assertEqual(Point((10 * i, 0)), _dict['geometry'], 'Test geometry value')

    def testDensifyByDistance2(self):
        result = PointsDensifierLib.densifyByDistance(
            self.geom2, distance=10.0, blockid=0, adjustableDist=True)
        self.assertEqual([], result, 'Test result emptiness')

    def testDensifyByCurvilinearAbscissa1(self):
        result = PointsDensifierLib.densifyByCurvilinearAbscissa(
            self.geom1, curvAbsc=[0, 0.25, 0.5, 0.75], blockid=0)

        self.assertIsInstance(result, list, 'Is a list')
        for i, _dict in enumerate(result):
            self.assertIsInstance(_dict, dict, 'Is a list of dict')

            self.assertEqual([0, 0, i], ArrayCoding.decode(_dict['node_id']), 'Test node_id value')
            self.assertEqual([1, 0], ArrayCoding.decode(_dict['motion_dir']), 'Test motion_dir value')
            self.assertEqual(Point((25 * i, 0)), _dict['geometry'], f'Test geometry value ({i})')


    def testDensifyByCurvilinearAbscissa2(self):
        result = PointsDensifierLib.densifyByCurvilinearAbscissa(
            self.geom2, curvAbsc=[0, 0.25, 0.5, 0.75], blockid=0)
        self.assertEqual([], result, 'Test result emptiness')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
