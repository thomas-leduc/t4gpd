'''
Created on 27 aug. 2020

@author: tleduc
'''
from datetime import datetime, timedelta
import unittest

from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.sun.STHardShadow import STHardShadow


class STHardShadowTest(unittest.TestCase):

    def setUp(self):
        # self.buildings = GeoDataFrameDemos.districtGraslinInNantesBuildings()
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        # self.buildings = GeoDataFrameDemos.singleBuildingInNantes()
        self.datetimes = [datetime(2020, 7, 21, 9), datetime(2020, 7, 21, 15), timedelta(hours=3)] 
        self.datetimes = DatetimeLib.generate(self.datetimes)
        
    def tearDown(self):
        pass

    def testRun1(self):
        result = STHardShadow(
            self.buildings, self.datetimes, occludersElevationFieldname='HAUTEUR',
            altitudeOfShadowPlane=0, aggregate=True, tz=None, model='pysolar').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(3, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        datetimes = [str(dt) for dt in list(self.datetimes.values())[0]]
        for _, shadowRow in result.iterrows():
            self.assertIn(shadowRow.datetime, datetimes, 'Datetime test')

            shadowGeom = shadowRow.geometry
            for _, buildingRow in self.buildings.iterrows():
                buildingGeom = buildingRow.geometry
                self.assertTrue(buildingGeom.within(shadowGeom), 'Within test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.plot(ax=basemap, column='datetime', alpha=0.3, legend=True)
        self.buildings.boundary.plot(ax=basemap, color='red')
        plt.show()
        # result.to_file('/tmp/x.shp')
        '''

    def testRun2(self):
        result = STHardShadow(
            self.buildings, self.datetimes, occludersElevationFieldname='HAUTEUR',
            altitudeOfShadowPlane=0, aggregate=False, tz=None, model='pysolar').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(132, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')

        datetimes = [str(dt) for dt in list(self.datetimes.values())[0]]
        for _, shadowRow in result.iterrows():
            self.assertIn(shadowRow.datetime, datetimes, 'Datetime test')

            shadowGeom = shadowRow.geometry
            shadowId = shadowRow.ID
            for _, buildingRow in self.buildings[self.buildings.ID == shadowId].iterrows():
                buildingGeom = buildingRow.geometry
                self.assertTrue(buildingGeom.within(shadowGeom.buffer(0.001)), 'Within test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.plot(ax=basemap, column='datetime', alpha=0.3, legend=True)
        self.buildings.boundary.plot(ax=basemap, color='red')
        plt.show()
        # result.to_file('/tmp/x.shp')
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
