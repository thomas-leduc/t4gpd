'''
Created on 16 juin 2020

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
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.MABR import MABR
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class MABRTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        self.buildings = None

    def testRun1(self):
        result = STGeoProcess(MABR, self.buildings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(44, len(result), '44 rows')
        self.assertEqual(3, len(result.columns), '3 columns')

        shapeAreas = self.buildings.area
        inputShapes = self.buildings.geometry
        for i, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertLessEqual(shapeAreas[i], row.geometry.area, 'Areas test')
            self.assertTrue(inputShapes[i].within(row.geometry.buffer(0.01)), 'Within test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.boundary.plot(ax=basemap, color='grey')
        self.buildings.plot(ax=basemap, color='red')
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')

    def testRun2(self):
        inputGeom = Polygon([(1, 0), (3, 0), (4, 1), (3, 1.9), (1, 1.9), (0, 1), (1, 0)])
        inputGdf = GeoDataFrame([{'geometry': inputGeom}])

        result = STGeoProcess(MABR, inputGdf).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(1, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            rect = row['geometry']

            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertEqual(7.6, rect.area, 'Area test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.boundary.plot(ax=basemap, color='grey')
        inputGdf.plot(ax=basemap, color='red')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
