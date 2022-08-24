'''
Created on 28 avr. 2022

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
from datetime import datetime, timezone
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.morph.geoProcesses.Translation import Translation
from t4gpd.sun.STHardShadow import STHardShadow

from t4gpd.commons.sun.SunBeamLib import SunBeamLib


class SunBeamLibTest(unittest.TestCase):

    def setUp(self):
        self.masks = GeoDataFrameDemos.regularGridOfPlots(1, 1, dw=1.0)
        self.dx, self.dy = 353904, 6695053
        self.masks = STGeoProcess(Translation([self.dx, self.dy]), self.masks).run()
        self.masks['HAUTEUR'] = 10.0
        self.masks.crs = 'epsg:2154'
        self.dt = datetime(2021, 6, 21, 12, tzinfo=timezone.utc)  # summer solstice at noon

    def tearDown(self):
        pass

    def __plot(self, shadow, viewpoint, ray, result):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        color = 'red' if result else 'blue'
        ax.set_title(f'isHitBySunBeam: {result}')
        GeoDataFrame(data=[{'geometry': viewpoint}]).plot(ax=ax, color=color)
        GeoDataFrame(data=[{'geometry': ray}]).plot(ax=ax, color=color)
        self.masks.plot(ax=ax, color='dimgrey')
        shadow.plot(ax=ax, color='lightgrey', alpha=0.5)
        plt.axis('off')
        plt.show()
        plt.close(fig)

    def testIsHitBySunBeam(self):
        shadow = STHardShadow(self.masks, self.dt, 'HAUTEUR', 0.0).run()

        for viewpoint in [Point([self.dx, self.dy + 6.0]),
                          Point([self.dx, self.dy + 5.7]),
                          Point([self.dx, self.dy + 5.5])]:
            result, ray = SunBeamLib.isHitBySunBeam(viewpoint, self.dt, self.masks, 'HAUTEUR')
            self.assertTrue(result, 'Is hit by sunbeam (1)')
            self.__plot(shadow, viewpoint, ray, result)

        for viewpoint in [Point([self.dx, self.dy + 5.4]),
                          Point([self.dx, self.dy + 5.3]),
                          Point([self.dx, self.dy + 2.3])]:
            result, ray = SunBeamLib.isHitBySunBeam(viewpoint, self.dt, self.masks, 'HAUTEUR')
            self.assertFalse(result, 'Is not hit by sunbeam (2)')
            self.__plot(shadow, viewpoint, ray, result)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
