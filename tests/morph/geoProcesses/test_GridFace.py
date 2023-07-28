'''
Created on 1 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from shapely.geometry import MultiPoint, MultiPolygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.morph.geoProcesses.GridFace import GridFace


class GridFaceTest(unittest.TestCase):

    def setUp(self):
        self.building = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def testRun1(self):
        op = GridFace(dx=3, dy=None, intoPoint=True)
        result = STGeoProcess(op, self.building).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(1 + len(self.building.columns), len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiPoint, 'Is a GeoDataFrame of MultiPoint')
            self.assertEqual(192, len(row.geometry.geoms), 'MultiPolygon of 192 Points')
            self.assertEqual(192, row.n_cells, 'Test n_cells attribute value')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.building.plot(ax=basemap, color='lightgrey', edgecolor='dimgrey', linewidth=0.2)
        result.plot(ax=basemap, color='red', linewidth=1.2)
        plt.show()
        '''

    def testRun2(self):
        op = GridFace(dx=3, dy=None, intoPoint=False)
        result = STGeoProcess(op, self.building).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(1 + len(self.building.columns), len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiPolygon, 'Is a GeoDataFrame of MultiPolygon')
            self.assertEqual(192, len(row.geometry.geoms), 'MultiPolygon of 192 Polygons')
            self.assertEqual(192, row.n_cells, 'Test n_cells attribute value')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.building.plot(ax=basemap, color='lightgrey', edgecolor='dimgrey', linewidth=0.2)
        result.boundary.plot(ax=basemap, color='red', linewidth=1.2)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
