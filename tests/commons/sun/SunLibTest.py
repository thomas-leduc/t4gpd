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
import unittest

from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunLib import SunLib


class SunLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testPlotDayLengths(self):
        # SunLib(model='solene').plotDayLengths()
        SunLib(gdf=LatLonLib.NANTES, model='pysolar').plotDayLengths()

    def testPlotSolarDeclination(self):
        # SunLib(model='solene').plotSolarDeclination()
        SunLib(model='pysolar').plotSolarDeclination()

    def testPlotSunAltiAtNoon(self):
        # SunLib(model='solene').plotSunAltiAtNoon()
        SunLib(gdf=LatLonLib.NANTES, model='pysolar').plotSunAltiAtNoon()

    def testPlotSunriseSunset(self):
        # SunLib(model='solene').plotSunriseSunset()
        SunLib(gdf=LatLonLib.NANTES, model='pysolar').plotSunriseSunset()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
