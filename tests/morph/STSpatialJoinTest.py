'''
Created on 22 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point, Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STSpatialJoin import STSpatialJoin


class STSpatialJoinTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.sensors = STGrid(self.buildings, 50, dy=None, indoor='both', intoPoint=True).run()

    def tearDown(self):
        self.buildings = None
        self.sensors = None

    def testRun1(self):
        for op in ['intersects', 'within']:
            result = STSpatialJoin(self.sensors, op, self.buildings).run()

            self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
            self.assertEqual(10, len(result), 'Count rows')
            self.assertEqual(7, len(result.columns), 'Count columns')

            for _, row in result.iterrows():
                self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')

    def testRun2(self):
        for op in ['contains', 'contains_centroid', 'intersects']:
            result = STSpatialJoin(self.buildings, op, self.sensors).run()

            self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
            self.assertEqual(10, len(result), 'Count rows')
            self.assertEqual(7, len(result.columns), 'Count columns')
    
            for _, row in result.iterrows():
                self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')

        '''
        import matplotlib.pyplot as plt
        my_map_base = self.buildings.plot(color='lightgrey', edgecolor='black', linewidth=0.3)
        result.plot(ax=my_map_base, color='red')
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
