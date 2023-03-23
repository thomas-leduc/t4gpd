'''
Created on 17 dec. 2020

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
from shapely.geometry import  Point
from t4gpd.commons.graph.MCALib import MCALib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class MCALibTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()

    def tearDown(self):
        pass

    def testBetweenness_centrality(self):
        result = MCALib(self.roads).betweenness_centrality()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(33, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertLessEqual(0, row.betweenness, 'Tests betweenness attribute')

        '''
        import matplotlib.pyplot as plt
        basemap = self.roads.plot(color='grey', linewidth=0.6)
        result.plot(ax=basemap, column='betweenness', legend=True)
        plt.show()
        '''

    def testCloseness_centrality(self):
        result = MCALib(self.roads).closeness_centrality()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(33, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertLessEqual(0, row.closeness, 'Tests betweenness attribute')

        '''
        import matplotlib.pyplot as plt
        basemap = self.roads.plot(color='grey', linewidth=0.6)
        result.plot(ax=basemap, column='closeness', legend=True)
        plt.show()
        '''

    def testDegree_centrality(self):
        result = MCALib(self.roads).degree_centrality()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(33, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertLessEqual(0, row.degree_c, 'Tests betweenness attribute')

        '''
        import matplotlib.pyplot as plt
        basemap = self.roads.plot(color='grey', linewidth=0.6)
        result.plot(ax=basemap, column='degree_c', legend=True)
        plt.show()
        '''

    def testMinimum_spanning_tree(self):
        result = MCALib(self.roads).minimum_spanning_tree()
        

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
