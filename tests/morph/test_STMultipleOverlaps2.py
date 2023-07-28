'''
Created on 21 sept. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.affinity import translate
from shapely.geometry import Polygon
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.ListUtilities import ListUtilities
from t4gpd.morph.STMultipleOverlaps2 import STMultipleOverlaps2


class STMultipleOverlaps2Test(unittest.TestCase):

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
        result = STMultipleOverlaps2(self.inputGdf).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(3, len(result), 'Count rows')
        self.assertEqual(2, len(result.columns), 'Count columns')

        result2 = result.explode(ignore_index=True)

        self.assertIsInstance(result2, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(6, len(result2), 'Count rows')
        self.assertEqual(2, len(result2.columns), 'Count columns')

        for _, row in result2.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygons')
            self.assertTrue(25 <= row.geometry.area <= 50, 'Areas test')
            self.assertTrue(1 <= row['nOverlap'] <= 3, 'nOverlap field test')
            self.assertTrue(
                ((row['nOverlap'] in [2, 3]) and (25 == row.geometry.area)) or
                ((row['nOverlap'] == 1) and (25 <= row.geometry.area <= 50)),
                'Areas and nOverlap field test')

    def testRun2(self):
        result = STMultipleOverlaps2(self.inputGdf, 'gid').run()

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
            text='%d\n%s' % (x.nOverlap, x.matched_id), xy=x.geometry.centroid.coords[0],
            color='black', size=11, ha='center'), axis=1);
        plt.show()
        '''

        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
