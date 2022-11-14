'''
Created on 9 nov. 2022

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

from geopandas import GeoDataFrame, read_file
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from tempfile import TemporaryDirectory
from t4gpd.io.GpkgWriter import GpkgWriter


class GpkgWriterTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.roads = GeoDataFrameDemos.ensaNantesRoads()
        self.misc = GeoDataFrame(data=[{'geometry': None}])

    def tearDown(self):
        pass

    def testRun(self):
        with TemporaryDirectory() as tmpdir:
            ofile = f'{tmpdir}/test.gpkg'
            GpkgWriter({'buildings': self.buildings, 'roads': self.roads, 'misc': self.misc},
                      ofile).run()

            actualBuildings = read_file(ofile, layer='buildings', driver='GPKG')
            self.assertIsInstance(actualBuildings, GeoDataFrame, 'Is a GeoDataFrame (1)')
            self.assertEqual(len(self.buildings), len(actualBuildings), 'Count rows (1)')

            actualRoads = read_file(ofile, layer='roads', driver='GPKG')
            self.assertIsInstance(actualRoads, GeoDataFrame, 'Is a GeoDataFrame (2)')
            self.assertEqual(len(self.roads), len(actualRoads), 'Count rows (2)')

            actualMisc = read_file(ofile, layer='misc', driver='GPKG')
            self.assertIsInstance(actualMisc, GeoDataFrame, 'Is a GeoDataFrame (3)')
            self.assertEqual(len(self.misc), len(actualMisc), 'Count rows (3)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
