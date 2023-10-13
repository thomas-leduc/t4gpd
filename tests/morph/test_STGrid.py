'''
Created on 11 juin 2020

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

from geopandas import clip, read_file
from geopandas.datasets import get_path
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid

import matplotlib.pyplot as plt


class STGridTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        self.buildings = None
        self.countries = None

    def __plot(self, inputGdf, grid):
        # grid.to_file('/tmp/grid.shp')
        basemap = inputGdf.boundary.plot(color='red', linewidth=1.0)
        if (0 < len(grid['Point' == grid.geom_type])):
            # NODES
            if 'indoor' in grid:
                grid.plot(ax=basemap, column='indoor',
                          legend=True, cmap='plasma')
            else:
                grid.plot(ax=basemap)
        else:
            # POLYGONS
            if 'indoor' in grid:
                grid.plot(ax=basemap, edgecolor='black', alpha=0.75,
                          column='indoor', legend=True, cmap='plasma')
            else:
                grid.plot(ax=basemap, edgecolor='black',
                          color='white', alpha=0.75)
        plt.show()

    def __commons(self, inputGdf, grid, nFeatures, nIndoorFeatures=0, nOutdoorFeatures=0):
        self.assertIsInstance(grid, GeoDataFrame, "grid is a GeoDataFrame")
        self.assertEqual(grid.crs, inputGdf.crs, "Verify grid CRS")
        self.assertEqual(nFeatures, len(grid), "grid features count")
        if (0 < nIndoorFeatures) or (0 < nOutdoorFeatures):
            self.assertEqual(nIndoorFeatures, len(
                grid.query('True == indoor')), "Indoor features count")
            self.assertEqual(nOutdoorFeatures, len(grid.query(
                'False == indoor')), "Outdoor features count")
            if 0 == nIndoorFeatures:
                for indoor in grid['indoor']:
                    self.assertFalse(indoor, "Outdoor grid attribute value")
            elif 0 == nOutdoorFeatures:
                for indoor in grid['indoor']:
                    self.assertTrue(indoor, "Indoor grid attribute value")
            else:
                for indoor in grid['indoor']:
                    self.assertIn(indoor, [True, False],
                                  "Indoor or outdoor grid items")

    def testRunBuildings_Point_None(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor=None, intoPoint=True).run()
        self.__commons(self.buildings, grid, 25)
        # self.__plot(self.buildings, grid)

    def testRunBuildings_Point_Both(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor='both', intoPoint=True).run()
        self.__commons(self.buildings, grid, 25, 12, 13)
        # self.__plot(self.buildings, grid)

    def testRunBuildings_Point_True(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor=True, intoPoint=True).run()
        self.__commons(self.buildings, grid, 12, 12, 0)
        # self.__plot(self.buildings, grid)

    def testRunBuildings_Point_False(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor=False, intoPoint=True).run()
        self.__commons(self.buildings, grid, 13, 0, 13)
        # self.__plot(self.buildings, grid)

    def testRunBuildings_Polygon_None(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor=None, intoPoint=False).run()
        self.__commons(self.buildings, grid, 25)
        # self.__plot(self.buildings, grid)

    def testRunBuildings_Polygon_Both(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor='both', intoPoint=False).run()
        self.__commons(self.buildings, grid, 25, 12, 13)
        # self.__plot(self.buildings, grid)

    def testRunBuildings_Polygon_True(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor=True, intoPoint=False).run()
        self.__commons(self.buildings, grid, 12, 12, 0)
        # self.__plot(self.buildings, grid)

    def testRunBuildings_Polygon_False(self):
        grid = STGrid(self.buildings, 50, dy=None,
                      indoor=False, intoPoint=False).run()
        self.__commons(self.buildings, grid, 13, 0, 13)
        # self.__plot(self.buildings, grid)

    def testRunBuildings(self):
        self.assertEqual(57, len(self.buildings), "Buildings features count")


if __name__ == "__main__":
    # import sys; sys.argv = ['', 'Test.testRun']
    unittest.main()
