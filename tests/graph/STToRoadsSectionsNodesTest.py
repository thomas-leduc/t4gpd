'''
Created on 17 juin 2020

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

from shapely.geometry import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.graph.STToRoadsSectionsNodes import STToRoadsSectionsNodes
from geopandas.geodataframe import GeoDataFrame


class STToRoadsSectionsNodesTest(unittest.TestCase):

    def setUp(self):
        self.roads = GeoDataFrameDemos.ensaNantesRoads()

    def tearDown(self):
        self.roads = None

    def testRun(self):
        result = STToRoadsSectionsNodes(self.roads).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(31, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertIn(row['nb_connections'], [1, 3, 4], 'nb_connections attribute values')

        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
