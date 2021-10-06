'''
Created on 11 sept. 2020

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
from shapely.geometry import Point
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.morph.geoProcesses.Rotation2D import Rotation2D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class Rotation2DTest(unittest.TestCase):

    def setUp(self):
        rows = [
            {'gid': 0, 'geometry': Point((0, 0))},
            {'gid': 1, 'geometry': Point((100, 0))},
            {'gid': 2, 'geometry': Point((0, 100))},
            ]
        self.inputGdf = GeoDataFrame(rows)

    def tearDown(self):
        pass

    def testRun(self):
        result = STGeoProcess(Rotation2D(90, origin=(0, 0)), self.inputGdf).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(3, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            if (0 == row['gid']):
                self.assertEqual(row.geometry, Point((0, 0)), 'Equality test (1)')
            elif (1 == row['gid']):
                self.assertTrue(Epsilon.equals(row.geometry, Point((100.0, 0.0))), 'Equality test (2)')
            elif (2 == row['gid']):
                self.assertTrue(Epsilon.equals(row.geometry, Point((0.0, 100.0))), 'Equality test (3)')

            
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
