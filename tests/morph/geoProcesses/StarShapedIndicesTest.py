'''
Created on 15 janv. 2021

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
from shapely.geometry import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.isovist.STIsovistField2D import STIsovistField2D
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.morph.geoProcesses.StarShapedIndices import StarShapedIndices


class StarShapedIndicesTest(unittest.TestCase):

    def setUp(self):
        self.nRays, self.rayLength = 36, 50.0
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = GeoDataFrame(
            [{'geometry': Point((355317.9, 6688409.5))}], crs=self.buildings.crs)
        self.isovRays, self.isov = STIsovistField2D(
            self.buildings, self.viewpoints, self.nRays, self.rayLength).run()

    def tearDown(self):
        pass

    def testRun(self):
        result = STGeoProcess(StarShapedIndices(precision=1.0, base=2), self.isovRays).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(9, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row['min_raylen'], float, 'Test min_raylen return type')
            self.assertIsInstance(row['avg_raylen'], float, 'Test avg_raylen return type')
            self.assertIsInstance(row['std_raylen'], float, 'Test std_raylen return type')
            self.assertIsInstance(row['max_raylen'], float, 'Test max_raylen return type')
            self.assertIsInstance(row['entropy'], float, 'Test entropy return type')
            self.assertIsInstance(row['drift'], float, 'Test drift return type')

            self.assertTrue(0 <= row['min_raylen'] <= self.rayLength, 'Test min_raylen attribute value')
            self.assertTrue(0 <= row['avg_raylen'] <= self.rayLength, 'Test avg_raylen attribute value')
            self.assertTrue(0 <= row['std_raylen'] <= self.rayLength, 'Test std_raylen attribute value')
            self.assertTrue(0 <= row['max_raylen'] <= self.rayLength + 1e-6, 'Test max_raylen attribute value')
            self.assertTrue(0 <= row['entropy'], 'Test entropy attribute value')
            self.assertTrue(0 <= row['drift'] <= self.rayLength, 'Test drift attribute value')

        '''
        import matplotlib.pyplot as plt
        basemap = self.buildings.plot(color='lightgrey', edgecolor='black', linewidth=0.3)
        self.isovRays.plot(ax=basemap, color='blue')
        self.isov.boundary.plot(ax=basemap, color='red')
        plt.show()
        '''

        # isovField.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
