'''
Created on 19 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.Diameter import Diameter
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class DiameterTest(unittest.TestCase):

    def setUp(self):
        self.building = GeoDataFrameDemos.singleBuildingInNantes()
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        self.buildings = None

    def testRun1(self):
        result = STGeoProcess(Diameter, self.buildings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(len(self.buildings), len(result), 'Count rows')
        self.assertEqual(2 + len(self.buildings.columns), len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            self.assertIsInstance(row.diam_len, float, 'Test diam_len attribute')
            self.assertTrue(0 < row.diam_len < 103.0, 'Test diam_len attribute')
            self.assertIsInstance(row.diam_azim, float, 'Test diam_azim attribute')
            self.assertTrue(0 < row.diam_azim < 180.0, 'Test diam_len attribute')

        '''
        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey', edgecolor='black', linewidth=0.3)
        result.plot(ax=basemap, color='red', linewidth=0.7)
        plt.show()
        '''

    def testRun2(self):
        result = STGeoProcess(Diameter, self.building).run()
        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(len(self.building), len(result), 'Count rows')
        self.assertEqual(2 + len(self.building.columns), len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertAlmostEqual(95.58, row.diam_len, None, 'Check diam_len attr. value', 1e-2)

        '''
        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.building.plot(ax=basemap, color='lightgrey', edgecolor='black', linewidth=0.3)
        result.plot(ax=basemap, color='red', linewidth=0.7)
        plt.show()
        plt.close(fig)
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
