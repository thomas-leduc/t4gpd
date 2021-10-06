'''
Created on 17 juin 2020

@author: tleduc
'''
import unittest

from numpy import pi
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.wkt import loads
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.isovist.STIsovistField2D import STIsovistField2D
from t4gpd.morph.STGrid import STGrid

import geopandas as gpd


class STIsovistField2DTest(unittest.TestCase):

    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()
        self.viewpoints = STGrid(self.buildings, 50, dy=None, indoor=False, intoPoint=True).run()

    def tearDown(self):
        self.buildings = None
        self.viewpoints = None

    def testRun(self):
        nRays, rayLength = 64, 20.0
        isovRaysField, isovField = STIsovistField2D(self.buildings, self.viewpoints, nRays, rayLength).run()

        for result in [isovRaysField, isovField]:
            self.assertIsInstance(result, gpd.GeoDataFrame, "Is a GeoDataFrame")
            self.assertEqual(result.crs, self.buildings.crs, "Verify CRS")
            self.assertEqual(15, len(result), "Count rows")
            self.assertEqual(7, len(result.columns), 'Count columns')

        approxRayLength = rayLength + 1e-6            
        for _, row in isovRaysField.iterrows():
            self.assertIsInstance(row.geometry, MultiLineString, 'Is a GeoDataFrame of MultiLineString')
            self.assertEqual(0, row['indoor'], 'indoor attribute values')
            self.assertEqual(nRays, len(row.geometry.geoms), 'Verify number of rays')
            self.assertTrue(all([0 <= g.length <= approxRayLength for g in row.geometry.geoms]), 'Verify ray lengths')
            self.assertIsInstance(loads(row['viewpoint']), Point, 'Test viewpoint attribute')
            self.assertIsInstance(loads(row['vect_drift']), LineString, 'Test vect_drift attribute')
            self.assertEqual(loads(row['viewpoint']).coords[0], loads(row['vect_drift']).coords[0],
                             'Test viewpoint and vect_drift attribute values')

        for _, row in isovField.iterrows():
            self.assertIsInstance(row.geometry, Polygon, 'Is a GeoDataFrame of Polygon')
            self.assertEqual(0, row['indoor'], 'indoor attribute values')
            self.assertTrue(0 <= row.geometry.area <= pi * rayLength ** 2, 'Verify isovist field areas')
            self.assertIsInstance(loads(row['viewpoint']), Point, 'Test viewpoint attribute')
            self.assertIsInstance(loads(row['vect_drift']), LineString, 'Test vect_drift attribute')
            self.assertEqual(loads(row['viewpoint']).coords[0], loads(row['vect_drift']).coords[0],
                             'Test viewpoint and vect_drift attribute values')

        '''
        import matplotlib.pyplot as plt
        basemap = self.buildings.plot(color='lightgrey', edgecolor='black', linewidth=0.3)
        isovRaysField.plot(ax=basemap, color='blue')
        isovField.boundary.plot(ax=basemap, color='red')
        plt.show()
        '''

        # isovField.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
