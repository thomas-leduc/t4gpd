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
from pandas import concat
from shapely.geometry import Point
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STShortestPath import STShortestPath


class STShortestPathTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()
        self.fromPoints = GeoDataFrame([ {'geometry': Point((355195, 6688483))} ], crs=self.roads.crs)
        self.toPoints = GeoDataFrame([ {'geometry': Point((355412, 6688447))} ], crs=self.roads.crs)

    def tearDown(self):
        pass

    def testRun1(self):
        result = STShortestPath(self.roads, self.fromPoints, self.toPoints).run()
        gid, pathLen, fromPoint, toPoint = result[['gid', 'pathLen', 'fromPoint', 'toPoint']].squeeze()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')
        self.assertEqual(0, gid, 'Test attribute (1)')
        self.assertEqual(pathLen, result.length.squeeze(), 'Test path length (1)')
        self.assertEqual(fromPoint, self.fromPoints.geometry.squeeze().wkt, 'Test attribute (2)')
        self.assertEqual(toPoint, self.toPoints.geometry.squeeze().wkt, 'Test attribute (3)')
        self.assertTrue(Epsilon.equals(340.85, result.geometry.length.squeeze(), 1e-2), msg='Test path length (2)')

    def testRun2(self):
        result = STShortestPath(self.roads, self.fromPoints.geometry.squeeze(), self.toPoints).run()
        gid, pathLen, fromPoint, toPoint = result[['gid', 'pathLen', 'fromPoint', 'toPoint']].squeeze()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')
        self.assertEqual(0, gid, 'Test attribute (1)')
        self.assertEqual(pathLen, result.length.squeeze(), 'Test path length (1)')
        self.assertEqual(fromPoint, self.fromPoints.geometry.squeeze().wkt, 'Test attribute (2)')
        self.assertEqual(toPoint, self.toPoints.geometry.squeeze().wkt, 'Test attribute (3)')
        self.assertTrue(Epsilon.equals(340.85, result.geometry.length.squeeze(), 1e-2), msg='Test path length (2)')

    def testRun3(self):
        result = STShortestPath(self.roads, self.fromPoints, self.toPoints.geometry.squeeze()).run()
        gid, pathLen, fromPoint, toPoint = result[['gid', 'pathLen', 'fromPoint', 'toPoint']].squeeze()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')
        self.assertEqual(0, gid, 'Test attribute (1)')
        self.assertEqual(pathLen, result.length.squeeze(), 'Test path length (1)')
        self.assertEqual(fromPoint, self.fromPoints.geometry.squeeze().wkt, 'Test attribute (2)')
        self.assertEqual(toPoint, self.toPoints.geometry.squeeze().wkt, 'Test attribute (3)')
        self.assertTrue(Epsilon.equals(340.85, result.geometry.length.squeeze(), 1e-2), msg='Test path length (2)')

    def testRun4(self):
        result = STShortestPath(self.roads, self.fromPoints.geometry.squeeze(), self.toPoints.geometry.squeeze()).run()
        gid, pathLen, fromPoint, toPoint = result[['gid', 'pathLen', 'fromPoint', 'toPoint']].squeeze()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')
        self.assertEqual(0, gid, 'Test attribute (1)')
        self.assertEqual(pathLen, result.length.squeeze(), 'Test path length (1)')
        self.assertEqual(fromPoint, self.fromPoints.geometry.squeeze().wkt, 'Test attribute (2)')
        self.assertEqual(toPoint, self.toPoints.geometry.squeeze().wkt, 'Test attribute (3)')
        self.assertTrue(Epsilon.equals(340.85, result.geometry.length.squeeze(), 1e-2), msg='Test path length (2)')

    def testRun5(self):
        fromToPoints = concat([self.fromPoints, self.toPoints])

        result = STShortestPath(self.roads, fromToPoints, fromToPoints).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(4, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            if row.fromPoint == row.toPoint:
                self.assertEqual(0.0, row.pathLen, 'Test path emptiness (1)')
                self.assertEqual(0.0, row.geometry.length, 'Test path emptiness (2)')
            else:
                self.assertTrue(Epsilon.equals(340.85, row.pathLen, 1e-2), msg='Test path length (1)')
                self.assertTrue(Epsilon.equals(340.85, row.geometry.length, 1e-2), msg='Test path length (2)')

        '''
        result = result[~(result.geometry.is_empty | result.geometry.isna())]

        import matplotlib.pyplot as plt
        basemap = self.roads.plot(color='grey', linewidth=4.2)
        result.plot(ax=basemap, color='red', linewidth=1.2)
        self.fromPoints.plot(ax=basemap, color='blue')
        self.toPoints.plot(ax=basemap, color='green')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
