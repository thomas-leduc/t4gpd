'''
Created on 7 janv. 2021

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
from numpy import array, nan
from geopandas import GeoDataFrame
from pandas import isna
from shapely import Point
from t4gpd.commons.ArrayCoding import ArrayCoding


class ArrayCodingTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testEncode(self):
        self.assertTrue(isna(ArrayCoding.encode(None)), "Test encode None")
        self.assertEqual("123", ArrayCoding.encode(123),
                         "Test encode ouput (1)")
        self.assertEqual("12.3", ArrayCoding.encode(
            12.3), "Test encode ouput (2)")
        self.assertEqual("123#12.3", ArrayCoding.encode(
            (123, 12.3)), "Test encode ouput (3)")
        self.assertEqual("123#12.3", ArrayCoding.encode(
            [123, 12.3]), "Test encode ouput (4)")
        self.assertEqual("123#12.3", ArrayCoding.encode(
            {123, 12.3}), "Test encode ouput (5)")
        self.assertEqual("123#12.3", ArrayCoding.encode(
            {123: "a", 12.3: "b"}), "Test encode ouput (6)")
        self.assertEqual("123.0#12.3", ArrayCoding.encode(
            array([123, 12.3])), "Test encode ouput (7)")

    def testDecode(self):
        self.assertTrue(isna(ArrayCoding.decode(None)), "Test decode None")
        self.assertEqual([123, 12.3], ArrayCoding.decode(
            "123#12.3"), "Test decode ouput (1)")
        self.assertEqual([123, 12.3], ArrayCoding.decode(
            "123:12.3", separator=":"), "Test decode ouput (2)")
        self.assertEqual(["123", "12.3"], ArrayCoding.decode(
            "123#12.3", outputType=str), "Test decode ouput (3)")

    def testEncodeDecode(self):
        expected = GeoDataFrame({"A": range(4), "B": [[0], None, [2, 2], nan],
                                 "geometry": [Point()]*4}, crs="epsg:2154")
        actual = expected.copy(deep=True)
        actual.B = actual.B.apply(lambda v: ArrayCoding.encode(v))
        actual.B = actual.B.apply(
            lambda v: ArrayCoding.decode(v, outputType=int))
        self.assertTrue(expected.equals(actual),
                        "Test encode + decode")
        print(f"{expected}\n\n{actual}")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
