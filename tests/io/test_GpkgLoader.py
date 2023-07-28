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
from tempfile import TemporaryDirectory
import unittest

from geopandas import GeoDataFrame
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.io.GpkgLoader import GpkgLoader
from t4gpd.io.GpkgWriter import GpkgWriter


class GpkgLoaderTest(unittest.TestCase):

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
            result = GpkgLoader(ofile).run()

            self.assertIsInstance(result, dict, 'Is a dict')
            self.assertEqual(3, len(result), 'Is a dict of 3 items')
            for k, v in result.items():
                self.assertIsInstance(k, str, 'Key is a str')
                self.assertIsInstance(v, GeoDataFrame, 'Value is a GeoDataFrame')

            self.assertEqual(len(self.buildings), len(result['buildings']), 'Count rows (1)')
            self.assertEqual(len(self.roads), len(result['roads']), 'Count rows (2)')
            self.assertEqual(len(self.misc), len(result['misc']), 'Count rows (3)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
