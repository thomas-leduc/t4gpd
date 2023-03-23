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

from geopandas import GeoDataFrame, overlay
from numpy import ndarray
from shapely.geometry import Polygon
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.grid.GridLib import GridLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STSquaredBBox import STSquaredBBox


class GridLibTest(unittest.TestCase):

    def setUp(self):
        self.building = GeoDataFrameDemos.singleBuildingInNantes()
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()

    def tearDown(self):
        pass

    def testGrid(self):
        result = GridLib(self.building, dx=10, dy=None, encode=True).grid()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(72, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Test is a GeoDataFrame of Polygon')
            self.assertIn(row.gid, range(110), 'Test gid attribute value')
            self.assertEqual(4, len(ArrayCoding.decode(row.neighbors4)),
                             'Test neighbors4 attribute length')
            self.assertEqual(8, len(ArrayCoding.decode(row.neighbors8)),
                             'Test neighbors8 attribute length')

    def testIndoorGrid(self):
        result = GridLib(self.building, dx=10, dy=None, encode=True).indoorGrid()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(23, len(result), 'Count rows')
        self.assertEqual(7, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Test is a GeoDataFrame of Polygon')
            self.assertIn(row.gid, range(110), 'Test gid attribute value')
            self.assertEqual(4, len(ArrayCoding.decode(row.neighbors4)),
                             'Test neighbors4 attribute length')
            self.assertEqual(8, len(ArrayCoding.decode(row.neighbors8)),
                             'Test neighbors8 attribute length')
            self.assertEqual(1, row.indoor, 'Test indoor attribute value')

    def testOutdoorGrid(self):
        result = GridLib(self.building, dx=10, dy=None, encode=True).outdoorGrid()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(49, len(result), 'Count rows')
        self.assertEqual(7, len(result.columns), 'Count columns')

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
        bbox = GeoDataFrame([{'geometry': box(*self.building.total_bounds)}])
        _, basemap = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.building.plot(ax=basemap, color='lightgrey')
        bbox.boundary.plot(ax=basemap, color='blue', linewidth=0.2)
        result.boundary.plot(ax=basemap, color='red', linewidth=0.2)
        plt.show()
        '''

    def testGradient(self):
        roi = STSquaredBBox(self.buildings, buffDist=-100.0).run()
        sbuildings = overlay(self.buildings, roi, how='intersection')
        grid = GridLib(sbuildings, dx=10, dy=None, encode=True).outdoorGrid()
        # grid = GridLib(sbuildings, dx=10, dy=None, encode=True).grid()

        scalField = GridLib.fromGridToNumpyArray(grid, 'gid')
        self.assertIsInstance(scalField, ndarray, 'Is a NumPy array')

        scalField = GridLib.fromNumpyArrayToGrid(scalField, grid, 'Z_value')
        self.assertIsInstance(scalField, GeoDataFrame, 'Is a GeoDataFrame')

        grad = GridLib.gradient(scalField, "Z_value", rowFieldname='row',
                                colFieldname='column', magn=7.0)
        self.assertIsInstance(grad, GeoDataFrame, 'Is a GeoDataFrame')

        '''
        import matplotlib.pyplot as plt
        minx, miny, maxx, maxy = roi.buffer(5.0).total_bounds
        
        _, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.buildings.plot(ax=ax, color='lightgrey')
        grid.boundary.plot(ax=ax, color='blue', linewidth=0.2)
        grid.apply(lambda x: ax.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color='blue', size=12, ha='center'), axis=1);

        scalField.plot(ax=ax, column="Z_value", alpha=0.5, legend=True)
        grad.plot(ax=ax, color='green', linewidth=2.5)

        ax.axis([minx, maxx, miny, maxy])
        plt.show()
        '''

    def testDivergence(self):
        roi = STSquaredBBox(self.buildings, buffDist=-100.0).run()
        sbuildings = overlay(self.buildings, roi, how='intersection')
        grid = GridLib(sbuildings, dx=10, dy=None, encode=True).outdoorGrid()
        # grid = GridLib(sbuildings, dx=10, dy=None, encode=True).grid()

        scalField = GridLib.fromGridToNumpyArray(grid, 'gid')
        self.assertIsInstance(scalField, ndarray, 'Is a NumPy array')

        scalField = GridLib.fromNumpyArrayToGrid(scalField, grid, 'Z_value')
        self.assertIsInstance(scalField, GeoDataFrame, 'Is a GeoDataFrame')

        div = GridLib.divergence(scalField, "Z_value", rowFieldname='row',
                                colFieldname='column', magn=7.0)
        self.assertIsInstance(div, GeoDataFrame, 'Is a GeoDataFrame')

        '''
        import matplotlib.pyplot as plt
        minx, miny, maxx, maxy = roi.buffer(5.0).total_bounds
        
        _, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.buildings.plot(ax=ax, color='lightgrey')
        # grid.boundary.plot(ax=ax, color='blue', linewidth=0.2)
        grid.apply(lambda x: ax.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color='blue', size=12, ha='center'), axis=1);

        scalField.plot(ax=ax, column="Z_value", alpha=0.5)
        div.plot(ax=ax, column="divergence", legend=True)

        ax.axis([minx, maxx, miny, maxy])
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
