'''
Created on 30 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STClip import STClip


class STClipTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        pass

    def testRun(self):
        result = STClip(self.buildings, [355160.6, 6688350.0, 355275.1, 6688476.7]).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(4, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        inputShapes = dict()
        for _, row in self.buildings.iterrows():
            currGeom = row.geometry
            inputShapes[row['ID']] = { 'area': currGeom.area, 'geometry': currGeom.buffer(0.001) }

        for _, row in result.iterrows():
            currId = row['ID']
            currGeom = row.geometry
            currArea = currGeom.area

            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertLessEqual(currArea, inputShapes[currId]['area'], 'Areas test')
            self.assertTrue(currGeom.within(inputShapes[currId]['geometry']), 'Within test')

        '''
        import matplotlib.pyplot as plt
        basemap = self.buildings.plot(color='lightgrey', edgecolor='black', linewidth=0.3)
        result.plot(ax=basemap, color='red')
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
