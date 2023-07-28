'''
Created on 31 aug. 2020

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

from shapely.geometry import Polygon
from t4gpd.io.CSVWKTReader import CSVWKTReader

import geopandas as gpd
from t4gpd.commons.TestUtils import TestUtils


class CSVWKTReaderTest(unittest.TestCase):

    def setUp(self):
        self.inputFilename = TestUtils.getDataSetFilename('tests/data', 'ensa_nantes.wkt')

    def tearDown(self):
        pass

    def testRun(self):
        result = CSVWKTReader(self.inputFilename, 'the_geom:Polygon', ';', 'EPSG:2154').run()

        self.assertIsInstance(result, gpd.GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(38, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertGreaterEqual(row['# gid:int'], 0, 'Check attribute')
            self.assertGreaterEqual(row['elevation:string'], 4, 'Check attribute')

        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
