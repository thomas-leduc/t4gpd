'''
Created on 24 sept. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from pandas import read_csv
from shapely.geometry import Point
from t4gpd.commons.TestUtils import TestUtils
from t4gpd.io.CSVReader import CSVReader
from t4gpd.morph.STSnappingPointsOnLines2 import STSnappingPointsOnLines2


class STSnappingPointsOnLines2Test(unittest.TestCase):

    def setUp(self):
        self.lines1 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_path.shp').to_crs('EPSG:2154')
        self.points1 = CSVReader(
            TestUtils.getDataSetFilename('../data', 'jardin_extraordinaire_path.csv'),
            'longitude_Lamb93', 'latitude_Lamb93', ';', srcEpsgCode='EPSG:2154',
            decimalSep=',').run()
        self.waypoints1 = TestUtils.loadDataSet('../data', 'jardin_extraordinaire_waypoints.shp').to_crs('EPSG:2154')

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

        self.lines6 = TestUtils.loadDataSet('../data', 'quai_des_plantes_path2.gpkg',
                                            driver='GPKG').to_crs('EPSG:2154')
        self.points6 = read_csv(TestUtils.getDataSetFilename('../data', 'quai_des_plantes_points2.csv'))
        self.waypoints6 = TestUtils.loadDataSet('../data', 'quai_des_plantes_waypoints2.gpkg',
                                                driver='GPKG').to_crs('EPSG:2154')

        self.lines7 = TestUtils.loadDataSet('../data', 'la_defense_pathway.gpkg',
                                            driver='GPKG').to_crs('EPSG:2154')
        self.points7 = read_csv(TestUtils.getDataSetFilename('../data', 'la_defense_measurepts.csv'))
        self.waypoints7 = TestUtils.loadDataSet('../data', 'la_defense_waypoints.gpkg',
                                                driver='GPKG').to_crs('EPSG:2154')

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

        pathLength = sum(self.lines2.length)
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

        pathLength = sum(self.lines4.length)
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

        pathLength = sum(self.lines5.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 <= row['STEP.COUNT'] <= 129, 'STEP.COUNT field test')
            self.assertTrue(0 < row['dist_to_l'] < 3.5, 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength + 1e-3, 'curv_absc field test')

    def testRun6(self):
        result = STSnappingPointsOnLines2(self.points6, self.lines6, self.waypoints6,
                                          stepCountFieldname='step_count',
                                          tagName='TagName', wayPointsIdFieldname='id').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(175, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines6.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(1 <= row['step_count'] <= 176, 'STEP.COUNT field test')
            self.assertIsNone(row['dist_to_l'], 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength + 1e-3, 'curv_absc field test')

    def testRun7(self):
        result = STSnappingPointsOnLines2(self.points7, self.lines7, self.waypoints7,
                                          stepCountFieldname='step_count',
                                          tagName='TagName', wayPointsIdFieldname='id').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(118, len(result), 'Count rows')
        self.assertEqual(19, len(result.columns), 'Count columns')

        pathLength = sum(self.lines7.length)
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0 <= row['step_count'] <= 117, 'STEP.COUNT field test')
            self.assertIsNone(row['dist_to_l'], 'dist_to_l field test')
            self.assertTrue(0 <= row['curv_absc'] <= pathLength + 1e-3, 'curv_absc field test')

        '''
        import matplotlib.pyplot as plt
        basemap = self.lines7.plot(color='lightgrey', linewidth=1.3)
        # self.points7.plot(ax=basemap, color='green', marker='+', markersize=6)
        self.waypoints7.plot(ax=basemap, color='red', marker='*', markersize=16)
        result.plot(ax=basemap, color='blue', marker='*', markersize=12)
        # result.to_file('../data/xxx.gpkg', driver='GPKG')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
