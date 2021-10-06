'''
Created on 21 nov. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, MultiLineString, Point
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.graph.ShortestPathLib import ShortestPathLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class ShortestPathLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testShortestPath1(self):
        roads = GeoDataFrameDemos.ensaNantesRoads()
        origDest = GeoDataFrame([ {'geometry': Point((355195, 6688483))}, {'geometry': Point((355412, 6688447))} ])
        fromPoint, toPoint = origDest.geometry

        dijk = ShortestPathLib(roads)
        nNodes1, nEdges1 = dijk.graph.node_count, dijk.graph.edge_count

        pathGeom, pathLen = dijk.shortestPath(fromPoint, toPoint)
        nNodes2, nEdges2 = dijk.graph.node_count, dijk.graph.edge_count

        self.assertIsInstance(pathGeom, MultiLineString, 'Is a MultiLineString')
        self.assertIsInstance(pathLen, float, 'Is a float')
        self.assertEqual(pathGeom.length, pathLen, 'Test path length (1)')
        self.assertTrue(Epsilon.equals(340.85, pathLen, 1e-2), msg='Test path length (2)')
        self.assertEqual(nNodes1, nNodes2, 'Nb nodes in graph equality')
        self.assertEqual(nEdges1, nEdges2, 'Nb edges in graph equality')

        '''
        result = GeoDataFrame([{'geometry':pathGeom, 'short_dist': pathLen}], crs=roads.crs)
        import matplotlib.pyplot as plt
        basemap = roads.plot(color='grey', linewidth=4.2)
        result.plot(ax=basemap, color='red', linewidth=1.2)
        origDest.plot(ax=basemap, color='blue')
        plt.show()
        '''

    def testShortestPath2(self):
        roads = GeoDataFrame([
            {'geometry': LineString([ (0, 0), (10, 0) ])},
            {'geometry': LineString([ (10, 0), (10, 10) ])},
            {'geometry': LineString([ (10, 10), (20, 10) ])},
            {'geometry': LineString([ (20, 10), (20, 20) ])},
            {'geometry': LineString([ (10, 0), (30, 0) ])},
            {'geometry': LineString([ (30, 0), (30, 10), (20, 10) ])},
            {'geometry': LineString([ (10, 10), (20, 20) ])}
            ])
        origDest = GeoDataFrame([ {'geometry': Point((19, 2))}, {'geometry': Point((21, 17))} ])
        fromPoint, toPoint = origDest.geometry

        dijk = ShortestPathLib(roads)
        nNodes1, nEdges1 = dijk.graph.node_count, dijk.graph.edge_count

        pathGeom, pathLen = dijk.shortestPath(fromPoint, toPoint)
        nNodes2, nEdges2 = dijk.graph.node_count, dijk.graph.edge_count

        self.assertIsInstance(pathGeom, MultiLineString, 'Is a MultiLineString')
        self.assertIsInstance(pathLen, float, 'Is a float')
        self.assertEqual(pathGeom.length, pathLen, 'Test path length (1)')
        self.assertTrue(Epsilon.equals(39, pathLen, 1e-2), msg='Test path length (2)')
        self.assertEqual(nNodes1, nNodes2, 'Nb nodes in graph equality')
        self.assertEqual(nEdges1, nEdges2, 'Nb edges in graph equality')

        '''
        result = GeoDataFrame([{'geometry':pathGeom, 'short_dist': pathLen}], crs=roads.crs)
        import matplotlib.pyplot as plt
        basemap = roads.plot(color='grey', linewidth=4.2)
        result.plot(ax=basemap, color='red', linewidth=1.2)
        origDest.plot(ax=basemap, color='blue')
        plt.show()
        '''

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
