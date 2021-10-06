'''
Created on 28 sept. 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from pandas.core.series import Series
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from t4gpd.commons.RayCastingLib import RayCastingLib


class RayCastingLibTest(unittest.TestCase):

    def setUp(self):
        self.viewpoint = Point((0, 0))
        rows = [
            {'geometry': Polygon([(10, 10), (11, 10), (11, -10), (10, -10)]), 'HAUTEUR': 10.0},
            {'geometry': Polygon([(20, 10), (21, 10), (21, -10), (20, -10)]), 'HAUTEUR': 22.0},
            ]
        self.masks = GeoDataFrame(rows)
        self.spatialIndex = self.masks.sindex

    def tearDown(self):
        pass
    
    def testPrepareOrientedRays(self):
        shootingDirs = RayCastingLib.prepareOrientedRays(
            self.masks, self.spatialIndex, self.viewpoint)
        self.assertIsInstance(shootingDirs, list, 'shootingDirs is a list')
        self.assertEqual(2, len(shootingDirs), 'shootingDirs is a list of 2 items')
        self.assertEqual([1.0, 0.0], shootingDirs[0], 'Test shootingDirs 1st item')
        self.assertEqual([-1.0, 0.0], shootingDirs[1], 'Test shootingDirs 2nd item')

    def testPreparePanopticRays(self):
        shootingDirs = RayCastingLib.preparePanopticRays(4)
        self.assertIsInstance(shootingDirs, list, 'shootingDirs is a list')
        self.assertEqual(4, len(shootingDirs), 'shootingDirs is a list of 4 items')

    def testSingleRayCast2D(self):
        shootingDir, rayLength = [1.0, 0.0], 100.0
        ray, hitPoint, hitDist, hitMask = RayCastingLib.singleRayCast2D(
            self.masks, self.spatialIndex, self.viewpoint, shootingDir, rayLength)

        self.assertIsInstance(ray, LineString, 'Ray is a LineString')
        self.assertIsInstance(hitPoint, Point, 'hitPoint is a Point')
        self.assertEqual(10.0, hitDist, 'Test hitDist value')
        self.assertIsInstance(hitMask, Series, 'hitMask is a pandas.core.series.Series')
        self.assertEqual(10.0, hitMask['HAUTEUR'], 'Test hitMask HAUTEUR attribute value')

    def testSingleRayCast25D(self):
        shootingDir, rayLength, elevationFieldName = [1.0, 0.0], 100.0, 'HAUTEUR'
        ray, hitPoint, hitDist, hitMask, hitHW = RayCastingLib.singleRayCast25D(
            self.masks, self.spatialIndex, self.viewpoint, shootingDir, rayLength,
            elevationFieldName, background=True)

        self.assertIsInstance(ray, LineString, 'Ray is a LineString')
        self.assertIsInstance(hitPoint, Point, 'hitPoint is a Point')
        self.assertEqual(20.0, hitDist, 'Test hitDist value')
        self.assertIsInstance(hitMask, Series, 'hitMask is a pandas.core.series.Series')
        self.assertEqual(22.0, hitMask['HAUTEUR'], 'Test hitMask HAUTEUR attribute value')
        self.assertEqual(22.0 / 20.0, hitHW, 'Test hitHW value')

    def testMultipleRayCast2D(self):
        shootingDirs, rayLength = RayCastingLib.preparePanopticRays(4), 100.0
        rays, hitPoints, hitDists, hitMasks = RayCastingLib.multipleRayCast2D(
            self.masks, self.spatialIndex, self.viewpoint, shootingDirs, rayLength)

        self.assertIsInstance(rays, MultiLineString, 'Rays is a MultiLineString')
        self.assertIsInstance(hitPoints, list, 'hitPoints is a list')
        self.assertEqual([10.0, 100.0, 100.0, 100.0], hitDists, 'Test hitDists value')
        self.assertIsInstance(hitMasks[0], Series, 'hitMasks[0] is a pandas.core.series.Series')
        self.assertIsInstance(hitMasks[0].geometry, Polygon, 'hitMasks[0].geometry is a Polygon')
        self.assertEqual(10.0, hitMasks[0]['HAUTEUR'], 'Test hitMasks[0]["HAUTEUR"] attribute value')

        '''
        import matplotlib.pyplot as plt
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        GeoDataFrame([ {'geometry': self.viewpoint} ]).plot(ax=basemap, color='black')
        self.masks.plot(ax=basemap, color='lightgrey')
        GeoDataFrame([ {'geometry': ray} ]).plot(ax=basemap, color='red')
        GeoDataFrame([ {'geometry': hitPoint} ]).plot(ax=basemap, color='blue')
        self.masks.apply(lambda x: basemap.annotate(
            s='%.1f' % (x.HAUTEUR), xy=x.geometry.centroid.coords[0],
            color='black', size=14, ha='center'), axis=1);
        plt.show()
        '''
        # result.to_file('/tmp/xxx.shp')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
