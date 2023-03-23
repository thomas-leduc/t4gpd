'''
Created on 19 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STDilationErosion import STDilationErosion


class STDilationErosionTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        self.buildings = None

    def testRun(self):
        squares, streets = STDilationErosion(self.buildings, buffDist=10.0).run()

        self.assertIsInstance(squares, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(2, len(squares), 'Count rows')
        self.assertEqual(2, len(squares.columns), 'Count columns')
        for _, row in squares.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')

        self.assertIsInstance(streets, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(28, len(streets), 'Count rows')
        self.assertEqual(2, len(streets.columns), 'Count columns')
        for _, row in streets.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')

        '''
        import matplotlib.pyplot as plt
        my_map_base = self.buildings.plot(color='lightgrey', edgecolor='black', linewidth=0.3)
        squares.plot(ax=my_map_base, color='white', edgecolor='green', linewidth=0.3, hatch='||')
        streets.plot(ax=my_map_base, color='white', edgecolor='red', linewidth=0.3, hatch='--')
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
