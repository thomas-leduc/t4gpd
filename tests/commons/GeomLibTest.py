'''
Created on 18 juin 2020

@author: tleduc
'''
import unittest

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import GeometryCollection, LinearRing, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class GeomLibTest(unittest.TestCase):

    def setUp(self):
        a = Point((0, 0))
        b = Point((0, 9))
        c = Point((9, 9))
        d = Point((9, 0))
        
        self.linearring = LinearRing([(100, 0), (100, 100), (0, 100)])
        
        self.point = a
        self.multipoint = MultiPoint((a, b, c, d))
        self.linestring = LineString((a, b, c))
        self.multilinestring = MultiLineString([ ((0, 0), (0, 9), (9, 9)), ((3, 3), (6, 3), (6, 6)) ])
        self.polygon = Polygon((a, b, c, d), [[(3, 3), (3, 6), (6, 6), (6, 3)]])
        self.polygon2 = Polygon(((0, 0), (10, 0), (10, 90), (100, 90), (100, 100), (0, 100), (0, 0)))
        self.multipolygon = MultiPolygon((self.polygon, Polygon(self.linearring)))
        
        self.gc = GeometryCollection([self.point, self.linestring, self.polygon])

    def tearDown(self):
        pass

    def testAddZCoordinateIfNecessary(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            result = GeomLib.addZCoordinateIfNecessary(geom)
            self.assertTrue(result.has_z, 'has_z test')
            if GeomLib.isMultipart(result):
                self.assertTrue(all(
                    [ 0 == p.z  for p in GeomLib.getListOfShapelyPoints(result) ]),
                    'z value test')

    def testCutsLineStringByCurvilinearDistance(self):
        result = GeomLib.cutsLineStringByCurvilinearDistance(self.linestring, -4.5)
        self.assertIsInstance(result, list, 'Is a list of LineString (1)')
        self.assertEqual(len(result), 1, 'Is a list composed of a single LineString')
        self.assertIsInstance(result[0], LineString, 'Is a list of LineString (2)')
        self.assertEqual(result[0], self.linestring, 'Equality test (1)')

        result = GeomLib.cutsLineStringByCurvilinearDistance(self.linestring, 4.5)
        self.assertIsInstance(result, list, 'Is a list of LineStrings (3)')
        self.assertEqual(len(result), 2, 'Is a list of LineStrings (4)')
        self.assertEqual(result[0].wkt, 'LINESTRING (0 0, 0 4.5)', 'Equality test (2)')
        self.assertEqual(result[1].wkt, 'LINESTRING (0 4.5, 0 9, 9 9)', 'Equality test (3)')

    def testForceZCoordinateToZ0(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            result = GeomLib.forceZCoordinateToZ0(geom, z0=12.34)
            self.assertTrue(result.has_z, 'has_z test')
            if GeomLib.isMultipart(result):
                self.assertTrue(all(
                    [ 12.34 == p.z  for p in GeomLib.getListOfShapelyPoints(result) ]),
                    'z value test')

    def testGetEnclosingFeatures(self):
        buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        spatialIndex = buildings.sindex

        result = GeomLib.getEnclosingFeatures(buildings, spatialIndex, Point((355148, 6689335)))
        self.assertIsInstance(result, list, 'Test if result is a list')
        self.assertEqual(1, len(result), 'Test result length')
        self.assertEqual('BATIMENT0000000302931268', result[0]['ID'], 'Test ID attribute')
        self.assertEqual(21.7, result[0]['HAUTEUR'], 'Test HAUTEUR attribute')

        result = GeomLib.getEnclosingFeatures(buildings, spatialIndex, Point((355160, 6689335)))
        self.assertEqual([], result, 'Test if result is an empty list')

    def testGetInteriorPoint(self):
        result = GeomLib.getInteriorPoint(self.polygon)
        self.assertTrue(result.within(self.polygon), 'Point within polygon test (1)')

        result = GeomLib.getInteriorPoint(self.polygon2)
        self.assertTrue(result.within(self.polygon2), 'Point within polygon test (2)')

    def testGetListOfShapelyPoints(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            result = GeomLib.getListOfShapelyPoints(geom)
            self.assertTrue(isinstance(result, (list, tuple)))
            for pt in result:
                self.assertTrue(isinstance(pt, Point))

    def testIsAnIndoorPoint(self):
        p1 = Point((0, 0))
        p2 = Point((10, 0))
        buildings = GeoDataFrame([{ 'geometry': p1.buffer(5.0)}])
        self.assertTrue(GeomLib.isAnIndoorPoint(p1, buildings, buildings.sindex), 'Is an indoor point (1)')
        self.assertFalse(GeomLib.isAnIndoorPoint(p2, buildings, buildings.sindex), 'Is an indoor point (2)')
        
    def testIsAShapelyGeometry(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            self.assertTrue(GeomLib.isAShapelyGeometry(geom))

    def testIsInFrontOf(self):
        self.assertTrue(GeomLib.isInFrontOf(self.point, LineString([(0, 1), (10, 1)])), 'Is in front of (1)')
        self.assertFalse(GeomLib.isInFrontOf(self.point, LineString([(10, 1), (0, 1)])), 'Is in front of (2)')
        self.assertFalse(GeomLib.isInFrontOf(self.point, LineString([(0, 1), (0, 10)])), 'Is in front of (3)')

    def testIsMultipart(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon]:
            self.assertFalse(GeomLib.isMultipart(geom))
        for geom in [self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            self.assertTrue(GeomLib.isMultipart(geom))

    def testIsPolygonal(self):
        for geom in [self.polygon, self.multipolygon]:
            self.assertTrue(GeomLib.isPolygonal(geom))
        for geom in [self.point, self.linearring, self.linestring,
                     self.multipoint, self.multilinestring, self.gc]:
            self.assertFalse(GeomLib.isPolygonal(geom))

    def testNormalizeRingOrientation(self):
        result = GeomLib.normalizeRingOrientation(self.linearring)
        self.assertEqual('LINEARRING (100 0, 100 100, 0 100, 100 0)', result.wkt,
                         'Test normalize ring orientation (1)')

        result = GeomLib.normalizeRingOrientation(self.polygon)
        self.assertEqual('POLYGON ((0 0, 9 0, 9 9, 0 9, 0 0), (3 3, 3 6, 6 6, 6 3, 3 3))', result.wkt,
                         'Test normalize ring orientation (2)')

        result = GeomLib.normalizeRingOrientation(self.polygon2)
        self.assertEqual('POLYGON ((0 0, 10 0, 10 90, 100 90, 100 100, 0 100, 0 0))', result.wkt,
                         'Test normalize ring orientation (3)')

        result = GeomLib.normalizeRingOrientation(self.multipolygon)
        self.assertEqual('MULTIPOLYGON (((0 0, 9 0, 9 9, 0 9, 0 0), (3 3, 3 6, 6 6, 6 3, 3 3)), ((100 0, 100 100, 0 100, 100 0)))',
                         result.wkt, 'Test normalize ring orientation (4)')

    def testRemoveHoles(self):
        p = GeomLib.removeHoles(self.polygon)
        self.assertTrue(isinstance(p, Polygon))
        self.assertEqual(81.0, p.area)

        p = GeomLib.removeHoles(self.multipolygon)
        self.assertTrue(isinstance(p, MultiPolygon))
        self.assertEqual(2, len(p.geoms))
        self.assertEqual(5081.0, p.area)

    def testRemoveZCoordinate(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            geom = GeomLib.forceZCoordinateToZ0(geom, z0=12.34)
            self.assertTrue(geom.has_z, 'has_z test (1)')
            result = GeomLib.removeZCoordinate(geom)
            self.assertFalse(result.has_z, 'has_z test (2)')

    def testToListOfBipointsAsLineStrings(self):
        for geom in (self.linestring, self.linearring, self.multilinestring, self.polygon,
                     self.polygon2, self.multipolygon, self.gc):
            result = GeomLib.toListOfBipointsAsLineStrings(geom)
            self.assertIsInstance(result, (list, tuple), 'Test to list of bipoints as linestrings (1)')
            for r in result:
                self.assertIsInstance(r, LineString, 'Test to list of bipoints as linestrings (2)')
                self.assertEqual(2, len(r.coords), 'Test to list of bipoints as linestrings (3)')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
