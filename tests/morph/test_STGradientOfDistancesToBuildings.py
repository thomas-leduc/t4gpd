'''
Created on 6 oct. 2020

@author: tleduc

Copyright 2020 Thomas Leduc

This file is part of t4gpd.

t4gpd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

t4gpd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with t4gpd.  If not, see <https://www.gnu.org/licenses/>.
'''
from math import isnan
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STToRoadsSections import STToRoadsSections
from t4gpd.morph.STGradientOfDistancesToBuildings import STGradientOfDistancesToBuildings


class STGradientOfDistancesToBuildingsTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        _lines = GeoDataFrameDemos.ensaNantesRoads()
        self.lines = STToRoadsSections(_lines, withoutCulDeSac=True).run()

    def tearDown(self):
        pass

    def testRun(self):
        # pathidFieldname='ID'
        result1, result2, result3 = STGradientOfDistancesToBuildings(
            self.lines, self.buildings, sampleDist=10.0, threshold=0.05, order=1).run()

        self.assertIsInstance(result1, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(154, len(result1), 'Count rows')
        self.assertEqual(9, len(result1.columns), 'Count columns')

        for _, row in result1.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertIn(row['area_type'], ('canyon', 'square'), 'Test area_type" attribute values')
            self.assertLessEqual(0 , row['curv_absc'], 'Test "curv_absc" attribute values (1)')
            self.assertLessEqual(0 , row['r'], 'Test "r" attribute values')
            if 0 == row['nodeid']:
                self.assertEqual(0 , row['curv_absc'], 'Test "curv_absc" attribute values (2)')
                self.assertTrue(isnan(row['r_deriv2']), 'Test "r_deriv2" attribute values')
                self.assertTrue(isnan(row['r_deriv3']), 'Test "r_deriv3" attribute values')

        self.assertIsInstance(result2, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(154, len(result2), 'Count rows')
        self.assertEqual(9, len(result2.columns), 'Count columns')

        for _, row in result2.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            self.assertIn(row['area_type'], ('canyon', 'square'), 'Test area_type" attribute values')
            self.assertLessEqual(0 , row['curv_absc'], 'Test "curv_absc" attribute values (1)')
            self.assertLessEqual(0 , row['r'], 'Test "r" attribute values')
            if 0 == row['nodeid']:
                self.assertEqual(0 , row['curv_absc'], 'Test "curv_absc" attribute values (2)')
                self.assertTrue(isnan(row['r_deriv2']), 'Test "r_deriv2" attribute values')
                self.assertTrue(isnan(row['r_deriv3']), 'Test "r_deriv3" attribute values')

        self.assertIsInstance(result3, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(53, len(result3), 'Count rows')
        self.assertEqual(3, len(result3.columns), 'Count columns')

        for _, row in result3.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            self.assertIn(row['area_type'], ('canyon', 'square'), 'Test area_type" attribute values')

        '''
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8.26, 8.26))  # 21 cm ~ 8.26 inches
        basemap = fig.subplots()
        self.buildings.plot(ax=basemap, color='lightgrey')
        self.lines.plot(ax=basemap, color='black', linewidth=1.3)
        result1.plot(ax=basemap, column='area_type', cmap='bwr', legend=True)
        result2.plot(ax=basemap, column='area_type', cmap='bwr')
        result3.plot(ax=basemap, column='area_type', cmap='bwr')
        plt.show()
        '''
        # result1.to_file('/tmp/xx1.shp')
        # result2.to_file('/tmp/xx2.shp')
        # result3.to_file('/tmp/xx3.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
