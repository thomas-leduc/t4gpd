'''
Created on 21 janv. 2021

@author: tleduc

Copyright 2020 Thomas Leduc

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
from datetime import datetime, timezone
import unittest

from numpy import abs
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.PySolarSunLib import PySolarSunLib


class PySolarSunLibTest(unittest.TestCase):

    def setUp(self):
        gdf = LatLonLib.NANTES
        self.sunLib = PySolarSunLib(gdf)
        self.lat, _ = LatLonLib.fromGeoDataFrameToLatLon(gdf)

    def tearDown(self):
        pass

    def testGetDayLengthInMinutes(self):
        dt = datetime(2021, 4, 21, tzinfo=timezone.utc)

        _actual = self.sunLib.getDayLengthInMinutes(dt)
        self.assertEqual(836, _actual, 'Test day length in minutes')

    def testGetRadiationDirection(self):
        dt = datetime(2021, 6, 21, 12, tzinfo=timezone.utc)
        result = self.sunLib.getRadiationDirection(dt)

        self.assertAlmostEqual(0.032, result[0], None, 'Test x-component', 1e-3)
        self.assertAlmostEqual(-0.402, result[1], None, 'Test y-component', 1e-3)
        self.assertAlmostEqual(0.914, result[2], None, 'Test z-component', 1e-3)

    def testGetSolarAnglesInDegrees1(self):
        dt = datetime(2021, 6, 21, 12, tzinfo=timezone.utc)
        result = self.sunLib.getSolarAnglesInDegrees(dt)

        self.assertIsInstance(result, tuple, 'Test return type')
        self.assertEqual(2, len(result), 'Test return length')
        self.assertTrue(abs((90 + 23 - self.lat) - result[0]) <= 1, 'Test alti at summer solstice)')
        self.assertTrue(abs(270 - result[1]) <= 5, 'Test azim at summer solstice)')

    def testGetSolarAnglesInDegrees2(self):
        dt = datetime(2021, 12, 21, 12, tzinfo=timezone.utc)
        result = self.sunLib.getSolarAnglesInDegrees(dt)

        self.assertIsInstance(result, tuple, 'Test return type')
        self.assertEqual(2, len(result), 'Test return length')
        self.assertTrue(abs((90 - 23 - self.lat) - result[0]) <= 1, 'Test alti at winter solstice)')
        self.assertTrue(abs(270 - result[1]) <= 2, 'Test azim at winter solstice)')

    def testGetSunrise(self):
        dt = datetime(2021, 4, 21, tzinfo=timezone.utc)

        _expected = datetime(2021, 4, 21, 5, 8, tzinfo=timezone.utc)
        _actual = self.sunLib.getSunrise(dt)
        _delta = (_actual - _expected).seconds

        self.assertLess(_delta, 7, 'Test sunrise value')

    def testGetSunset(self):
        dt = datetime(2021, 4, 21, tzinfo=timezone.utc)

        _expected = datetime(2021, 4, 21, 19, 3, tzinfo=timezone.utc)
        _actual = self.sunLib.getSunset(dt)
        _delta = (_actual - _expected).seconds

        self.assertLess(_delta, 61, 'Test sunset value')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
