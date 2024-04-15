'''
Created on 22 feb. 2024

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
from numpy import arange
from pandas import DataFrame
from t4gpd.commons.TypeLib import TypeLib


class TypeLibTest(unittest.TestCase):

    def setUp(self):
        self.df = DataFrame({"X": range(5), "Y": 0.1 * arange(5)})

    def tearDown(self):
        pass

    def testAre_both_floating_or_integer(self):
        result = TypeLib.are_both_floating_or_integer(3, 3.3)
        self.assertFalse(result, "3 and 3.3 are not of the same types (1)")

        result = TypeLib.are_both_floating_or_integer(self.df.X, self.df.Y)
        self.assertFalse(
            result, f"{self.df.Y} and {self.df.Y} are not of the same types (2)")

        result = TypeLib.are_both_floating_or_integer(3, self.df.X)
        self.assertTrue(
            result, f"3 and {self.df.Y} are both of the same numeric types (1)")

        result = TypeLib.are_both_floating_or_integer(3.3, self.df.Y)
        self.assertTrue(
            result, f"3.3 and {self.df.Y} are both of the same numeric types (2)")

    def testIs_floating(self):
        result = TypeLib.is_floating(3)
        self.assertFalse(result, "3 is not a floating point value")

        result = TypeLib.is_floating(3.3)
        self.assertTrue(result, "3.3 is a floating point value")

        result = TypeLib.is_floating(self.df.X)
        self.assertFalse(result, f"{self.df.X} is not a floating point Series")

        result = TypeLib.is_floating(self.df.Y)
        self.assertTrue(result, f"{self.df.Y} is a floating point Series")

    def testIs_integer(self):
        result = TypeLib.is_integer(3)
        self.assertTrue(result, "3 is an integer")

        result = TypeLib.is_integer(3.3)
        self.assertFalse(result, "3.3 is not an integer")

        result = TypeLib.is_integer(self.df.X)
        self.assertTrue(result, f"{self.df.X} is an integer Series")

        result = TypeLib.is_integer(self.df.Y)
        self.assertFalse(result, f"{self.df.Y} is not an integer Series")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
