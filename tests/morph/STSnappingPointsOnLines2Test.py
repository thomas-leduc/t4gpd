'''
Created on 24 sept. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point
from t4gpd.io.CSVReader import CSVReader
from t4gpd.morph.STSnappingPointsOnLines2 import STSnappingPointsOnLines2

from t4gpd.commons.TestUtils import TestUtils


class STSnappingPointsOnLines2Test(unittest.TestCase):

    def setUp(self):
        self.lines1 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_path.shp').to_crs('EPSG:2154')
        self.points1 = CSVReader(
            TestUtils.getDataSetFilename('../data', 'jardin_extraordinaire_path.csv'),
            'longitude_Lamb93', 'latitude_Lamb93', ';', srcEpsgCode='EPSG:2154',
            decimalSep=',').run()
        self.waypoints1 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_waypoints.shp').to_crs('EPSG:2154')

        '''
        self.points1 = CSVReader('../data/jardin_extraordinaire_path_wgs84.csv', 'longitude_WGS84',
                                'latitude_WGS84', ';', srcEpsgCode='EPSG:3857',
                                decimalSep=',').run().to_crs('EPSG:2154')
        '''
        self.lines2 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_path3.shp').to_crs('EPSG:2154')
        self.points2 = CSVReader(
            TestUtils.getDataSetFilename('../data', 'jardin_extraordinaire_path3.csv'),
            'longitude_Lamb93', 'latitude_Lamb93', ';', srcEpsgCode='EPSG:2154',
            decimalSep=',').run()
        self.waypoints2 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_waypoints3.shp').to_crs('EPSG:2154')

        self.lines3 = TestUtils.loadDataSet('../data', 'theatre_graslin_path1.shp').to_crs('EPSG:2154')
        self.points3 = CSVReader(
            TestUtils.getDataSetFilename('../data', 'theatre_graslin_path1.csv'),
            'longitude_Lamb93', 'latitude_Lamb93', ';', srcEpsgCode='EPSG:2154',
            decimalSep=',').run()
        self.waypoints3 = TestUtils.loadDataSet('../data', 'theatre_graslin_waypoints1.shp').to_crs('EPSG:2154')

        self.lines4 = TestUtils.loadDataSet('../data', 'quai_des_plantes_path1.shp').to_crs('EPSG:2154')
        self.points4 = CSVReader(
            TestUtils.getDataSetFilename('../data', 'quai_des_plantes_path1.csv'),
            'longitude_Lamb93', 'latitude_Lamb93', ';', srcEpsgCode='EPSG:2154',
            decimalSep=',').run()
        self.waypoints4 = TestUtils.loadDataSet('../data', 'quai_des_plantes_waypoints1.shp').to_crs('EPSG:2154')

        self.lines5 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_path5.shp').to_crs('EPSG:2154')
        self.points5 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_points5.shp').to_crs('EPSG:2154')
        self.waypoints5 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_waypoints5.shp').to_crs('EPSG:2154')

    def tearDown(self):
        pass

    def testRun1(self):
        result = STSnappingPointsOnLines2(self.points1, self.lines1, self.waypoints1,
                                          stepCountFieldname='STEP.COUNT',
                                          tagName='TagName', wayPointsIdFieldname='id').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(154, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines1.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 <= row['STEP.COUNT'] <= 153, 'STEP.COUNT field test')
            self.assertTrue(0 < row['dist_to_l'] < 7.9, 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength, 'curv_absc field test')

    def testRun2(self):
        result = STSnappingPointsOnLines2(self.points2, self.lines2, self.waypoints2,
                                          stepCountFieldname='STEP.COUNT',
                                          tagName='TagName', wayPointsIdFieldname='id').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(109, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines3.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 <= row['STEP.COUNT'] <= 109, 'STEP.COUNT field test')
            self.assertTrue(0 < row['dist_to_l'] < 7.9, 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength + 1e-3, 'curv_absc field test')

    def testRun3(self):
        result = STSnappingPointsOnLines2(self.points3, self.lines3, self.waypoints3,
                                          stepCountFieldname='STEP.COUNT',
                                          tagName='TagName', wayPointsIdFieldname='id').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(166, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines3.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 <= row['STEP.COUNT'] <= 166, 'STEP.COUNT field test')
            self.assertTrue(0 < row['dist_to_l'] < 7.9, 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength + 1e-3, 'curv_absc field test')

    def testRun4(self):
        result = STSnappingPointsOnLines2(self.points4, self.lines4, self.waypoints4,
                                          stepCountFieldname='STEP.COUNT',
                                          tagName='TagName', wayPointsIdFieldname='id').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(176, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines3.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 <= row['STEP.COUNT'] <= 176, 'STEP.COUNT field test')
            self.assertTrue(0 < row['dist_to_l'] < 7.9, 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength + 1e-3, 'curv_absc field test')

    def testRun5(self):
        result = STSnappingPointsOnLines2(self.points5, self.lines5, self.waypoints5,
                                          stepCountFieldname='STEP.COUNT',
                                          tagName='TagName', wayPointsIdFieldname='id').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(129, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines3.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 <= row['STEP.COUNT'] <= 129, 'STEP.COUNT field test')
            self.assertTrue(0 < row['dist_to_l'] < 3.5, 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength + 1e-3, 'curv_absc field test')

        '''
        import matplotlib.pyplot as plt
        basemap = self.lines3.plot(color='lightgrey', linewidth=1.3)
        self.points3.plot(ax=basemap, color='green', marker='+', markersize=6)
        self.waypoints3.plot(ax=basemap, color='red', marker='*', markersize=16)
        result.plot(ax=basemap, color='blue', marker='*', markersize=12)
        plt.show()
        '''
        # self.points.to_file('/tmp/yyy.shp')
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
