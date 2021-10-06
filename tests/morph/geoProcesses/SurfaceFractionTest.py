'''
Created on 5 janv. 2021

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
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.STPolygonize import STPolygonize
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.morph.geoProcesses.SurfaceFraction import SurfaceFraction


class SurfaceFractionTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.roads = GeoDataFrameDemos.ensaNantesRoads()

    def tearDown(self):
        pass

    def testRun1(self):
        blocks = STPolygonize(self.roads).run()

        op = SurfaceFraction(self.buildings, buffDist=None)
        result = STGeoProcess(op, blocks).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(6, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertTrue(0.0 <= row['surf_ratio'] <= 1.0, 'Test "surf_ratio" attribute value')
        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        result.plot(ax=basemap, column='surf_ratio', legend=True, cmap='cividis')
        self.buildings.plot(ax=basemap, color='lightgrey')
        self.roads.plot(ax=basemap, color='black')
        plt.show()
        '''

    def testRun2(self):
        sensors = STGrid(self.buildings, 50, dy=None, indoor=False, intoPoint=True).run()

        op = SurfaceFraction(self.buildings, buffDist=30.0)
        result = STGeoProcess(op, sensors).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(15, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertTrue(0.0 <= row['surf_ratio'] <= 1.0, 'Test "surf_ratio" attribute value')
        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey')
        self.roads.plot(ax=basemap, color='black')
        result.plot(ax=basemap, column='surf_ratio', legend=True, cmap='cividis')
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
