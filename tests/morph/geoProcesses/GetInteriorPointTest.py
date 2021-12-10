'''
Created on 21 juin 2021

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
from shapely.geometry import Point, Polygon
from t4gpd.morph.geoProcesses.GetInteriorPoint import GetInteriorPoint
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class GetInteriorPointTest(unittest.TestCase):

    def setUp(self):
        self.inputGdf = GeoDataFrame([
            {'gid':0, 'geometry': Polygon([(0, 0), (9, 0), (9, 9), (0, 9)])},
            {'gid':1, 'geometry': Polygon([(0, 0), (9, 0), (9, 9), (0, 9)], [[(1, 1), (8, 1), (8, 8), (1, 8)]])},
            ])

    def tearDown(self):
        pass

    def testRun(self):
        result = STGeoProcess(GetInteriorPoint(), self.inputGdf).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(2, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            if (0 == row.gid):
                self.assertEqual('POINT (4.5 4.5)', row.geometry.wkt, 'Test returned geometry')
            elif (1 == row.gid):
                self.assertEqual('POINT (0.5625 0.5625)', row.geometry.wkt, 'Test returned geometry')
            else:
                raise self.failureException('Test gid attribute value')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
