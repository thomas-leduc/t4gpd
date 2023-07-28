'''
Created on 18 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
import pyproj
from shapely.geometry import Polygon
from t4gpd.commons.BoundingBox import BoundingBox
from t4gpd.io.STLoadAndClip import STLoadAndClip

from t4gpd.commons.TestUtils import TestUtils


class STLoadAndClipTest(unittest.TestCase):

    def setUp(self):
        self.inputFilename = TestUtils.getDataSetFilename('tests/data', 'ensa_nantes.shp')

    def tearDown(self):
        pass

    def testRun(self):
        roi = (355187.4, 6688430.0, 355309.7, 6688544.4)
        result = STLoadAndClip(self.inputFilename, roi).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        expectedCrs = pyproj.CRS('EPSG:2154')
        self.assertEqual(result.crs, expectedCrs, 'Verify CRS')
        self.assertEqual(7, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        roi = BoundingBox(roi).asPolygon()
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertTrue(row.geometry.within(roi), 'Test if polygons within RoI')
        '''
        import matplotlib.pyplot as plt
        result.plot()
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
