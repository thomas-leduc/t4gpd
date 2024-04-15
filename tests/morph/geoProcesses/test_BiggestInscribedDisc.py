'''
Created on 18 juin 2020

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from numpy import pi
from shapely import Polygon
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.geoProcesses.BiggestInscribedDisc import BiggestInscribedDisc
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class BiggestInscribedDiscTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.sensors = STGrid(self.buildings, 50, dy=None,
                              indoor=False, intoPoint=True).run()

    def tearDown(self):
        self.buildings = None
        self.sensors = None

    def testRun(self):
        disc = BiggestInscribedDisc(self.buildings)
        result = STGeoProcess(disc, self.sensors).run()
        self.assertIsInstance(result, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(self.sensors), len(result), "Count rows")
        self.assertEqual(len(self.sensors.columns)+1,
                         len(result.columns), "Count columns")

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon,
                                  "Is a GeoDataFrame of Polygons")

            expectedSurf = pi * (row["insc_diam"] / 2.0) ** 2
            ratioToTest = (expectedSurf - row.geometry.area) / expectedSurf
            self.assertGreater(0.01, ratioToTest, "Areas test")

        '''
        import matplotlib.pyplot as plt
        my_map_base = self.buildings.boundary.plot(edgecolor="black", linewidth=0.3)
        self.sensors.plot(ax=my_map_base, marker="+", markersize=120)
        result.boundary.plot(ax=my_map_base, edgecolor="red", linewidth=0.3)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
