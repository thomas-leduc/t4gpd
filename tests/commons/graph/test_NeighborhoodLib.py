'''
Created on 23 nov. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, Point
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.graph.NeighborhoodLib import NeighborhoodLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class NeighborhoodLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testNeighborhood(self):
        roads = GeoDataFrameDemos.ensaNantesRoads()
        origDest = GeoDataFrame([ {'geometry': Point((355295, 6688411))} ])
        maxDist = 155.0
        fromPoint = origDest.geometry.squeeze()

        result = NeighborhoodLib.neighborhood(roads, fromPoint, maxDist)

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(26, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            # self.assertEqual(row.geometry.length, row['length'], 'Test attribute')
            self.assertTrue(Epsilon.equals(row.geometry.length, row['length']), 'Test attribute')

        for _path in [(25, 17, 16, 8, 7), (25, 17, 16, 10, 2, 0), (25, 17, 15, 13, 12), (25, 20, 18, 21), (25, 20, 19, 22)]:
            _distAcc = sum(result[ result.gid.isin(_path) ].length)
            self.assertTrue(Epsilon.equals(maxDist, _distAcc), 'Test full path length')

        '''
        import matplotlib.pyplot as plt
        basemap = roads.plot(color='grey', linewidth=4.2)
        result.plot(ax=basemap, color='red', linewidth=1.2)
        origDest.plot(ax=basemap, color='blue')
        result.apply(lambda x: basemap.annotate(
            text=x.gid, xy=x.geometry.centroid.coords[0],
            color='black', size=9, ha='center'), axis=1)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
