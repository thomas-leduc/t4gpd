'''
Created on 27 sep. 2024

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

from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class SatelliteLibTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testConstellation(self):
        pairs = [
            ("E15", "Galileo"),
            ("R07", "GLONASS"),
            ("G05", "GPS"),
        ]
        for satName, expected in pairs:
            actual = SatelliteLib.constellation(satName)
            self.assertEqual(actual, expected, "Test constellation")

    def testGet_satellite_name(self):
        pairs = [
            (72, "E15"),
            (38, "R07"),
            (4, "G05"),
        ]
        for satName, expected in pairs:
            actual = SatelliteLib.get_satellite_name(satName)
            self.assertEqual(actual, expected, "Test get_satellite_name")


if __name__ == "__main__":
    # import sys; sys.argv = ['', 'Test.testRun']
    unittest.main()
