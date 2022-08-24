'''
Created on 7 avr. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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

from geopandas import GeoDataFrame
from shapely.geometry import Point
from shapely.wkt import loads

from t4gpd.morph.STPointsDensifier2 import STPointsDensifier2


class STPointsDensifier2Test(unittest.TestCase):

    def setUp(self):
        self.geoms = [
            loads('LINESTRING (50 0, 50 100, 100 100, 100 50, 150 50)'),
            loads('POLYGON ((0 150, 50 150, 50 200, 0 200, 0 150))')
            ]
        self.gdf = GeoDataFrame([{'gid': gid, 'geometry': geom} for gid, geom in enumerate(self.geoms)])
        self.curvAbsc = [0.25, 0.75]

    def tearDown(self):
        pass

    def testRun1(self):
        result = STPointsDensifier2(
            self.gdf, self.curvAbsc, pathidFieldname='gid').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(16, len(result), 'Count rows')
        self.assertEqual(3 + len(self.gdf), len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertAlmostEqual(0.0, self.geoms[row.gid].distance(row.geometry),
                                   msg='Points are close to the input shape')

    def testRun2(self):
        d = 5.0
        result = STPointsDensifier2(
            self.gdf, self.curvAbsc, pathidFieldname='gid', distToTheSubstrate=d).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(16, len(result), 'Count rows')
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
