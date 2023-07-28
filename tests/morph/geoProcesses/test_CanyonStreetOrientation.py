'''
Created on 7 oct. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.CanyonStreetOrientation import CanyonStreetOrientation
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class CanyonStreetOrientationTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoint = GeoDataFrame(
            [{'geometry': Point((355217, 6688432))}], crs=self.buildings.crs)

    def tearDown(self):
        pass

    def testRun(self):
        magnitude = 10.0
        op = CanyonStreetOrientation(self.buildings, magnitude)
        result = STGeoProcess(op, self.viewpoint).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            self.assertAlmostEqual(2 * magnitude, row.geometry.length, 3, 'Test LineString length')
            self.assertTrue(0 <= row['azimuth'] < 180, 'Test azimuth attribute value')

        '''
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8.26, 8.26))  # 21 cm ~ 8.26 inches
        basemap = fig.subplots()
        self.buildings.plot(ax=basemap, color='lightgrey')
        self.viewpoint.plot(ax=basemap, color='red')
        result.plot(ax=basemap)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
