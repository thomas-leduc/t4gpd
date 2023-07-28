'''
Created on 24 sept. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point
from t4gpd.io.CSVReader import CSVReader
from t4gpd.morph.STSnappingPointsOnLines import STSnappingPointsOnLines

from t4gpd.commons.TestUtils import TestUtils


class STSnappingPointsOnLinesTest(unittest.TestCase):

    def setUp(self):
        self.lines = TestUtils.loadDataSet('tests/data', 'jardin_extraordinaire_path.shp').to_crs('EPSG:2154')

        self.points = CSVReader(
            TestUtils.getDataSetFilename('tests/data', 'jardin_extraordinaire_path.csv'),
            'longitude_Lamb93', 'latitude_Lamb93', ';', srcEpsgCode='EPSG:2154', decimalSep=',').run()

        '''
        self.points = CSVReader('tests/data/jardin_extraordinaire_path_wgs84.csv', 'longitude_WGS84',
                                'latitude_WGS84', ';', srcEpsgCode='EPSG:3857',
                                decimalSep=',').run().to_crs('EPSG:2154')
        '''

    def tearDown(self):
        pass

    def testRun(self):
        result = STSnappingPointsOnLines(self.points, self.lines,
                                         stepCountFieldname='STEP.COUNT').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(154, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 < row['dist_to_l'] < 7.2, 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength, 'curv_absc field test')

        '''
        import matplotlib.pyplot as plt
        basemap = self.lines.plot(color='lightgrey', linewidth=1.3)
        self.points.plot(ax=basemap, color='green', marker='+', markersize=6)
        result.plot(ax=basemap, color='red', marker='*', markersize=12)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
