'''
Created on 1 juin 2022

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

from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.raster.STToRaster import STToRaster
from numpy import ndarray


class STToRasterTest(unittest.TestCase):

    def setUp(self):
        self.gdf = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def testRun(self):
        nrows, ncols = 5, 10
        result = STToRaster(self.gdf, nrows, ncols, bbox=None, threshold=0.5, outputFile=None).execute()

        self.assertIsInstance(result, ndarray, 'Is a NumPy ndarray')
        self.assertEqual(nrows, result.shape[0], 'Test ndarray nb of rows')
        self.assertEqual(ncols, result.shape[1], 'Test ndarray nb of columns')
        self.assertEqual(22, result.sum(), 'Test ndarray sum')
        for r in range(nrows):
            for c in range(ncols):
                self.assertIn(result[r, c], [0, 1], f'Test ndarray values at [{r},{c}]')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
