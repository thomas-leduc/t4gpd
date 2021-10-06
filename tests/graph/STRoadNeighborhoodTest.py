'''
Created on 16 nov. 2020

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
from shapely.geometry import MultiLineString
from shapely.geometry import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STRoadNeighborhood import STRoadNeighborhood


class STRoadNeighborhoodTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()
        self.fromPointsAndMaxDists = GeoDataFrame([ 
            {'geometry': Point((355295, 6688411)), 'maxDist': 155.0 },
            {'geometry': Point((355184, 6688540)), 'maxDist': 45.0 },
            {'geometry': Point((355382, 6688533)), 'maxDist': 45.0 }
            ], crs=self.roads.crs)

    def tearDown(self):
        pass

    def testRun1(self):
        result = STRoadNeighborhood(self.roads, self.fromPointsAndMaxDists, 'maxDist').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(3, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')
        for gid, row in result.iterrows():
            self.assertEqual(gid, row['gid'], 'Test attribute value (1)')
            self.assertEqual(self.fromPointsAndMaxDists.geometry[gid].wkt, row['fromPoint'], 'Test attribute value (2)')
            self.assertEqual(155.0 if (0 == gid) else 45.0, row['maxDist'], 'Test attribute value (3)')
            self.assertIsInstance(row['geometry'], MultiLineString, 'Test geometry type')

    def testRun2(self):
        result = STRoadNeighborhood(self.roads, self.fromPointsAndMaxDists, 45.0).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(3, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')
        for gid, row in result.iterrows():
            self.assertEqual(gid, row['gid'], 'Test attribute value (1)')
            self.assertEqual(self.fromPointsAndMaxDists.geometry[gid].wkt, row['fromPoint'], 'Test attribute value (2)')
            self.assertEqual(45.0, row['maxDist'], 'Test attribute value (3)')
            self.assertIsInstance(row['geometry'], MultiLineString, 'Test geometry type')

        '''
        import matplotlib.pyplot as plt
        basemap = self.roads.plot(color='grey', linewidth=4.2)
        result.plot(ax=basemap, color='red', linewidth=1.2)
        self.fromPointsAndMaxDists.plot(ax=basemap, color='blue')
        # self.toPoints.plot(ax=basemap, color='green')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
