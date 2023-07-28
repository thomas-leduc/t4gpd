'''
Created on 17 juin 2021

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

from geopandas import GeoDataFrame
from t4gpd.morph.geoProcesses.AngularAbscissa import AngularAbscissa
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.morph.STCrossroadsGeneration import STCrossroadsGeneration
from t4gpd.morph.geoProcesses.RectifyByFWT import RectifyByFWT


class RectifyByFWTTest(unittest.TestCase):

    def setUp(self):
        self.patterns = STCrossroadsGeneration(
            nbranchs=4, length=100.0, width=10.0, mirror=False,
            withBranchs=True, withSectors=True,
            crs='EPSG:2154', magnitude=2.5).run()
        self.patterns = self.patterns.loc[ self.patterns[ self.patterns.gid == 40 ].index ]

        self.nRays = 64
        self.rays = STGeoProcess(AngularAbscissa(
            self.patterns, 'vpoint_x', 'vpoint_y', self.nRays), self.patterns).run()

    def tearDown(self):
        pass

    def testRun(self):
        op = RectifyByFWT(nOutputRays=8, wavelet='Haar')
        result = STGeoProcess(op, self.rays).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')
        '''
        '''
        import matplotlib.pyplot as plt
        basemap = self.patterns.plot(color='lightgrey', edgecolor='black', linewidth=0.3)
        result.boundary.plot(ax=basemap, color='red', alpha=0.5)
        plt.show()
        '''
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
