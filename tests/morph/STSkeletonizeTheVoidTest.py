'''
Created on 27 sept. 2020

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
from shapely.geometry import LineString
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STSkeletonizeTheVoid import STSkeletonizeTheVoid


class STSkeletonizeTheVoidTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        pass

    def testRun(self):
        result = STSkeletonizeTheVoid(self.buildings, samplingDist=10.0).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(89, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, LineString, 'Is a GeoDataFrame of LineString')
            self.assertTrue(0 <= row['gid'] <= 89, 'Test gid attribute')
            self.assertTrue(0 < row['distance'], 'Test distance attribute')
            self.assertTrue(row.geometry.length == row['distance'], 'Test distance attribute')

        '''
        import matplotlib.pyplot as plt
        basemap = self.buildings.plot(edgecolor='dimgrey', color='lightgrey',)
        result.plot(ax=basemap, color='red', linewidth=1.3)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
