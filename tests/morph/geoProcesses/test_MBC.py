'''
Created on 15 dec. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from numpy import pi
from shapely.geometry import MultiPoint, Polygon

import geopandas as gpd
from t4gpd.morph.geoProcesses.MBC import MBC
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class MBCTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun(self):
        inputGeom = MultiPoint([(0, 0), (5, 4), (7, 3), (6, 2)])
        inputGdf = GeoDataFrame([{'geometry': inputGeom}])

        result = STGeoProcess(MBC, inputGdf).run()

        self.assertIsInstance(result, gpd.GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertAlmostEqual(pi * row['radius'] * row['radius'], row.geometry.area, 0, 'Area test')
            self.assertIsInstance(row['radius'], float, 'Radius test')
            self.assertIsInstance(row['center'], str, 'Center test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.boundary.plot(ax=basemap, color='grey')
        inputGdf.plot(ax=basemap, color='red')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testRun']
    unittest.main()
