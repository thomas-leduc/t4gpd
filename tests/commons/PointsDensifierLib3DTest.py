'''
Created on 20 sept. 2022

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

from shapely.geometry import LineString, Point

from t4gpd.commons.PointsDensifierLib3D import PointsDensifierLib3D


class PointsDensifierLib3DTest(unittest.TestCase):

    def setUp(self):
        self.geom = LineString(((0, 0, 0), (0, 0, 10)))
        self.curvAbsc = [0, 0.5, 1]

    def tearDown(self):
        pass

    def testDensifyByCurvilinearAbscissa(self):
        result = PointsDensifierLib3D.densifyByCurvilinearAbscissa(self.geom, self.curvAbsc, blockid=0)

        self.assertIsInstance(result, list, 'Is a list of dict (1)')
        self.assertEqual(len(self.curvAbsc), len(result), 'Is a list of 3 dict')
        for i, item in enumerate(result):
            self.assertIsInstance(item, dict, 'Is a list of dict (2)')
            self.assertIsInstance(item['geometry'], Point, 'Is a list of dict (2)')
            self.assertEqual(10 * self.curvAbsc[i], item['geometry'].z, 'Test resulting z-values')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
