'''
Created on 21 juin 2021

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

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.IsAnIndoorPoint import IsAnIndoorPoint
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.morph.geoProcesses.GetInteriorPoint import GetInteriorPoint
from t4gpd.morph.STGrid import STGrid


class IsAnIndoorPointTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.nodes1 = STGeoProcess(GetInteriorPoint(), self.buildings).run()
        self.nodes2 = STGrid(self.buildings, dx=25.0, dy=None, indoor=False,
                             intoPoint=True, encode=False).run()

    def tearDown(self):
        pass

    def testRun1(self):
        result = STGeoProcess(IsAnIndoorPoint(self.buildings), self.nodes1).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(44, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertEqual(1, row.indoor, 'Test indoor attribute values')

    def testRun2(self):
        result = STGeoProcess(IsAnIndoorPoint(self.buildings), self.nodes2).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(54, len(result), 'Count rows')
        self.assertEqual(5, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertEqual(0, row.indoor, 'Test indoor attribute values')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=basemap, color='grey')
        result.plot(ax=basemap, color='black')
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
