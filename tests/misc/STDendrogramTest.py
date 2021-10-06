'''
Created on 5 janv. 2021

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
from random import randint
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point
from t4gpd.misc.STDendrogram import STDendrogram


class STDendrogramTest(unittest.TestCase):

    def setUp(self):
        rows = []
        for x, y in [(0, 0), (100, 0), (0, 100)]:
            for _ in range(10):
                _x, _y = x + randint(-10, 10), y + randint(-10, 10)
                rows.append({'geometry': Point((_x, _y)), 'x': float(_x), 'y': float(_y)}) 
        self.inputGdf = GeoDataFrame(rows)

    def tearDown(self):
        pass

    def testRun(self):
        result = STDendrogram(self.inputGdf, orientation='top', no_plot=False, verbose=True).run()
        self.assertEqual(3, result, 'Test nb clusters')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
