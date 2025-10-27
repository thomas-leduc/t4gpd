"""
Created on 19 jun. 2025

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
from numpy import float16, float32, int8, int16, int32, ndarray, uint8, uint16, uint32
from t4gpd.commons.ArrayLib import ArrayLib


class ArrayLibTest(unittest.TestCase):

    def setUp(self):
        from numpy import asarray

        self.arrays = [
            ([1, 2, 3], uint8),
            ([-1, 2, -3], int8),
            (2**8 + asarray([1, 2, 3]), uint16),
            (2**8 * asarray([-1, 0, 1]), int16),
            (2**16 * asarray([1, 0, 2]), uint32),
            (2**16 * asarray([-1, 0, 1]), int32),
            ([1.0, 2.0, 3.0], float16),
            (2**16 * asarray([1.0, 2.0, 3.0]), float32),
            ([True, False, True], bool),
        ]

    def tearDown(self):
        pass

    def testGet_compact_dtype(self):
        for arr, expected in self.arrays:
            actual = ArrayLib.get_compact_dtype(arr)
            self.assertEqual(actual, expected, f"Test get_compact_dtype for {arr}")

    def testCast_compact_dtype(self):
        for arr, expected in self.arrays:
            actual = ArrayLib.cast_compact_dtype(arr)
            self.assertIsInstance(actual, ndarray, f"Test cast_compact_dtype for {arr}")
            self.assertEqual(
                actual.dtype, expected, f"Test cast_compact_dtype for {arr}"
            )
            # Check if the values are preserved
            self.assertTrue((actual == arr).all(), f"Values not preserved for {arr}")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
