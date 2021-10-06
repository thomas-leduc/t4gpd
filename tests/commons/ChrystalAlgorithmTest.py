'''
Created on 15 dec. 2020

@author: tleduc

Copyright 2020 Thomas Leduc

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

from shapely.geometry import MultiPoint

from t4gpd.commons.ChrystalAlgorithm import ChrystalAlgorithm
from shapely.geometry import Point, Polygon
from numpy import pi


class ChrystalAlgorithmTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun(self):
        inputGeom = MultiPoint([(0, 0), (5, 4), (7, 3), (6, 2)])

        circle, center, radius = ChrystalAlgorithm(inputGeom).run()

        self.assertIsInstance(circle, Polygon, 'circle is a Polygon')
        self.assertIsInstance(center, Point, 'center is a Point')
        self.assertTrue(center.within(circle), 'center is in circle')
        self.assertIsInstance(radius, float, 'radius is a float')
        self.assertAlmostEqual(pi * radius * radius, circle.area, 0, 'Area test')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
