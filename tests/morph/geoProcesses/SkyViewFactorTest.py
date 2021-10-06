'''
Created on 28 sept. 2020

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

from shapely.geometry import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.morph.geoProcesses.SkyViewFactor import SkyViewFactor
from geopandas.geodataframe import GeoDataFrame


class SkyViewFactorTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = STGrid(self.buildings, 50, dy=None, indoor=False,
                                 intoPoint=True).run()

    def tearDown(self):
        pass

    def testRun(self):
        nRays, maxRayLen, elevationFieldname = 4, 100.0, 'HAUTEUR'
        op = SkyViewFactor(self.buildings, nRays, maxRayLen, elevationFieldname,
                           method=2018, background=True)
        result = STGeoProcess(op, self.viewpoints).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(15, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Point, 'Is a GeoDataFrame of Points')
            self.assertTrue(0 <= row['svf'] <= 1.0, 'Test svf attribute values')
            # self.assertTrue(4 == len(ArrayCoding.decode(row['hit_dists'])), 'Test hit_dists attribute values')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey')
        self.viewpoints.plot(ax=basemap, color='black')
        result.plot(ax=basemap, column='svf', legend=True, cmap='plasma')
        result.apply(lambda x: basemap.annotate(
            s='%.1f' % (x.svf), xy=x.geometry.centroid.coords[0],
            color='black', size=14, ha='center'), axis=1);
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
