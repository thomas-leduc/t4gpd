'''
Created on 19 juil. 2021

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
from tempfile import TemporaryDirectory
import unittest

from geopandas import GeoDataFrame, read_file
from pandas import DataFrame
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.io.ZipWriter import ZipWriter


class ZipWriterTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testName(self):
        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        roads = GeoDataFrameDemos.ensaNantesRoads()
        misc = DataFrame(data=[(i, 10 * i) for i in range(4)], columns=['colA', 'colB'])

        with TemporaryDirectory() as tmpdir:
            ZipWriter({'buildings': buildings, 'roads': roads, 'misc': misc},
                      f'{tmpdir}/test', driver='GPKG').run()

            actualBuildings = read_file(f'{tmpdir}/test.zip!test/buildings.gpkg', driver='GPKG')
            self.assertIsInstance(actualBuildings, GeoDataFrame, 'Is a GeoDataFrame (1)')
            self.assertEqual(len(buildings), len(actualBuildings), 'Count rows (1)')

            actualRoads = read_file(f'{tmpdir}/test.zip!test/roads.gpkg', driver='GPKG')
            self.assertIsInstance(actualRoads, GeoDataFrame, 'Is a GeoDataFrame (2)')
            self.assertEqual(len(roads), len(actualRoads), 'Count rows (2)')

            actualMisc = read_file(f'{tmpdir}/test.zip!test/misc.gpkg', driver='GPKG')
            self.assertIsInstance(actualMisc, DataFrame, 'Is a GeoDataFrame (3)')
            self.assertEqual(len(misc), len(actualMisc), 'Count rows (3)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
