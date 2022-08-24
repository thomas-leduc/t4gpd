'''
Created on 13 mai 2022

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

from geopandas import GeoDataFrame
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib


class GeoDataFrameLibTest(unittest.TestCase):

    def setUp(self):
        self.gdf1 = GeoDataFrameDemos.singleBuildingInNantes()
        self.gdf2 = GeoDataFrameDemos.districtGraslinInNantesTrees()
        self.gdf3 = GeoDataFrameDemos.regularGridOfPlots(3, 3, dw=5.0)
        self.gdf4 = GeoDataFrameDemos.regularGridOfPlots2(4, 5, bdx=25, bdy=8, sdx=10, sdy=10)
        self.gdf5 = GeoDataFrame([])

    def tearDown(self):
        pass

    def testShareTheSameCrs(self):
        self.assertTrue(GeoDataFrameLib.shareTheSameCrs(self.gdf1, self.gdf2), 'Test shareTheSameCrs (1)')
        self.assertTrue(GeoDataFrameLib.shareTheSameCrs(self.gdf3, self.gdf4), 'Test shareTheSameCrs (2)')
        self.assertTrue(GeoDataFrameLib.shareTheSameCrs(self.gdf3, self.gdf5), 'Test shareTheSameCrs (3)')

        self.assertFalse(GeoDataFrameLib.shareTheSameCrs(self.gdf1, self.gdf5), 'Test shareTheSameCrs (4)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
