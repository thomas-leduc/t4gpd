'''
Created on 20 avr. 2021

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
from shapely.geometry import Point
from shapely.wkt import loads
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STPointsDensifier import STPointsDensifier


class STPointsDensifierTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()

        self.geoms = [
            loads('LINESTRING (50 0, 50 100, 100 100, 100 50, 150 50)'),
            loads('POLYGON ((0 150, 50 150, 50 200, 0 200, 0 150))')
            ]
        self.gdf = GeoDataFrame([{'gid': gid, 'geometry': geom} for gid, geom in enumerate(self.geoms)])

    def tearDown(self):
        pass

    def testRunKeepDuplicate1(self):
        result = STPointsDensifier(
            self.roads, distance=10.0, pathidFieldname=None,
            adjustableDist=True, removeDuplicate=False).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(185, len(result), 'Count rows')
        self.assertEqual(3 + len(self.roads), len(result.columns), 'Count columns')

        inputShapes = self.roads.geometry.unary_union
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertAlmostEqual(0.0, inputShapes.distance(row.geometry),
                                   msg='Points are close to the input shape')

    def testRunRemoveDuplicate1(self):
        result = STPointsDensifier(
            self.roads, distance=10.0, pathidFieldname=None,
            adjustableDist=True, removeDuplicate=True).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(149, len(result), 'Count rows')
        self.assertEqual(3 + len(self.roads), len(result.columns), 'Count columns')

        inputShapes = self.roads.geometry.unary_union
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertAlmostEqual(0.0, inputShapes.distance(row.geometry),
                                   msg='Points are close to the input shape')

    def testRunKeepDuplicate2(self):
        result = STPointsDensifier(
            self.roads, distance=10.0, pathidFieldname='ID',
            adjustableDist=True, removeDuplicate=False).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(185, len(result), 'Count rows')
        self.assertEqual(3 + len(self.roads), len(result.columns), 'Count columns')

        inputShapes = self.roads.geometry.unary_union
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertAlmostEqual(0.0, inputShapes.distance(row.geometry),
                                   msg='Points are close to the input shape')

    def testRunRemoveDuplicate2(self):
        result = STPointsDensifier(
            self.roads, distance=10.0, pathidFieldname='ID',
            adjustableDist=True, removeDuplicate=True).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(149, len(result), 'Count rows')
        self.assertEqual(3 + len(self.roads), len(result.columns), 'Count columns')

        inputShapes = self.roads.geometry.unary_union
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertAlmostEqual(0.0, inputShapes.distance(row.geometry),
                                   msg='Points are close to the input shape')

    def testRun(self):
        d = 5.0
        result = STPointsDensifier(
            self.gdf, distance=30.0, pathidFieldname='gid', adjustableDist=True,
            removeDuplicate=True, distToTheSubstrate=d).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(17, len(result), 'Count rows')
        self.assertEqual(3 + len(self.gdf), len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertAlmostEqual(d, self.geoms[row.gid].distance(row.geometry),
                                   msg='Points are close to the input shape')
        '''
        import matplotlib.pyplot as plt
        fig, basemap = plt.subplots(figsize=(1.0 * 8.26, 1.0 * 8.26))
        self.gdf.plot(ax=basemap, color='lightgrey', linewidth=1.3)
        result.plot(ax=basemap, color='red', marker='*', markersize=64)
        result.apply(lambda x: basemap.annotate(
            text=x.node_id, xy=x.geometry.coords[0],
            color='black', size=9, ha='left'), axis=1)
        plt.show()
        plt.close(fig)
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
