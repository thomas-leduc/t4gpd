'''
Created on 18 juil. 2022

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

from t4gpd.demos.GeoDataFrameDemos5 import GeoDataFrameDemos5
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid

from t4gpd.pyvista.geoProcesses.FromContourToNormalVector import FromContourToNormalVector
from t4gpd.pyvista.geoProcesses.AutomaticFaceOrientation import AutomaticFaceOrientation


class AutomaticFaceOrientationTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRun(self):
        gdf = GeoDataFrameDemos5.cirSceneMasque1()

        op = AutomaticFaceOrientation(gdf)
        gdfCorr = STGeoProcess(op, gdf).run()

        noCorr = gdfCorr[ gdfCorr.reverse == 1 ].reverse.sum()
        noIndecision = gdfCorr[ gdfCorr.reverse == 2 ].reverse.sum()
        print(f'Nb of corr.: {noCorr}, Nb of indecision: {noIndecision}')

        self.assertEqual(174, noCorr, 'Nb of corr.')
        self.assertEqual(0, noIndecision, 'Nb of indecision')

        op = FromContourToNormalVector(magn=3.0)
        nvect = STGeoProcess(op, gdfCorr).run()

        # scene = ToUnstructuredGrid([gdf, nvect]).run()
        scene = ToUnstructuredGrid([gdfCorr, nvect]).run()
        scene.plot(show_edges=True)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
