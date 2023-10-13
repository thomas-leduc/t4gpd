'''
Created on 1 juil. 2021

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
from t4gpd.avidon.STDeploymentOfPVPanels import STDeploymentOfPVPanels
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class STDeploymentOfPVPanelsTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        pass

    def testName(self):
        coverRate = 0.3
        azim0, azim1 = (270 - 45, 270 + 45)
        dh, dw = 1.6, 1.0
        result = STDeploymentOfPVPanels(self.buildings, coverRate=coverRate,
                                        azimuthRange=(azim0, azim1), sizeOfPVPanel=(dh, dw)).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        # self.assertEqual(61, len(result), 'Count rows')
        self.assertEqual(8, len(result.columns), 'Count columns')
        for _, row in result.iterrows():
            self.assertTrue(azim0 <= row.azimuth <= azim1, 'Test azimuth attribute value')
            self.assertLessEqual(1, row.n_modules, 'Test n_modules attribute value')
            self.assertGreaterEqual(coverRate * row.length * row.HAUTEUR / (dh * dw),
                                    row.n_modules, 'Test n_modules attribute value')

        '''
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar

        _, basemap = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        self.buildings.plot(ax=basemap, color='lightgrey', edgecolor='dimgrey', linewidth=0.5)
        self.buildings.apply(lambda x: basemap.annotate(
            text=x.HAUTEUR, xy=x.geometry.centroid.coords[0],
            color='black', size=9, ha='center'), axis=1)
        result.plot(ax=basemap, column='n_modules', linewidth=3.0, legend=True, cmap='magma')
        result.apply(lambda x: basemap.annotate(
            text=x.n_modules, xy=x.geometry.centroid.coords[0],
            color='red', size=9, ha='center'), axis=1)
        basemap.axis('off')
        scalebar = ScaleBar(dx=1.0, units='m', length_fraction=None, width_fraction=0.005,
            location='lower left', frameon=True)
        basemap.add_artist(scalebar)
        plt.show()
        '''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
