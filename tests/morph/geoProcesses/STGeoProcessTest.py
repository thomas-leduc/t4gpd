'''
Created on 18 mai 2021

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
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.CircularityIndices import CircularityIndices
from t4gpd.morph.geoProcesses.ConvexityIndices import ConvexityIndices
from t4gpd.morph.geoProcesses.RectangularityIndices import RectangularityIndices
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class STGeoProcessTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def testRun1(self):
        op1 = ConvexityIndices()
        result = STGeoProcess(op1, self.buildings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(8, len(result.columns), 'Count columns')

        for fieldname in ['n_con_comp', 'a_conv_def', 'p_conv_def', 'big_concav', 'small_conc']:
            self.assertTrue(fieldname in result, f'Test if "{fieldname}" is a valid fieldname')

    def testRun2(self):
        op1 = ConvexityIndices()
        result = STGeoProcess([op1], self.buildings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(8, len(result.columns), 'Count columns')

        for fieldname in ['n_con_comp', 'a_conv_def', 'p_conv_def', 'big_concav', 'small_conc']:
            self.assertTrue(fieldname in result, f'Test if "{fieldname}" is a valid fieldname')

    def testRun3(self):
        op1 = ConvexityIndices()
        op2 = CircularityIndices()
        op3 = RectangularityIndices()
        result = STGeoProcess([op1, op2, op3], self.buildings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(16, len(result.columns), 'Count columns')

        for fieldname in ['n_con_comp', 'a_conv_def', 'p_conv_def', 'big_concav', 'small_conc',
                          'gravelius', 'jaggedness', 'miller', 'morton', 'a_circ_def',
                          'stretching', 'a_rect_def', 'p_rect_def']:
            self.assertTrue(fieldname in result, f'Test if "{fieldname}" is a valid fieldname')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
