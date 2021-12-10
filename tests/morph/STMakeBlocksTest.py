'''
Created on 12 feb. 2021

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

from shapely.geometry import box

from geopandas import GeoDataFrame
from t4gpd.morph.STMakeBlocks import STMakeBlocks
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class STMakeBlocksTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.roads = GeoDataFrameDemos.ensaNantesRoads()

    def tearDown(self):
        pass

    def testRun(self):
        roi = GeoDataFrame([{'geometry': box(*self.roads.total_bounds)}], crs=self.buildings.crs)
        result = STMakeBlocks(self.buildings, self.roads, roi=roi).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(7, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        '''
        import matplotlib.pyplot as plt
        basemap = self.buildings.boundary.plot(edgecolor='dimgrey', color='lightgrey',)
        result.plot(ax=basemap, color='red', linewidth=1.3)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
