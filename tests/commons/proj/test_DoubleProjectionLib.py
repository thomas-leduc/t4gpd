'''
Created on 22 mar. 2024

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
from t4gpd.commons.proj.DoubleProjectionLib import DoubleProjectionLib


class DoubleProjectionLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_projectionSwitch(self):
        PAIRS = [
            ("Isoaire", "isoaire_projection"),
            ("Orthogonal", "orthogonal_projection"),
            ("Stereographic", "stereographic_projection"),
        ]
        for projectionName, expected in PAIRS:
            result = DoubleProjectionLib.projectionSwitch(
                projectionName)
            self.assertEqual(expected, result.__name__,
                             "Test _projectionSwitch")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
