'''
Created on 25 sep. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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

from numpy import array_equal, pi, r_
from t4gpd.commons.AngleLib import AngleLib


class AngleLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testAngleBetween(self):
        trios = [
            ((1, 0), (1, 0), 0),
            ((1, 0), (1, 1), pi/4),
            ((1, 0), (0, 1), pi/2),
            ((1, 0), (-1, 1), 3*pi/4),
            ((1, 0), (-1, 0), pi),
            ((1, 0), (-1, -1), 5*pi/4),
            ((1, 0), (0, -1), 3*pi/2),
            ((1, 0), (1, -1), 7*pi/4),
            ((0, -1), (1, 0), pi/2),
        ]
        for dir1, dir2, expected in trios:
            actual = AngleLib.angleBetween(dir1, dir2)
            self.assertEqual(actual, expected, "Test angleBetween")

    def testAngleBetweenNodes(self):
        trios = [
            ((1, 0), (1, 0), 0),
            ((1, 0), (1, 1), pi/4),
            ((1, 0), (0, 1), pi/2),
            ((1, 0), (-1, 1), 3*pi/4),
            ((1, 0), (-1, 0), pi),
            ((1, 0), (-1, -1), 5*pi/4),
            ((1, 0), (0, -1), 3*pi/2),
            ((1, 0), (1, -1), 7*pi/4),
        ]
        orig = (0, 0)
        for node1, node2, expected in trios:
            actual = AngleLib.angleBetweenNodes(node1, orig, node2)
            self.assertEqual(actual, expected, "Test angleBetweenNodes")

    def testCompositions(self):
        for expected in range(360):
            actual1 = AngleLib.eastCCW2northCW(
                AngleLib.northCW2eastCCW(expected, degree=True), degree=True)
            self.assertEqual(actual1, expected,
                             "Test eastCCW2northCW o northCW2eastCCW")

            actual2 = AngleLib.northCW2eastCCW(
                AngleLib.eastCCW2northCW(expected, degree=True), degree=True)
            self.assertEqual(actual2, expected,
                             "Test northCW2eastCCW o eastCCW2northCW")

    def testEastCCW2northCW(self):
        pairs = [(90, 0), (0, 90), (180, 270), (270, 180), (359, 91)]
        for angle, expected in pairs:
            actual = AngleLib.eastCCW2northCW(angle, degree=True)
            self.assertEqual(actual, expected, "Test eastCCW2northCW")

    def testFromEastCCWAzimuthToOppositeSliceIds(self):
        nslices, trios = 64, [
            (0, 0, slice(16, 49)),
            (45, 0, slice(24, 57)),
            (90, 0, r_[slice(32, 64), slice(0, 1)]),
            (180, 0, r_[slice(48, 64), slice(0, 17)]),
            (270, 0, slice(0, 33)),
            # NON-ZERO OFFSET
            (0, 1, slice(17, 48)),
            (45, 2, slice(26, 55)),
            (90, 3, slice(35, 62)),
        ]
        for azim, offset, expected in trios:
            actual = AngleLib.fromEastCCWAzimuthToOppositeSliceIds(
                azim, nslices, offset, degree=True)
            self.assertTrue(array_equal(actual, expected),
                            "Test fromEastCCWAzimuthToOppositeSliceIds")

    def testFromEastCCWAzimuthToSliceId(self):
        nslices, pairs = 64, [
            (88, 16), (89, 16), (90, 16), (91, 16), (92, 16), (93, 17),
            (180, 32), (270, 48), (-3, 63), (-2, 0), (2, 0)
        ]
        for azim, expected in pairs:
            actual = AngleLib.fromEastCCWAzimuthToSliceId(
                azim, nslices, degree=True)
            self.assertEqual(actual, expected,
                             "Test fromEastCCWAzimuthToSliceId")

    def testNormAzimuth(self):
        pairs = [((1, 0), 0), ((1, 1), pi/4), ((0, 1), pi/2),
                 ((-1, 1), 3*pi/4), ((-1, 0), pi), ((-1, -1), 5*pi/4),
                 ((0, -1), 3*pi/2), ((1, -1), 7*pi/4)]
        for direction, expected in pairs:
            actual = AngleLib.normAzimuth(direction)
            self.assertEqual(actual, expected, "Test normAzimuth")

    def testNormalizeAngle(self):
        pairs = [(450, 90), (-90, 270), (-180, 180), (720, 0)]
        for angle, expected in pairs:
            actual = AngleLib.normalizeAngle(angle, degree=True)
            self.assertEqual(actual, expected, "Test normalizeAngle")

    def testNorthCW2eastCCW(self):
        pairs = [(0, 90), (90, 0), (180, 270), (270, 180), (359, 91)]
        for angle, expected in pairs:
            actual = AngleLib.northCW2eastCCW(angle, degree=True)
            self.assertEqual(actual, expected, "Test northCW2eastCCW")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
