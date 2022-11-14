'''
Created on 8 nov. 2022

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
from numpy import pi
from shapely.geometry import Polygon
from t4gpd.commons.crossroads_generation.SequenceRadii import SequenceRadii


class SequenceRadiiTest(unittest.TestCase):

    def setUp(self):
        self.w, self.r = 12.0, 100.0

    def tearDown(self):
        pass

    def testGetBranch(self):
        actual = SequenceRadii(nbranchs=4, width=self.w, length=self.r).getBranch(0)
        self.assertIsInstance(actual, Polygon, 'getSector(...) is a Polygon')
        expected = self.r * self.w
        delta = 0.01 * expected  # approxim. = 1%
        self.assertAlmostEqual(expected, actual.area, None,
                               'check the area of the polygon', delta)

    def testGetSector(self):
        actual = SequenceRadii(nbranchs=4, width=self.w, length=self.r).getSector([0, 1])
        self.assertIsInstance(actual, Polygon, 'getSector(...) is a Polygon')
        expected = 0.25 * pi * self.r ** 2
        delta = 0.14 * expected  # approxim. = 14%
        self.assertAlmostEqual(expected, actual.area, None,
                               'check the area of the polygon', delta)

        actual = SequenceRadii(nbranchs=4, width=self.w, length=self.r).getSector([0, 2])
        self.assertIsInstance(actual, Polygon, 'getSector(...) is a Polygon')
        expected = 0.5 * pi * self.r ** 2
        delta = 0.07 * expected  # approxim. = 7%
        self.assertAlmostEqual(expected, actual.area, None,
                               'check the area of the polygon', delta)

        actual = SequenceRadii(nbranchs=4, width=self.w, length=self.r).getSector([0, 4])
        self.assertIsInstance(actual, Polygon, 'getSector(...) is a Polygon')
        expected = pi * self.r ** 2
        delta = 0.01 * expected  # approxim. = 1%
        self.assertAlmostEqual(expected, actual.area, None,
                               'check the area of the polygon', delta)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
