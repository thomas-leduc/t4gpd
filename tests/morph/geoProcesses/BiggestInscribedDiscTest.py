'''
Created on 18 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from numpy import pi
from shapely.geometry import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.geoProcesses.BiggestInscribedDisc import BiggestInscribedDisc
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class BiggestInscribedDiscTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.sensors = STGrid(self.buildings, 50, dy=None, indoor=False, intoPoint=True).run()

    def tearDown(self):
        self.buildings = None
        self.sensors = None

    def testRun(self):
        disc = BiggestInscribedDisc(self.buildings)
        result = STGeoProcess(disc, self.sensors).run()
        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(15, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')

            expectedSurf = pi * (row['insc_diam'] / 2.0) ** 2
            ratioToTest = (expectedSurf - row.geometry.area) / expectedSurf
            self.assertTrue(0.01 > ratioToTest, 'Areas test')

        '''
        import matplotlib.pyplot as plt
        my_map_base = self.buildings.boundary.plot(edgecolor='black', linewidth=0.3)
        self.sensors.plot(ax=my_map_base, marker='+', markersize=120)
        result.boundary.plot(ax=my_map_base, edgecolor='red', linewidth=0.3)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
