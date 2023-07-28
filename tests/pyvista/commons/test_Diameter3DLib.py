'''
Created on 5 sept. 2022

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

from numpy import sqrt
from shapely.geometry import Polygon

from t4gpd.pyvista.commons.Diameter3DLib import Diameter3DLib


class Diameter3DLibTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDiameter3D1(self):
        d = 10
        geom = Polygon([(0, 0), (d, 0), (d, d), (0, d)])
        diam, dist = Diameter3DLib.diameter3D(geom)
        self.assertEqual(f'LINESTRING (0 0, {d} {d})', diam.wkt, 'Test diameter WKT')
        self.assertEqual(d * sqrt(2), dist, 'Test diameter length')

    def testDiameter3D2(self):
        d = 10
        geom = Polygon([(0, 0, 0), (0, d, 0), (0, d, d), (0, 0, d)])
        diam, dist = Diameter3DLib.diameter3D(geom)
        self.assertEqual(f'LINESTRING Z (0 0 0, 0 {d} {d})', diam.wkt, 'Test diameter WKT')
        self.assertEqual(d * sqrt(2), dist, 'Test diameter length')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
