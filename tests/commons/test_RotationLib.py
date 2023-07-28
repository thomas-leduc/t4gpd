'''
Created on 11 sept. 2020

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

from numpy import array_equal, asarray, sqrt
from shapely.geometry import LinearRing, LineString, MultiLineString, MultiPoint, Point, Polygon
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.RotationLib import RotationLib


class RotationLibTest(unittest.TestCase):

    def setUp(self):
        self.zero = AngleLib.toRadians(0)

    def tearDown(self):
        pass

    def testMakeRotationMatrix(self):
        expected = asarray([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
        actual = RotationLib.makeRotationMatrix([1, 0, 0], [0, 1, 0])
        self.assertTrue(array_equal(actual, expected), 'msg')

        a = 1 / sqrt(2)
        expected = asarray([[-a, 0, -a], [0, 1, 0], [a, 0, -a]])
        actual = RotationLib.makeRotationMatrix([1, 0, 0], [-a, 0, a])
        for nl in range(3):
            for nc in range(3):
                self.assertAlmostEqual(
                    expected[nl, nc], actual[nl, nc], None,
                    f'\nInequality in row {nl} and column {nc}', 1e-9)

    def testRotate2DXYZ(self):
        for p in [Point((1, 0)), (1, 0)]:
            pp = RotationLib.rotate2DXYZ(p, AngleLib.toRadians(90))
            self.assertTrue(Epsilon.equals([0.0, 1.0], pp), 'Equality test (1)')

        for p in [Point((1, 0, 123)), (1, 0, 123)]:
            pp = RotationLib.rotate2DXYZ(p, AngleLib.toRadians(90))
            self.assertTrue(Epsilon.equals([0.0, 1.0, 123.0], pp), 'Equality test (2)')

    def testRotate2D(self):
        geoms = [
            Point((1, 2)),
            LineString(((1, 2), (3, 4))),
            LinearRing(((1, 2), (3, 4), (0, 3))),
            Polygon(((1, 2), (3, 4), (0, 3))),
            MultiPoint([(1, 2)]),
            MultiLineString([((1, 2), (3, 4))])
            ]
        for g in geoms:
            gg = RotationLib.rotate2D(g, self.zero)
            self.assertEqual(g, gg, 'Equality test')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
