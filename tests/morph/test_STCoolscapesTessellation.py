'''
Created on 2 oct. 2020

@author: tleduc
'''
import unittest

from shapely.geometry import Polygon
from t4gpd.morph.STCoolscapesTessellation import STCoolscapesTessellation

import geopandas as gpd
from t4gpd.commons.TestUtils import TestUtils


class STCoolscapesTessellationTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun1(self):
        # lines = gpd.read_file('tests/data/jardin_extraordinaire_path.shp').to_crs('EPSG:2154')
        lines = TestUtils.loadDataSet('tests/data', 'jardin_extraordinaire_path.shp').to_crs('EPSG:2154')
        sampleDist, buffDist = 3.0, 1.0 
        tessell = STCoolscapesTessellation(lines, sampleDist, buffDist).run()

        self.assertIsInstance(tessell, gpd.GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(49, len(tessell), 'Count rows')
        self.assertEqual(4, len(tessell.columns), 'Count columns')
        for _, row in tessell.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')
            self.assertTrue(row['curv_abs_0'] < row['curv_abs_1'],
                            'Test curv_abs_{0,1} attributes')

        '''
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8.26, 8.26))  # 21 cm ~ 8.26 inches
        basemap = fig.subplots()
        lines.plot(ax=basemap, color='black', linewidth=1.3)
        tessell.boundary.plot(ax=basemap, color='red')
        tessell.apply(lambda x: basemap.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color='black', size=12, ha='center'), axis=1);
        plt.show()
        '''

    def testRun2(self):
        # lines = gpd.read_file('tests/data/jardin_extraordinaire_path5.shp').to_crs('EPSG:2154')
        lines = TestUtils.loadDataSet('tests/data', 'jardin_extraordinaire_path5.shp').to_crs('EPSG:2154')
        sampleDist, buffDist = 3.0, 1.0 
        tessell = STCoolscapesTessellation(lines, sampleDist, buffDist).run()

        self.assertIsInstance(tessell, gpd.GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(46, len(tessell), 'Count rows')
        self.assertEqual(4, len(tessell.columns), 'Count columns')
        for _, row in tessell.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')
            self.assertTrue(row['curv_abs_0'] < row['curv_abs_1'],
                            'Test curv_abs_{0,1} attributes')

        '''
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8.26, 8.26))  # 21 cm ~ 8.26 inches
        basemap = fig.subplots()
        lines.plot(ax=basemap, color='black', linewidth=1.3)
        tessell.boundary.plot(ax=basemap, color='red')
        tessell.apply(lambda x: basemap.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color='black', size=10, ha='center'), axis=1);
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
