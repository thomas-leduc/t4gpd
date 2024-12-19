'''
Created on 15 oct. 2024

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

from t4gpd.commons.IntervalLib import IntervalLib


class IntervalLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testMerge1(self):
        intervals = [[1, 3], [6, 9], [2, 5], [10, 12]]
        expected = [[1, 5], [6, 9], [10, 12]]
        actual = IntervalLib.merge(intervals)
        self.assertEqual(expected, actual, "Test merge (1)")

    def testMerge2(self):
        from datetime import date, datetime
        from pandas import date_range

        dts = date_range(
            start=date(2024, 9, 30),
            end=date(2024, 10, 10),
            freq="D"
        )
        intervals = ([dts[2], dts[4]], [dts[6], dts[7]],
                     [dts[1], dts[5]], [dts[8], dts[9]])
        expected = [
            [datetime(2024, 10, 1), datetime(2024, 10, 5)],
            [datetime(2024, 10, 6), datetime(2024, 10, 7)],
            [datetime(2024, 10, 8), datetime(2024, 10, 9)],
        ]
        actual = IntervalLib.merge(intervals)
        self.assertEqual(expected, actual, "Test merge (2)")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
