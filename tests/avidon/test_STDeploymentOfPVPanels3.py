'''
Created on 28 mar. 2022

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
from shapely.geometry import MultiPolygon
from t4gpd.avidon.STDeploymentOfPVPanels3 import STDeploymentOfPVPanels3
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class STDeploymentOfPVPanels3Test(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        pass

    def testRun1(self):
        coverRate, ribbonWidth = 0.3, 3.2
        azim0, azim1 = (270 - 45, 270 + 45)
        dh, dw = 1.6, 1.0

        result = STDeploymentOfPVPanels3(self.buildings, coverRate=coverRate,
                                         ribbonWidth=ribbonWidth, azimuthRange=(azim0, azim1),
                                         sizeOfPVPanel=(dh, dw)).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        # self.assertEqual(55, len(result), 'Count rows')
        self.assertEqual(7, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertTrue(azim0 <= row.azimuth <= azim1, 'Test azimuth attribute value')
            
            nMax = coverRate * row.length * ribbonWidth / (dh * dw)
            self.assertLessEqual(nMax - 2, row.n_modules, 'Test n_modules attribute value')
            self.assertGreaterEqual(nMax, row.n_modules, 'Test n_modules attribute value')

        '''
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar

        _, basemap = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey', edgecolor='dimgrey', linewidth=0.5)
        self.buildings.apply(lambda x: basemap.annotate(
            text=x.HAUTEUR, xy=x.geometry.centroid.coords[0],
            color='blue', size=9, ha='center'), axis=1)
        result.boundary.plot(ax=basemap, color='red', linewidth=0.4, hatch='//')
        result.apply(lambda x: basemap.annotate(
            text=x.n_modules, xy=x.geometry.centroid.coords[0],
            color='black', size=9, ha='center'), axis=1)
        basemap.axis('off')
        scalebar = ScaleBar(dx=1.0, units='m', length_fraction=None, width_fraction=0.005,
            location='lower left', frameon=True)
        basemap.add_artist(scalebar)
        plt.show()
        '''

    def testRun2(self):
        coverRate, ribbonWidth = 0.3, None
        azim0, azim1 = None, None
        dh, dw = 1.6, 1.0

        result = STDeploymentOfPVPanels3(self.buildings, coverRate=coverRate,
                                         ribbonWidth=ribbonWidth, azimuthRange=(azim0, azim1),
                                         sizeOfPVPanel=(dh, dw)).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(len(self.buildings), len(result), 'Count rows')
        self.assertEqual(len(self.buildings.columns) + 1, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiPolygon, 'Is a GeoDataFrame of MultiPolygons')
            self.assertEqual(row.n_modules, len(row.geometry.geoms), 'Test n_modules attribute value')

        '''
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar

        _, basemap = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey', edgecolor='dimgrey', linewidth=0.5)
        result.boundary.plot(ax=basemap, color='red', linewidth=0.4)
        result.apply(lambda x: basemap.annotate(
            text=x.n_modules, xy=x.geometry.centroid.coords[0],
            color='black', size=9, ha='center'), axis=1)
        basemap.axis('off')
        scalebar = ScaleBar(dx=1.0, units='m', length_fraction=None, width_fraction=0.005,
            location='lower left', frameon=True)
        basemap.add_artist(scalebar)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
