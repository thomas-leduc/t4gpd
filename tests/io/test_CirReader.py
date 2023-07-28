'''
Created on 10 mars 2021

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
from shapely.geometry import Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.io.CirReader import CirReader

from t4gpd.commons.TestUtils import TestUtils
from t4gpd.demos.GeoDataFrameDemos5 import GeoDataFrameDemos5


class CirReaderTest(unittest.TestCase):

    def setUp(self):
        self.inputFilename = TestUtils.getDataSetFilename('tests/data', 'cube_unitaire.cir')

    def tearDown(self):
        pass

    def testRun1(self):
        result = CirReader(self.inputFilename).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(6, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIn(int(row.cir_id), range(1, 1 + len(result)), 'Test gid attr. values')
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertTrue(GeomLib.is3D(row.geometry), 'Is a GeoDataFrame of 3D Polygons')
            self.assertEqual(1.0, abs(GeomLib3D.getArea(row.geometry)), 'Test 3D Polygon area')
            # self.assertListEqual(row.normal_vec, GeomLib3D.getFaceNormalVector(row.geometry), 'Test normal vector')

    def testRun2(self):
        result = GeoDataFrameDemos5.cirSceneMasque1Corr()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(370, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIn(int(row.cir_id), range(1, 1 + len(result)), 'Test gid attr. values')
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertTrue(GeomLib.is3D(row.geometry), 'Is a GeoDataFrame of 3D Polygons')
            # self.assertListEqual(row.normal_vec, GeomLib3D.getFaceNormalVector(row.geometry), 'Test normal vector')

    def testRun3(self):
        result = GeoDataFrameDemos5.cirSceneMasque2Corr()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(370, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIn(int(row.cir_id), range(1, 1 + len(result)), 'Test gid attr. values')
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertTrue(GeomLib.is3D(row.geometry), 'Is a GeoDataFrame of 3D Polygons')
            # self.assertListEqual(row.normal_vec, GeomLib3D.getFaceNormalVector(row.geometry), 'Test normal vector')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
