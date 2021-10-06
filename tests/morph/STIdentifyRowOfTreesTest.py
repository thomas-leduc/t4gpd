'''
Created on 17 sept. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STIdentifyRowOfTrees import STIdentifyRowOfTrees
from t4gpd.morph.geoProcesses.IdentifyTheClosestPolyline import IdentifyTheClosestPolyline
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class STIdentifyRowOfTreesTest(unittest.TestCase):

    def setUp(self):
        self.trees1 = GeoDataFrameDemos.ensaNantesTrees()
        self.roads1 = GeoDataFrameDemos.ensaNantesRoads()

    def tearDown(self):
        pass

    def testRun(self):
        op = IdentifyTheClosestPolyline(self.roads1, 'ID')
        trees2 = STGeoProcess(op, self.trees1).run()
        
        result = STIdentifyRowOfTrees(trees2, 'MI_PRINX').run()
        print(result.columns)
        
        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(12, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            currGeom = row.geometry
            self.assertIsInstance(currGeom, LineString, 'Is a GeoDataFrame of LineString')
        
        '''
        import matplotlib.pyplot as plt
        basemap = self.roads1.plot(edgecolor='black', linewidth=0.3)
        result.plot(ax=basemap, edgecolor='red', linewidth=2.3)
        trees2.plot(ax=basemap, color='green', markersize=33)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
