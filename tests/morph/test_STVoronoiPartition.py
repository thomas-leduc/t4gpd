'''
Created on 25 sept. 2020

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
along with t4gpd. If not, see <https://www.gnu.org/licenses/>.
'''
import unittest
from shapely.geometry import MultiPoint, Polygon
from geopandas.geodataframe import GeoDataFrame
from t4gpd.morph.STVoronoiPartition import STVoronoiPartition


class STVoronoiPartitionTest(unittest.TestCase):

    def setUp(self):
        pointsGeom = MultiPoint(((0, 0), (100, 100), (0, 100), (100, 0), (20, 70),
                                 (70, 80), (60, 50), (50, 20), (20, 30), (80, 10),
                                 (10, 10)))
        self.points = GeoDataFrame([ {'geometry': pointsGeom} ])

    def tearDown(self):
        pass

    def testRun(self):
        op = STVoronoiPartition(self.points)
        # tin = op.getDelaunayTriangles()
        result = op.run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(7, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for i, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')
            self.assertEqual(i, row['gid'], 'test gid field')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.points.plot(ax=basemap, color='black')
        tin.boundary.plot(ax=basemap, color='green', linewidth=0.5)
        result.boundary.plot(ax=basemap, color='red')
        result.apply(lambda x: basemap.annotate(
            s=x.gid, xy=x.geometry.centroid.coords[0],
            color='red', size=14, ha='center'), axis=1);
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
