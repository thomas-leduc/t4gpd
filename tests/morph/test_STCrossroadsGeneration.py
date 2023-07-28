'''
Created on 17 juin 2020

@author: tleduc
'''
import unittest

import pyproj
from shapely.geometry import Polygon

import geopandas as gpd
from t4gpd.morph.STCrossroadsGeneration import STCrossroadsGeneration


class STCrossroadsGenerationTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun4Branches(self):
        result = STCrossroadsGeneration(nbranchs=4, length=100.0, width=10.0,
                                          mirror=False, withBranchs=True, withSectors=True,
                                          crs='EPSG:2154', magnitude=2.5).run()

        self.assertIsInstance(result, gpd.GeoDataFrame, 'Is a GeoDataFrame')

        expectedCrs = pyproj.CRS('EPSG:2154')
        self.assertEqual(result.crs, expectedCrs, 'Verify CRS')
        self.assertEqual(13, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertEqual(4, row['model'], 'Test "model" attributes values')

    def testRun8Branches(self):
        result = STCrossroadsGeneration(nbranchs=8, length=100.0, width=10.0,
                                          mirror=False, withBranchs=True, withSectors=True,
                                          crs='EPSG:2154', magnitude=2.5).run()

        self.assertIsInstance(result, gpd.GeoDataFrame, 'Is a GeoDataFrame')

        expectedCrs = pyproj.CRS('EPSG:2154')
        self.assertEqual(result.crs, expectedCrs, 'Verify CRS')
        self.assertEqual(78, len(result), 'Count rows (1)')
        self.assertEqual(6, len(result.columns), 'Count columns')

        self.assertEqual(65, len(result[result.model == 8]), 'Count rows (2)')
        self.assertEqual(13, len(result[result.model == 4]), 'Count rows (3)')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertIn(row['model'], (4, 8), 'Test "model" attributes values')

        '''
        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(8.26, 8.26))  # 21 cm ~ 8.26 inches
        result.plot(ax=basemap, column='model', cmap='bwr')
        result.apply(lambda x: basemap.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color='black', size=11, ha='center'), axis=1)
        basemap.axis('off')
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
