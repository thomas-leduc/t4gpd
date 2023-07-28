'''
Created on 18 juin 2020

@author: tleduc
'''
import unittest

from geopandas import GeoDataFrame
from shapely.geometry import MultiLineString
from t4gpd.morph.geoProcesses.AngularAbscissa import AngularAbscissa
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

from t4gpd.morph.STCrossroadsGeneration import STCrossroadsGeneration


class AngularAbscissaTest(unittest.TestCase):

    def setUp(self):
        self.rayLen = 100.0
        self.inputGdf = STCrossroadsGeneration(nbranchs=4, length=self.rayLen, width=10.0,
                                               mirror=False, withBranchs=True, withSectors=True,
                                               crs='EPSG:2154', magnitude=2.5).run()

    def tearDown(self):
        self.inputGdf = None

    def testRun(self):
        nRays = 16
        result = STGeoProcess(AngularAbscissa(self.inputGdf, 'vpoint_x', 'vpoint_y', nRays), self.inputGdf).run()

        self.assertIsInstance(result, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(13, len(result), 'Count rows')
        self.assertEqual(6, len(result.columns), 'Count columns')

        rayLen = self.rayLen + 0.1
        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiLineString, 'Is a GeoDataFrame of MultiLineString')
            self.assertEqual(nRays, len(row.geometry.geoms), 'Count MultiLineString rays')
            self.assertTrue(all([0 <= r.length <= rayLen for r in row.geometry.geoms]), 'MultiLineString ray lengths test')
        '''
        import matplotlib.pyplot as plt
        my_map_base = self.inputGdf.boundary.plot(edgecolor='black', linewidth=0.3)
        result.plot(ax=my_map_base, edgecolor='red', linewidth=0.3)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
