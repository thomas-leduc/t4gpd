'''
Created on 8 nov. 2021

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
import unittest

from geopandas import GeoDataFrame
from pandas import DataFrame
from tempfile import TemporaryDirectory
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.io.ZipLoader import ZipLoader
from t4gpd.io.ZipWriter import ZipWriter


class ZipLoaderTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.roads = GeoDataFrameDemos.ensaNantesRoads()
        self.misc = DataFrame(data=[(i, 10 * i)
                              for i in range(4)], columns=["colA", "colB"])

    def tearDown(self):
        pass

    def testRun1(self):
        with TemporaryDirectory() as tmpdir:
            ZipWriter({"buildings": self.buildings, "roads": self.roads, "misc": self.misc},
                      f"{tmpdir}/test", driver="GPKG").run()
            result = ZipLoader(f"{tmpdir}/test.zip").run()
            self.assertIsNone(result, "Test if result is None")

    def testRun2(self):
        with TemporaryDirectory() as tmpdir:
            ZipWriter({"buildings": self.buildings, "roads": self.roads, "misc": self.misc},
                      f"{tmpdir}/test", driver="GPKG").run()
            buildings, misc, roads = ZipLoader(f"{tmpdir}/test.zip",
                                               ["buildings", "misc", "roads"]).run()

        self.assertIsInstance(buildings, GeoDataFrame, "Is a GeoDataFrame (1)")
        self.assertEqual(len(self.buildings), len(buildings), "Count rows (1)")

        self.assertIsInstance(roads, GeoDataFrame, "Is a GeoDataFrame (2)")
        self.assertEqual(len(self.roads), len(roads), "Count rows (2)")

        self.assertIsInstance(misc, GeoDataFrame, "Is a GeoDataFrame (3)")
        self.assertEqual(len(self.misc), len(misc), "Count rows (3)")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
