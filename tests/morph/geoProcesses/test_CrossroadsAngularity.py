'''
Created on 25 juin 2021

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
from t4gpd.graph.STToRoadsSectionsNodes import STToRoadsSectionsNodes
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.CrossroadsAngularity import CrossroadsAngularity


class CrossroadsAngularityTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()
        self.nodes = STToRoadsSectionsNodes(self.roads).run()

    def tearDown(self):
        pass

    def testRun(self):
        result = STGeoProcess(CrossroadsAngularity(self.roads), self.nodes).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(result.crs, self.roads.crs, 'Verify CRS')
        self.assertEqual(31, len(result), 'Count rows')
        self.assertEqual(8, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')

            _azims = ArrayCoding.decode(row.cross_azim)
            for _azim in _azims:
                self.assertTrue(0 <= _azim < 360, 'Test cross_azim attribute value')
            self.assertIsNone(row.cross_std1, 'Test cross_std1 attribute value')

            _angles = ArrayCoding.decode(row.cross_angl)
            for _angle in _angles:
                self.assertTrue(0 <= _angle < 360, 'Test cross_angl attribute value')

            self.assertEqual(len(_azims), len(_angles), 'Test azims/angles attrib. lengths')
            self.assertGreaterEqual(4, len(_angles), 'Test azims/angles attrib. lengths')
            self.assertIsNone(row.cross_std2, 'Test cross_std2 attribute value')
            self.assertIn(row.cross_mode, [4, 8, 16], 'Test cross_mode attribute value')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.roads.plot(ax=basemap)
        result.plot(ax=basemap, color='red')
        plt.show()
        '''
        result.to_file('/tmp/z.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
