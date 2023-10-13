'''
Created on 27 sep. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from t4gpd.commons.TestUtils import TestUtils
from t4gpd.io.MedReader import MedReader
from t4gpd.pyvista.ToPolyData import ToPolyData


class MedReaderTest(unittest.TestCase):

    def setUp(self):
        self.ifile = TestUtils.getDataSetFilename(
            "tests/data", "VeineRueBat.med")

    def tearDown(self):
        pass

    def testRun(self):
        result = MedReader(self.ifile).run()

        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(648, len(result), "Count rows")
        self.assertEqual(2, len(result.columns), "Count columns")
        self.assertTrue(all(result.geometry.apply(
            lambda g: g.has_z)), "3D geometries")

        # scene = ToPolyData([result], fieldname=None).run()
        # scene.plot(opacity=0.5, show_edges=True)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
