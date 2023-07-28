'''
Created on 12 avr. 2021

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
from shapely.geometry import LineString
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

import matplotlib.pyplot as plt
from t4gpd.commons.LineStringCuttingLib import LineStringCuttingLib


class LineStringCuttingLibTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()

    def tearDown(self):
        pass

    def testCuttingIntoSegments(self):
        result = LineStringCuttingLib.cuttingIntoSegments(self.roads, cuttingDist=10.0)

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(182, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIn(row.gid, range(182), 'Test gid attribute value')
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')

        '''
        result.gid = result.gid % 3
        _, basemap = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.roads.plot(ax=basemap, color='grey', linewidth=6)
        result.plot(ax=basemap, column='gid', linewidth=3, cmap='viridis')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
