'''
Created on 20 janv. 2021

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

from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.TestUtils import TestUtils
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class LatLonLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testFromGeoDataFrameToLatLon1(self):
        gdf = GeoDataFrameDemos.ensaNantesBuildings()
        result = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        self.assertIsInstance(result, tuple, 'Test return type')
        self.assertEqual(2, len(result), 'Test return length')
        self.assertAlmostEqual(47.2, result[0], 1, 'Test return value (default latitude)')
        self.assertAlmostEqual(-1.55, result[1], 1, 'Test return value (default longitude)')

    def testFromGeoDataFrameToLatLon2(self):
        gdf = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_path.shp')
        result = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        self.assertIsInstance(result, tuple, 'Test return type')
        self.assertEqual(2, len(result), 'Test return length')
        self.assertAlmostEqual(47.2, result[0], 1, 'Test return value (default latitude)')
        self.assertAlmostEqual(-1.55, result[1], 1, 'Test return value (default longitude)')

    def testFromGeoDataFrameToLatLon3(self):
        gdf = GeoDataFrame([])
        result = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        self.assertIsInstance(result, tuple, 'Test return type')
        self.assertEqual(2, len(result), 'Test return length')
        self.assertEqual(47.2, result[0], 'Test return value (default latitude)')
        self.assertEqual(-1.55, result[1], 'Test return value (default longitude)')

    def testFromGeoDataFrameToLatLon4(self):
        gdf = LatLonLib.REYKJAVIK
        result = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        self.assertIsInstance(result, tuple, 'Test return type')
        self.assertEqual(2, len(result), 'Test return length')
        self.assertEqual(64.13548, result[0], 'Test return value (latitude)')
        self.assertEqual(-21.89541, result[1], 'Test return value (longitude)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
