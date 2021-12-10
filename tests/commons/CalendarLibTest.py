'''
Created on 1 juil. 2021

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
from datetime import date
import unittest

from t4gpd.commons.CalendarLib import CalendarLib


class CalendarLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGetEncapsulatingWeek(self):
        for month, monday, sunday in [(3, 15, 21), (6, 21, 27), (12, 20, 26)]:
            result = CalendarLib.getEncapsulatingWeek(date(2021, month, 21))
            self.assertIsInstance(result, tuple, 'Test the type of result')
            self.assertEqual(2, len(result), 'Test the length of result')
            self.assertEqual(date(2021, month, monday), result[0], 'Test the result value (1)')
            self.assertEqual(date(2021, month, sunday), result[1], 'Test the result value (1)')

        result = CalendarLib.getEncapsulatingWeek()
        self.assertIsInstance(result, tuple, 'Test the type of result')
        self.assertEqual(2, len(result), 'Test the length of result')
        self.assertTrue(result[0] <= date.today() <= result[1], 'Test the result values')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
