'''
Created on 11 juin 2021

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

from geopandas import GeoDataFrame
from t4gpd.graph.STToRoadsSectionsNodes import STToRoadsSectionsNodes
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.CrossroadsStarDomain import CrossroadsStarDomain


class CrossroadsStarDomainTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        self.roads = GeoDataFrameDemos.districtRoyaleInNantesRoads()
        self.nodes = STToRoadsSectionsNodes(self.roads).run()
        self.nodes = self.nodes.loc[ self.nodes.gid.isin([43, 59, 97, 102]) ]

    def tearDown(self):
        pass

    def testRun(self):
        op = CrossroadsStarDomain(self.buildings)
        result = STGeoProcess(op, self.nodes).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        print(result.columns, result)
        self.assertEqual(4, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIn(row.gid, [43, 59, 97, 102], 'Test gid attr. value')
            self.assertTrue(0 <= row.MinLenRad <= row.MaxLenRad, 'Test MinLenRad/MaxLenRad attr. values')
            self.assertTrue(0 <= row.kern_drift, 'Test kern_drift attr. value')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey', edgecolor='dimgrey', linewidth=0.2)
        self.roads.plot(ax=basemap, color='black', linewidth=0.5)
        self.nodes.plot(ax=basemap, color='red', marker='+', markersize=12)
        result.boundary.plot(ax=basemap, color='red')
        result.apply(lambda x: basemap.annotate(
            text='%d %.1f' % (x.gid, x.kern_drift), xy=x.geometry.centroid.coords[0],
            color='black', size=10, ha='right'), axis=1)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
