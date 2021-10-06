'''
Created on 17 juin 2020

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
from shapely.geometry import LineString
import unittest

from t4gpd.graph.STToRoadsSections import STToRoadsSections
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from geopandas.geodataframe import GeoDataFrame


class STToRoadsSectionsTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()

    def tearDown(self):
        self.roads = None

    def testRunWithCulDeSac(self):
        result = STToRoadsSections(self.roads, withoutCulDeSac=False).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(35, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineStrings')
            self.assertTrue(1 < row['distance'] < 120, 'distance attribute values')

    def testRunWithoutCulDeSac(self):
        result = STToRoadsSections(self.roads, withoutCulDeSac=True).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(23, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineStrings')
            self.assertTrue(1 < row['distance'] < 120, 'distance attribute values')

        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
