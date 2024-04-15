'''
Created on 15 dec. 2020

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
from shapely.geometry import Polygon
from t4gpd.commons.CaliperLib import CaliperLib


class CaliperLibTest(unittest.TestCase):

    def setUp(self):
        self.rectangle = Polygon([(1, 0), (3, 0), (4, 1), (3, 1.9), (1, 1.9), (0, 1), (1, 0)])
        pass

    def tearDown(self):
        pass

    def testMabr(self):
        rect, len1, len2 = CaliperLib.mabr(self.rectangle)
        self.assertIsInstance(rect, Polygon, 'MABR is a Polygon')
        self.assertTrue(len1 >= len2, 'MABR is a Polygon')
        print(rect, len1, len2)

    def testMpbr(self):
        rect, len1, len2 = CaliperLib.mpbr(self.rectangle)
        self.assertIsInstance(rect, Polygon, 'MPBR is a Polygon')
        self.assertTrue(len1 >= len2, 'MPBR is a Polygon')
        print(rect, len1, len2)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
