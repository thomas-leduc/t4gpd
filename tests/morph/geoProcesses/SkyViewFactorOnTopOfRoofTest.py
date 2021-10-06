'''
Created on 3 mars 2021

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
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.morph.geoProcesses.SkyViewFactorOnTopOfRoof import SkyViewFactorOnTopOfRoof
from shapely.geometry import Point


class SkyViewFactorOnTopOfRoofTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()

        self.viewpoints = self.buildings.copy(deep=True)
        self.viewpoints.geometry = self.viewpoints.centroid
        self.viewpoints = self.viewpoints[self.viewpoints.index.isin([147, 148, 149, 150, 151, 152])]
        self.viewpoints.reset_index(drop=True, inplace=True)

    def tearDown(self):
        pass

    def testRun(self):
        op = SkyViewFactorOnTopOfRoof(self.buildings, nRays=16)
        result = STGeoProcess(op, self.viewpoints).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(6, len(result), 'Count rows')
        self.assertEqual(4, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Point')
            self.assertTrue(0.09 < row.svf_roof < 0.40, 'svf_roof attribute test')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=basemap, color='grey', edgecolor='white', linewidth=0.5)
        result.plot(ax=basemap, column='svf_roof', legend=True)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
