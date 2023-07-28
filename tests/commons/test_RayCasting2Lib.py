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
import unittest

from shapely.geometry import Point
from t4gpd.commons.RayCasting2Lib import RayCasting2Lib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class RayCasting2LibTest(unittest.TestCase):

    def setUp(self):
        self.masks = GeoDataFrameDemos.regularGridOfPlots(1, 1, dw=1.0)
        self.masks['HAUTEUR'] = 2.0

    def tearDown(self):
        pass

    def testAreCovisible1(self):
        epsilon = 1e-3
        pairs = [
            [Point([-2.0, 0.0]), Point([-2.0, 0.0])],
            # [Point([1.0, 0.0]), Point([2.0, 0.0])],
            [Point([-2.0, 0.0]), Point([0.0, 3.0])],
            [Point([-2.0, 0.0, 3.0]), Point([2.0, 0.0, 3.0])],
            [Point([-2.0, 0.0, 2.0]), Point([2.0, 0.0, 2.0 + epsilon])],
            [Point([-2.0, 0.0]), Point([0.0, 0.0, 4.0 + epsilon])],
            ]
        for ptA, ptB in pairs:
            result, _ = RayCasting2Lib.areCovisible(ptA, ptB, self.masks, 'HAUTEUR', self.masks.sindex)
            self.assertTrue(result, f'{ptA} and {ptB} are covisible')

    def testAreCovisible2(self):
        pairs = [
            [Point([-2.0, 0.0]), Point([2.0, 0.0])],
            [Point([-2.0, 0.0, 1.0]), Point([2.0, 0.0, 1.0])],
            [Point([-2.0, 0.0, 2.0]), Point([2.0, 0.0, 2.0])],
            [Point([-2.0, 0.0]), Point([0.0, 0.0, 4.0])],
            ]
        for ptA, ptB in pairs:
            result, _ = RayCasting2Lib.areCovisible(ptA, ptB, self.masks, 'HAUTEUR', self.masks.sindex)
            self.assertFalse(result, f'{ptA} and {ptB} are not covisible')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        self.masks.plot(ax=basemap, color='lightgrey')
        self.masks.apply(lambda x: basemap.annotate(
            text='%.1f' % (x.HAUTEUR), xy=x.geometry.centroid.coords[0],
            color='black', size=14, ha='center'), axis=1);
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
