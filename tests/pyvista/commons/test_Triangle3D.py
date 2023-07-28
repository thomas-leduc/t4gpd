'''
Created on 23 aout 2022

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

from numpy import pi, sqrt
from t4gpd.pyvista.commons.Triangle3D import Triangle3D


class Triangle3DTest(unittest.TestCase):

    def setUp(self):
        self.triangle = Triangle3D([1, 0, 0], [0, 1, 0], [0, 0, 1])

    def tearDown(self):
        pass

    def testArea3D(self):
        self.assertAlmostEqual(sqrt(3.0) / 2.0, self.triangle.area3D(), None,
                               'Test area calculation in 3D', 1e-6)

    def testCentroid(self):
        expected = [1 / 3, 1 / 3, 1 / 3]
        self.assertListEqual(expected, self.triangle.centroid(), 'Test centroid value')

    def testSphericalArea(self):
        # Area of sphere = 4 * pi * R ** 2
        self.assertEqual(pi / 2.0, self.triangle.sphericalArea(),
                         'Test spherical area calculation')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
