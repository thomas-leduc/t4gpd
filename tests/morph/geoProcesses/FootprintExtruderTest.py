'''
Created on 1 feb. 2021

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

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import MultiPolygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.FootprintExtruder import FootprintExtruder
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class FootprintExtruderTest(unittest.TestCase):

    def setUp(self):
        self.building = GeoDataFrameDemos.singleBuildingInNantes()
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()

    def tearDown(self):
        pass

    def testRun1(self):
        self.building['HAUTEUR'] = 15.0

        op = FootprintExtruder(self.building, 'HAUTEUR', forceZCoordToZero=True)
        result = STGeoProcess(op, self.building).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiPolygon, 'Is a GeoDataFrame of MultiPolygon')
            self.assertFalse(GeomLib.isCCW(row.geometry.geoms[0].exterior), 'Ground is downward oriented')
            self.assertTrue(GeomLib.isCCW(row.geometry.geoms[1].exterior), 'Roof is upward oriented')
            self.assertTrue(row.geometry.has_z, 'Is a GeoDataFrame of MultiPolygon Z')
            self.assertEqual(15.0, row['HAUTEUR'], 'Test HAUTEUR attribute value')

    def testRun2(self):
        self.buildings = self.buildings.explode() 

        op = FootprintExtruder(self.buildings, 'HAUTEUR', forceZCoordToZero=True)
        result = STGeoProcess(op, self.buildings).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(250, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiPolygon, 'Is a GeoDataFrame of MultiPolygon')
            self.assertFalse(GeomLib.isCCW(row.geometry.geoms[0].exterior), 'Ground is downward oriented')
            self.assertTrue(GeomLib.isCCW(row.geometry.geoms[1].exterior), 'Roof is upward oriented')
            self.assertTrue(row.geometry.has_z, 'Is a GeoDataFrame of MultiPolygon Z')
            self.assertTrue(0.0 <= row['HAUTEUR'] <= 27.3, 'Test HAUTEUR attribute value')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
