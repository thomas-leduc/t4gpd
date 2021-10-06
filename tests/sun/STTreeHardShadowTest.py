'''
Created on 27 aug. 2020

@author: tleduc
'''
from datetime import datetime, timedelta
import unittest

from geopandas import clip
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.sun.STTreeHardShadow import STTreeHardShadow


class STTreeHardShadowTest(unittest.TestCase):

    def setUp(self):
        self.trees = GeoDataFrameDemos.districtGraslinInNantesTrees()
        
        roi = GeoDataFrameDemos.coursCambronneInNantes()
        self.trees = clip(self.trees, roi)
        # self.trees = self.trees[self.trees.osm_id == 1961183678]

        ids = ['1937451436', '1937451458', '1937451469', '1937451497',
               '1937451525', '1937451548', '1937451563', '1937451582']

        h1, a1 = 15.0, 5.0
        h2, a2 = 9.0, 3.0
        self.trees['h_arbre'] = self.trees.osm_id.apply(lambda _id: h1 if _id in ids else h2)
        self.trees['r_houppier'] = self.trees.osm_id.apply(lambda _id: a1 if _id in ids else a2)

        self.datetimes = [datetime(2020, 7, 21, 9), datetime(2020, 7, 21, 15), timedelta(hours=3)] 
        self.datetimes = DatetimeLib.generate(self.datetimes)

    def tearDown(self):
        pass

    def testRun(self):
        result = STTreeHardShadow(
            self.trees, self.datetimes, treeHeightFieldname='h_arbre',
            treeCrownRadiusFieldname='r_houppier', altitudeOfShadowPlane=0.0,
            aggregate=False, tz=None, model='pysolar', npoints=32).run()

        datetimes = [str(dt) for dt in list(self.datetimes.values())[0]]

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(3 * len(self.trees), len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertIn(row.datetime, datetimes, 'Datetime test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.plot(ax=basemap, column='datetime', alpha=0.3, legend=True)
        self.trees.plot(ax=basemap, color='red')
        plt.show()
        # result.to_file('/tmp/x.shp')
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
