'''
Created on 26 oct. 2022

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
from datetime import datetime, timedelta
import unittest

from numpy.random import seed, shuffle
from pandas import DataFrame

from t4gpd.commons.DataFrameLib import DataFrameLib


class DataFrameLibTest(unittest.TestCase):

    def setUp(self):
        dt = datetime(2022, 10, 26, 9)
        oneHour = timedelta(hours=1)
        self.df1 = DataFrame(data=[
            {'colA': i, 'colB': i ** 2, 'colC': dt + i * oneHour} for i in range(10)
        ])

        self.df2 = self.df1.copy(deep=True)
        colA = self.df2.colA.to_list()
        seed(0)
        shuffle(colA)
        self.df2.colA = colA

    def tearDown(self):
        pass

    def testGetNewColumnName(self):
        result = DataFrameLib.getNewColumnName(self.df1)
        self.assertEqual(10, len(result), 'Is a string of 10 chars')
        self.assertFalse(result in self.df1, 'Is not a column name')

    def testInterpolate(self):
        result = DataFrameLib.interpolate(self.df1, 'colA', 'colA', 4.5)
        self.assertEqual(4.5, result, 'Is equal to 4.5')

        result = DataFrameLib.interpolate(self.df1, 'colA', 'colB', 4.5)
        self.assertEqual(20.5, result, 'Is equal to 20.5')

        result = DataFrameLib.interpolate(self.df1, 'colA', 'colC', 4.5)
        self.assertEqual(datetime(2022, 10, 26, 13, 30), result,
                         'Is equal to "2022-10-26 13:30:00"')

        try:
            result = DataFrameLib.interpolate(self.df2, 'colA', 'colB', 4.5)
        except AssertionError as error:
            self.assertEqual(
                str(error), 'Column "colA" must be monotonic', 'Trap error message')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
