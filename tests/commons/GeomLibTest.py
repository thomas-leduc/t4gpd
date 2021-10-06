'''
Created on 18 juin 2020

@author: tleduc
'''
import unittest

from shapely.geometry import GeometryCollection, LinearRing, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon

from t4gpd.commons.GeomLib import GeomLib


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
        self.polygon = Polygon((a, b, c, d), [[(3, 3), (6, 3), (6, 6), (3, 6)]])
        self.multipolygon = MultiPolygon((self.polygon, Polygon(self.linearring)))
        
        self.gc = GeometryCollection([self.point, self.linestring, self.polygon])

    def tearDown(self):
        pass

    def testGetListOfShapelyPoints(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            result = GeomLib.getListOfShapelyPoints(geom)
            self.assertTrue(isinstance(GeomLib.getListOfShapelyPoints(geom), (list, tuple)))
            for pt in result:
                self.assertTrue(isinstance(pt, Point))

    def testIsAShapelyGeometry(self):
        for geom in [self.point, self.linearring, self.linestring, self.polygon,
                     self.multipoint, self.multilinestring, self.multipolygon, self.gc]:
            self.assertTrue(GeomLib.isAShapelyGeometry(geom))

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

    def testRemoveHoles(self):
        p = GeomLib.removeHoles(self.polygon)
        self.assertTrue(isinstance(p, Polygon))
        self.assertEqual(81.0, p.area)

        p = GeomLib.removeHoles(self.multipolygon)
        self.assertTrue(isinstance(p, MultiPolygon))
        self.assertEqual(2, len(p.geoms))
        self.assertEqual(5081.0, p.area)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
