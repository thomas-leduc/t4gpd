'''
Created on 21 avr. 2021

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

from t4gpd.commons.sun.AbstractSunLib import AbstractSunLib
from datetime import datetime


class AbstractSunLibTest(unittest.TestCase):

    def setUp(self):
        self.sunLib = AbstractSunLib() 

    def tearDown(self):
        pass

    def testGetDayOfYear(self):
        dt = datetime(2000, 12, 31)
        self.assertEqual(366, self.sunLib.getDayOfYear(dt), 'Test Dec. 31 2000')

        dt = datetime(2021, 4, 21)
        self.assertEqual(111, self.sunLib.getDayOfYear(dt), 'Test Apr. 21 2021')

        dt = datetime(2021, 12, 31)
        self.assertEqual(365, self.sunLib.getDayOfYear(dt), 'Test Dec. 31 2021')

    def testGetMinutesSpentSinceMidnight(self):
        dt = datetime(2021, 4, 21, 16, 28)
        self.assertEqual(988, self.sunLib.getMinutesSpentSinceMidnight(dt),
                         'Test Apr. 21 2021 at 16:28')

    def testGetTimeSpentSinceMidnight(self):
        dt = datetime(2021, 4, 21, 16, 28)
        self.assertAlmostEqual(16.47, self.sunLib.getTimeSpentSinceMidnight(dt),
                               None, 'Test Apr. 21 2021 at 16:28', 1e-2)

    def testIsALeapYear(self):
        self.assertTrue(self.sunLib.isALeapYear(2000), '2000 is a leap year')
        dt = datetime(2000, 6, 21)
        self.assertTrue(self.sunLib.isALeapYear(dt), '2000 is a leap year')

        self.assertFalse(self.sunLib.isALeapYear(2021), '2021 is not a leap year')
        dt = datetime(2021, 4, 21)
        self.assertFalse(self.sunLib.isALeapYear(dt), '2021 is not a leap year')

    def testNDaysPerYear(self):
        self.assertEqual(366, self.sunLib.nDaysPerYear(2000), '2000 is a leap year')
        dt = datetime(2000, 6, 21)
        self.assertEqual(366, self.sunLib.nDaysPerYear(dt), '2000 is a leap year')

        self.assertEqual(365, self.sunLib.nDaysPerYear(2021), '2021 is not a leap year')
        dt = datetime(2021, 4, 21)
        self.assertEqual(365, self.sunLib.nDaysPerYear(dt), '2021 is not a leap year')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
