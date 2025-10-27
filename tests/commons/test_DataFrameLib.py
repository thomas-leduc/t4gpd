"""
Created on 26 oct. 2022

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

import unittest
from datetime import datetime, timedelta
from numpy import nan
from numpy.random import default_rng
from pandas import DataFrame
from t4gpd.commons.DataFrameLib import DataFrameLib


class DataFrameLibTest(unittest.TestCase):

    def setUp(self):
        dt = datetime(2022, 10, 26, 9)
        oneHour = timedelta(hours=1)
        self.df1 = DataFrame(
            data=[
                {"colA": i, "colB": i**2, "colC": dt + i * oneHour} for i in range(10)
            ]
        )

        self.df2 = self.df1.copy(deep=True)
        colA = self.df2.colA.to_list()
        default_rng(0).shuffle(colA)
        self.df2.colA = colA

    def tearDown(self):
        pass

    def testEquals(self):
        df1 = DataFrame({"A": [1, 2, 3]})
        df2 = df1.sample(frac=1, random_state=0)
        self.assertFalse(df1.equals(df2), "Test simple DataFrame equality")
        self.assertTrue(DataFrameLib.equals(df1, df2), "Test DataFrameLib.equals()")

    def testFillWithMissingRows(self):
        expected = DataFrame(
            {
                "A": [1, 2, 3],
                "B": ["x", "y", "z"],
                "C": [True, True, nan],
                "D": [nan, nan, False],
            }
        )
        #
        df1 = DataFrame({"A": [1, 2], "B": ["x", "y"], "C": True})
        df2 = DataFrame({"A": [1, 3], "B": ["x", "z"], "D": False})
        #
        actual = DataFrameLib.fillWithMissingRows(df1, df2, on=["A", "B"])
        self.assertTrue(expected.equals(actual), "Test simple DataFrame equality")
        #
        actual = DataFrameLib.fillWithMissingRows(df1, df2, on=["A"])
        self.assertTrue(expected.equals(actual), "Test simple DataFrame equality")

    def testGetNewColumnName(self):
        result = DataFrameLib.getNewColumnName(self.df1)
        self.assertEqual(10, len(result), "Is a string of 10 chars")
        self.assertFalse(result in self.df1, "Is not a column name")

    def testHasAPrimaryKeyIndex(self):
        self.assertTrue(
            DataFrameLib.hasAPrimaryKeyIndex(self.df1), "Test hasAPrimaryKeyIndex (1)"
        )
        self.assertTrue(
            DataFrameLib.hasAPrimaryKeyIndex(self.df2), "Test hasAPrimaryKeyIndex (2)"
        )
        self.assertTrue(
            DataFrameLib.hasAPrimaryKeyIndex(DataFrame()),
            "Test hasAPrimaryKeyIndex (3)",
        )
        self.assertTrue(
            DataFrameLib.hasAPrimaryKeyIndex(DataFrame(index=[1, 2, 3])),
            "Test hasAPrimaryKeyIndex (4)",
        )
        self.assertFalse(
            DataFrameLib.hasAPrimaryKeyIndex(DataFrame(index=[1, 1, 2])),
            "Test hasAPrimaryKeyIndex (5)",
        )

    def testInterpolate(self):
        result = DataFrameLib.interpolate(self.df1, "colA", "colA", 4.5)
        self.assertEqual(4.5, result, "Is equal to 4.5")

        result = DataFrameLib.interpolate(self.df1, "colA", "colB", 4.5)
        self.assertEqual(20.5, result, "Is equal to 20.5")

        result = DataFrameLib.interpolate(self.df1, "colA", "colC", 4.5)
        self.assertEqual(
            datetime(2022, 10, 26, 13, 30), result, 'Is equal to "2022-10-26 13:30:00"'
        )

        try:
            result = DataFrameLib.interpolate(self.df2, "colA", "colB", 4.5)
        except AssertionError as error:
            self.assertEqual(
                str(error), 'Column "colA" must be monotonic', "Trap error message"
            )

    def testIsAPrimaryKey(self):
        self.assertTrue(
            DataFrameLib.isAPrimaryKey(self.df1, "colA"), "Test isAPrimaryKey (1)"
        )
        self.assertTrue(
            DataFrameLib.isAPrimaryKey(self.df2, "colA"), "Test isAPrimaryKey (2)"
        )
        self.assertFalse(
            DataFrameLib.isAPrimaryKey(DataFrame(), "gid"), "Test isAPrimaryKey (3)"
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
