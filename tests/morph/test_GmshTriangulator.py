'''
Created on 17 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.GmshTriangulator import GmshTriangulator


class GmshTriangulatorTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        self.buildings = None

    def testRun(self):
        result = GmshTriangulator(self.buildings, characteristicLength=10.0).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertLess(1000, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertEqual(0, len(row.geometry.interiors), 'Is a GeoDataFrame of no-hole polygons')
            self.assertEqual(4, len(row.geometry.exterior.coords), 'Is a GeoDataFrame of triangles')

        '''
        import matplotlib.pyplot as plt
        result.plot()
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
