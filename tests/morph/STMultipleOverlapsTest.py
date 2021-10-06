'''
Created on 12 sept. 2020

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
from shapely.affinity import translate
from shapely.geometry import Polygon
import unittest

from geopandas.geodataframe import GeoDataFrame

from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.ListUtilities import ListUtilities
from t4gpd.morph.STMultipleOverlaps import STMultipleOverlaps


class STMultipleOverlapsTest(unittest.TestCase):

    def setUp(self):
        a = Polygon(((0, 0), (0, 10), (10, 10), (10, 0), (0, 0)))
        b = translate(a, xoff=5.0, yoff=5.0)
        c = translate(a, xoff=5.0)
        self.inputGdf = GeoDataFrame([
            {'gid':10, 'geometry':a},
            {'gid':20, 'geometry':b},
            {'gid':30, 'geometry':c}])

    def tearDown(self):
        pass

    def testRun1(self):
        result = STMultipleOverlaps(self.inputGdf).run()
        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(6, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')

            self.assertTrue(25 <= row.geometry.area < 50.1, 'Areas test')
            self.assertTrue(1 <= row['nOverlap'] <= 3, 'nOverlap field test')
            self.assertTrue(
                ((row['nOverlap'] in [2, 3]) and (25 <= row.geometry.area < 25.1)) or
                ((row['nOverlap'] == 1) and (25 <= row.geometry.area < 50.1)),
                'Areas and nOverlap field test')

    def testRun2(self):
        result = STMultipleOverlaps(self.inputGdf, 'gid').run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(6, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')

            self.assertTrue(25 <= row.geometry.area < 50.1, 'Areas test')
            self.assertTrue(1 <= row['nOverlap'] <= 3, 'nOverlap field test')
            self.assertTrue(
                ((row['nOverlap'] in [2, 3]) and (25 <= row.geometry.area < 25.1)) or
                ((row['nOverlap'] == 1) and (25 <= row.geometry.area < 50.1)),
                'Areas and nOverlap field test')

            self.assertTrue(ListUtilities.isASubList(
                ArrayCoding.decode(row['matched_id']), [10, 20, 30]),
                'matched_id field test')

        '''
        import matplotlib.pyplot as plt
        basemap = self.inputGdf.boundary.plot(edgecolor='black', linewidth=1.3)
        result.plot(ax=basemap, column='nOverlap', alpha=0.2)
        result.apply(lambda x: basemap.annotate(
            s='%d\n%s' % (x.nOverlap, x.matched_id), xy=x.geometry.centroid.coords[0],
            color='black', size=11, ha='center'), axis=1);
        plt.show()
        '''

        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
