'''
Created on 18 juin 2020

@author: tleduc
'''
import unittest

from geopandas import GeoDataFrame
from numpy import pi, sqrt
from pandas import Series
from shapely import GeometryCollection, LinearRing, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union
from shapely.wkt import loads
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class GeomLibTest(unittest.TestCase):

    def setUp(self):
        a, b, c, d = (0, 0), (0, 9), (9, 9), (9, 0)

        self.linearring = LinearRing([(100, 0), (100, 100), (0, 100)])

        self.point = Point(a)
        self.multipoint = MultiPoint((a, b, c, d))
        self.linestring = LineString((a, b, c))
        self.multilinestring = MultiLineString([ ((0, 0), (0, 9), (9, 9)), ((3, 3), (6, 3), (6, 6)) ])
        self.polygon = Polygon([a, b, c, d], [[(3, 3), (3, 6), (6, 6), (6, 3)]])
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

    def testExtractFeaturesWithin(self):
        buildings = GeoDataFrameDemos.districtGraslinInNantesBuildings()
        zone = GeoDataFrameDemos.coursCambronneInNantes().geometry.squeeze().buffer(50.0)

        resultat = GeomLib.extractFeaturesWithin(zone, buildings)
        self.assertIsInstance(resultat, GeoDataFrame, 'Is a GeoDataFrame')
        self.assertEqual(96, len(resultat), 'Check GeoDataFrame length')
        self.assertAlmostEqual(17351.1, unary_union(resultat.geometry).area, None,
                               'Tests the resulting area', 0.1)
        """
        import matplotlib.pyplot as plt
        resultat.plot()
        plt.show()
        """

    def testExtractGeometriesWithin(self):
        buildings = GeoDataFrameDemos.districtGraslinInNantesBuildings()
        zone = GeoDataFrameDemos.coursCambronneInNantes().geometry.squeeze().buffer(50.0)

        resultat = GeomLib.extractGeometriesWithin(zone, buildings.geometry)
        self.assertIsInstance(resultat, (MultiPolygon, Polygon), 'Is a single MultiPolygon or Polygon')
        self.assertAlmostEqual(17351.1, resultat.area, None, 'Tests the resulting area', 0.1)
        """
        import matplotlib.pyplot as plt
        GeoDataFrame([{'geometry': resultat}], crs='epsg:2154').plot()
        plt.show()
        """

    def testForceZCoordinateToZ0(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            result = GeomLib.forceZCoordinateToZ0(geom, z0=12.34)
            self.assertTrue(result.has_z, 'has_z test')
            if GeomLib.isMultipart(result):
                self.assertTrue(all(
                    [ 12.34 == p.z  for p in GeomLib.getListOfShapelyPoints(result) ]),
                    'z value test')

    def testFromRayLengthsToPolygon(self):
        result = GeomLib.fromRayLengthsToPolygon([1.0, 1.0, 1.0, 1.0], origin=Point((0.0, 0.0)))
        self.assertIsInstance(result, Polygon, 'Is a Polygon (1)')
        self.assertAlmostEqual(2.0, result.area, None, 'Test Polygon area (1)', 1e-6)

        result = GeomLib.fromRayLengthsToPolygon([1.0] * 64, origin=Point((123.0, 456.0)))
        self.assertIsInstance(result, Polygon, 'Is a Polygon (2)')
        self.assertAlmostEqual(pi, result.area, None, 'Test Polygon area (2)', 1e-2)

    def testFromPolygonToListOfTriangles(self):
        input1 = loads('POLYGON ((0 0, 10 0, 10 10, 0 10, 9 5, 0 0))')
        input2 = loads('POLYGON ((200 100, 200 150, 250 150, 250 200, 200 250, 200 300, 150 300, 150 250, 180 250, 180 200, 150 200, 100 150, 150 150, 200 100))')
        input3 = loads('POLYGON ((353904.8 6695053.6, 353901.3 6695076.9, 353922.4 6695040.6, 353917.4 6695026.8, 353914.5 6695041, 353914.8 6695041.3, 353915 6695041.6, 353915.2 6695042, 353915.3 6695042.2, 353915.4 6695042.6, 353915.4 6695043.6, 353915.3 6695044, 353915.2 6695044.2, 353915 6695044.4, 353914.9 6695044.5, 353914.8 6695044.6, 353904.8 6695053.6))')
        input4 = GeoDataFrameDemos.singleBuildingInNantes().geometry.squeeze()

        for geom in [input1, input2, input3, input4]:
            result = GeomLib.fromPolygonToListOfTriangles(geom)
            self.assertIsInstance(result, list, 'Is a list of triangles (1)')
            self.assertEqual(len(geom.exterior.coords) - 3, len(result), 'Is a list of triangles (2)')
            self.assertAlmostEqual(MultiPolygon(result).area, geom.area, None, 'Test area', 1e-6)

    def testGetEnclosingFeatures(self):
        buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        result = GeomLib.getEnclosingFeatures(buildings, Point((355148, 6689335)))
        self.assertIsInstance(result, list, 'Test if result is a list')
        self.assertEqual(1, len(result), 'Test result length')
        self.assertEqual('BATIMENT0000000302931268', result[0]['ID'], 'Test ID attribute')
        self.assertEqual(21.7, result[0]['HAUTEUR'], 'Test HAUTEUR attribute')

        result = GeomLib.getEnclosingFeatures(buildings, Point((355160, 6689335)))
        self.assertEqual([], result, 'Test if result is an empty list')

    def testGetNearestFeature(self):
        buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
        result = GeomLib.getNearestFeature(buildings, Point((355160, 6689335)))
        self.assertIsInstance(result, list, "Test if result is a list")
        self.assertAlmostEqual(2.78028, result[0], None, "Test minDist", 1e-3)
        self.assertIsInstance(result[1], Point, "Test if nearestPoint is a Shapely Point")
        self.assertIsInstance(result[2], Series, "Test if nearestRow is a Series")

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

    def testIsABorderPoint(self):
        p = loads('MULTIPOLYGON (((0 0, 0 9, 9 9, 9 0, 0 0), (3 3, 3 6, 6 6, 6 3, 3 3)), ((10 0, 19 0, 19 9, 10 0)))')
        buildings = GeoDataFrame([{ 'geometry': p }])

        for pt in [Point((0, 0)), Point((3, 3)), Point((6, 6)), Point((10, 0)), Point((14.5, 4.5))]:
            self.assertTrue(GeomLib.isABorderPoint(pt, buildings), 'Is a border point (1)')

        for pt in [Point((1, 1)), Point((4.5, 4.5)), Point((12, 1))]:
            self.assertFalse(GeomLib.isABorderPoint(pt, buildings), 'Is a border point (2)')

    def testIsAnIndoorPoint(self):
        p1 = Point((0, 0))
        p2 = Point((10, 0))
        buildings = GeoDataFrame([{ 'geometry': p1.buffer(5.0)}])
        self.assertTrue(GeomLib.isAnIndoorPoint(p1, buildings), 'Is an indoor point (1)')
        self.assertFalse(GeomLib.isAnIndoorPoint(p2, buildings), 'Is an indoor point (2)')

    def testIsAnOutdoorPoint(self):
        p = loads('MULTIPOLYGON (((0 0, 0 9, 9 9, 9 0, 0 0), (3 3, 3 6, 6 6, 6 3, 3 3)), ((10 0, 19 0, 19 9, 10 0)))')
        buildings = GeoDataFrame([{ 'geometry': p }])

        for pt in [Point((0, 0)), Point((1, 1)), Point((3, 3)), Point((6, 6)), Point((10, 0)), Point((14.5, 4.5))]:
            self.assertFalse(GeomLib.isAnOutdoorPoint(pt, buildings), 'Is an outdoor point (1)')

        for pt in [Point((4.5, 4.5)), Point((100, 100))]:
            self.assertTrue(GeomLib.isAnOutdoorPoint(pt, buildings), 'Is an outdoor point (2)')

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

    def testProjectOnEdges(self):
        point = Point(5, 5)
        polygon = box(0, 0, 10, 10)
        expected = Point(10, 5)
        actual = GeomLib.projectOnEdges(point, polygon, distToEdge=0, exteriorOnly=True)
        self.assertEqual(expected, actual, 'Test project on edges (1)')

        point = Point(15, 0)
        polygon = box(0, 0, 10, 10)
        expected = Point(15, 0)
        actual = GeomLib.projectOnEdges(point, polygon, distToEdge=0, exteriorOnly=True)
        self.assertEqual(expected, actual, 'Test project on edges (2)')

        point = Point(5, 5)
        polygon = loads("POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0), (1 3, 3 3, 3 1, 1 1, 1 3))")
        expected = Point(3, 3)
        actual = GeomLib.projectOnEdges(point, polygon, distToEdge=0, exteriorOnly=False)
        self.assertEqual(expected, actual, 'Test project on edges (3)')

        point = Point(5, 5)
        polygon = loads("POLYGON ((10 0, 10 10, 0 10, 0 0, 10 0), (1 3, 3 3, 3 1, 1 1, 1 3))")
        expected = Point(3 - 0.5 / sqrt(2), 3 - 0.5 / sqrt(2))
        actual = GeomLib.projectOnEdges(point, polygon, distToEdge=0.5, exteriorOnly=False)
        self.assertEqual(expected, actual, 'Test project on edges (4)')

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

    def testSplitSegmentAccordingToTheDistanceToViewpoint(self):
        # FIRST SET OF TESTS
        segm, viewpt, dist = LineString([[0, 0], [8, 0]]), Point(0, 3), 1.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertListEqual([], result, '[1] Too short distance test')

        segm, viewpt, dist = LineString([[0, 0], [8, 0]]), Point(0, 3), 100.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertListEqual([], result, '[1] Too long distance test')

        segm, viewpt, dist = LineString([[0, 0], [8, 0]]), Point(0, 3), 3.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertIsInstance(result, list, '[1] Single point solution (1)')
        self.assertListEqual([Point([0, 0])], result, '[1] Single point solution (2)')

        segm, viewpt, dist = LineString([[0, 0], [8, 0]]), Point(0, 3), 5.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertIsInstance(result, list, '[1] Single point solution (3)')
        self.assertListEqual([Point([4, 0])], result, '[1] Single point solution (4)')

        segm, viewpt, dist = LineString([[-8, 0], [8, 0]]), Point(0, 3), 5.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertIsInstance(result, list, '[1] Pair of points solution (1)')
        self.assertListEqual([Point([4, 0]), Point([-4, 0])], result, '[1] Pair of points solution (2)')

        # SECOND SET OF TESTS
        segm, viewpt, dist = LineString([[0, 0], [0, 8]]), Point(3, 0), 1.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertListEqual([], result, '[2] Too short distance test')

        segm, viewpt, dist = LineString([[0, 0], [0, 8]]), Point(3, 0), 100.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertListEqual([], result, '[2] Too long distance test')

        segm, viewpt, dist = LineString([[0, 0], [0, 8]]), Point(3, 0), 3.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertIsInstance(result, list, '[2] Single point solution (1)')
        self.assertListEqual([Point([0, 0])], result, '[2] Single point solution (2)')

        segm, viewpt, dist = LineString([[0, 0], [0, 8]]), Point(3, 0), 5.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertIsInstance(result, list, '[2] Single point solution (3)')
        self.assertListEqual([Point([0, 4])], result, '[2] Single point solution (4)')

        segm, viewpt, dist = LineString([[0, -8], [0, 8]]), Point(3, 0), 5.0
        result = GeomLib.splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist)
        self.assertIsInstance(result, list, '[2] Pair of points solution (1)')
        self.assertListEqual([Point([0, 4]), Point([0, -4])], result, '[2] Pair of points solution (2)')

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
