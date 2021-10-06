'''
Created on 31 mars 2021

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
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.grid.GridLib import GridLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class GridLibTest(unittest.TestCase):

    def setUp(self):
        self.gdf = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def testGrid(self):
        result = GridLib(self.gdf, dx=10, dy=None, encode=True).grid()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(72, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Test is a GeoDataFrame of Polygon')
            self.assertIn(row.gid, range(110), 'Test gid attribute value')
            self.assertEqual(4, len(ArrayCoding.decode(row.neighbors4)),
                             'Test neighbors4 attribute length')
            self.assertEqual(8, len(ArrayCoding.decode(row.neighbors8)),
                             'Test neighbors8 attribute length')

    def testIndoorGrid(self):
        result = GridLib(self.gdf, dx=10, dy=None, encode=True).indoorGrid()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(23, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Test is a GeoDataFrame of Polygon')
            self.assertIn(row.gid, range(110), 'Test gid attribute value')
            self.assertEqual(4, len(ArrayCoding.decode(row.neighbors4)),
                             'Test neighbors4 attribute length')
            self.assertEqual(8, len(ArrayCoding.decode(row.neighbors8)),
                             'Test neighbors8 attribute length')
            self.assertEqual(1, row.indoor, 'Test indoor attribute value')

    def testOutdoorGrid(self):
        result = GridLib(self.gdf, dx=10, dy=None, encode=True).outdoorGrid()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(49, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Test is a GeoDataFrame of Polygon')
            self.assertIn(row.gid, range(110), 'Test gid attribute value')
            self.assertEqual(4, len(ArrayCoding.decode(row.neighbors4)),
                             'Test neighbors4 attribute length')
            self.assertEqual(8, len(ArrayCoding.decode(row.neighbors8)),
                             'Test neighbors8 attribute length')
            self.assertEqual(0, row.indoor, 'Test indoor attribute value')

        '''
        import matplotlib.pyplot as plt
        from shapely.geometry import box
        bbox = GeoDataFrame([{'geometry': box(*self.gdf.total_bounds)}])
        _, basemap = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.gdf.plot(ax=basemap, color='lightgrey')
        bbox.boundary.plot(ax=basemap, color='blue', linewidth=0.2)
        result.boundary.plot(ax=basemap, color='red', linewidth=0.2)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
