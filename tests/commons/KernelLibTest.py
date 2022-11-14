'''
Created on 25 feb. 2021

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

from shapely.wkt import loads

from t4gpd.commons.KernelLib import KernelLib


class KernelLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun1(self):
        inputWkt = 'POLYGON ((0 50, 50 50, 50 0, 100 0, 100 50, 150 50, 150 100, 100 100, 100 150, 50 150, 50 100, 0 100, 0 50))'
        inputGeom = loads(inputWkt)
        # expectedWkt = 'POLYGON ((100 50, 50 50, 50 100, 100 100, 100 50))'
        expectedWkt = 'POLYGON ((100 100, 100 50, 50 50, 50 100, 100 100))'
        expectedGeom = loads(expectedWkt)

        actualGeom, actualFlag = KernelLib.getKernel(inputGeom)

        self.assertTrue(actualFlag, 'Test kernel flag')
        self.assertEqual(actualGeom, expectedGeom, 'Test kernel geometry')

    def testRun2(self):
        inputWkt = 'POLYGON ((0 0, 150 0, 150 100, 100 100, 100 50, 50 50, 50 100, 0 100, 0 0))'
        inputGeom = loads(inputWkt)

        actualGeom, actualFlag = KernelLib.getKernel(inputGeom)

        self.assertFalse(actualFlag, 'Test kernel flag')
        self.assertIsNone(actualGeom, 'Test kernel geometry')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
