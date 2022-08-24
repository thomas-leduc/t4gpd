'''
Created on 22 juin 2022

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

from shapely.wkt import loads
from t4gpd.commons.GeomLib3D import GeomLib3D


class GeomLib3DTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGetFaceNormalVector1(self):
        expected = [0, 0, 1]
        WKTs = [
            'POLYGON Z ((0 0 1, 1 0 1, 1 1 1, 0 1 1, 0 0 1))',
            'POLYGON Z ((0 0 0, 1 0 0, 1 1 0, 0 1 0, 0 0 0))',
            'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
            ]
        for wkt in WKTs:
            geom = loads(wkt)
            actual = GeomLib3D.getFaceNormalVector(geom)
            self.assertListEqual(expected, actual, 'Test normal vector')

    def testGetFaceNormalVector2(self):
        expected = [1, 0, 0]
        PAIRS = [
            ('POLYGON Z ((1 0 0, 1 1 0, 1 1 1, 1 0 1))', [1, 0, 0]),
            ('POLYGON Z ((0 1 0, 0 0 0, 0 0 1, 0 1 1))', [-1, 0, 0])
            ]
        for wkt, expected in PAIRS:
            geom = loads(wkt)
            actual = GeomLib3D.getFaceNormalVector(geom)
            self.assertListEqual(expected, actual, 'Test normal vector')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
