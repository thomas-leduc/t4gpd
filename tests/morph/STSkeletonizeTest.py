'''
Created on 28 sept. 2020

@author: tleduc
'''
import unittest
import geopandas as gpd
from shapely.geometry import MultiLineString
from t4gpd.morph.STSkeletonize import STSkeletonize
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class STSkeletonizeTest(unittest.TestCase):

    def setUp(self):
        self.inputGdf = GeoDataFrameDemos.singleBuildingInNantes()

    def tearDown(self):
        pass

    def testRun(self):
        result = STSkeletonize(self.inputGdf, samplingDist=5.0).run()

        self.assertIsInstance(result, gpd.GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(1, len(result), 'Count rows')
        self.assertEqual(3, len(result.columns), 'Count columns')

        for _, row in result.iterrows():
            self.assertIsInstance(row.geometry, MultiLineString, 'Is a GeoDataFrame of MultiLineString')
            self.assertTrue(row.geometry.within(self.inputGdf.geometry.squeeze()),
                            'Test skeleton is within input geometry')

        '''
        import matplotlib.pyplot as plt
        basemap = self.inputGdf.plot(edgecolor='dimgrey', color='lightgrey',)
        result.plot(ax=basemap, color='red', linewidth=1.3)
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
