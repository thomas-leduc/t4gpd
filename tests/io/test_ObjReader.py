'''
Created on 25 aug. 2020

@author: tleduc
'''
import unittest

from shapely.geometry import Polygon
from t4gpd.io.ObjReader import ObjReader

import geopandas as gpd
from t4gpd.commons.TestUtils import TestUtils


class Test(unittest.TestCase):

    def setUp(self):
        self.inputFilename = TestUtils.getDataSetFilename('tests/data', 'surfaceWithHole.obj')

    def tearDown(self):
        pass

    def testRun(self):
        result = ObjReader(self.inputFilename).run()

        self.assertIsInstance(result, gpd.GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(172, len(result), 'Count rows')
        self.assertEqual(1, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertEqual(len(row.geometry.exterior.coords), 4, 'Is a GeoDataFrame of Triangles')
            self.assertEqual(len(row.geometry.interiors), 0, 'Is a GeoDataFrame of Triangles')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
