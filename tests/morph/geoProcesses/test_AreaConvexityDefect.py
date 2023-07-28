'''
Created on 16 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.AreaConvexityDefect import AreaConvexityDefect
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class AreaConvexityDefectTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        self.buildings = None

    def testRun(self):
        result = STGeoProcess(AreaConvexityDefect, self.buildings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(44, len(result), '44 rows')
        self.assertEqual(4, len(result.columns), '4 columns')
        self.assertIn('a_conv_def', result.columns, 'Has a "a_conv_def" column')
        for _, row in result.iterrows():
            self.assertTrue(0 <= row['a_conv_def'] <= 1, '0 <= conv. defect <= 1')

        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
