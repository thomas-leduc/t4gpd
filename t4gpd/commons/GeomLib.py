'''
Created on 15 juin 2020

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
from functools import reduce
from shapely.ops import nearest_points

from numpy import sqrt, pi
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon

from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class GeomLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def areCollinear(u, v, epsilon=Epsilon.EPSILON):
        return Epsilon.isZero(GeomLib.crossProduct(u, v), epsilon)

    @staticmethod
    def areAligned(a, b, c, epsilon=Epsilon.EPSILON):
        ab = GeomLib.vector_to(a, b)
        ac = GeomLib.vector_to(a, c)
        return GeomLib.areCollinear(ab, ac, epsilon)

    @staticmethod
    def crossProduct(u, v):
        return [0.0, 0.0, u[0] * v[1] - u[1] * v[0]]

    @staticmethod
    def distFromTo(a, b):
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        return sqrt(dx * dx + dy * dy)

    @staticmethod
    def dotProduct(u, v):
        return u[0] * v[0] + u[1] * v[1]

    @staticmethod
    def fromMultiLineStringToLengths(multiline):
        if not isinstance(multiline, MultiLineString):
            raise IllegalArgumentTypeException(multiline, 'MultiLineString')
            # return []
        return [line.length for line in multiline.geoms]

    @staticmethod
    def getLineSegmentBisector(a, b):
        # The resulting line is represented by a point and a vector
        ab = GeomLib.vector_to(a, b)
        c = GeomLib.getMidPoint(a, b)
        return [ c, [-ab[1], ab[0]] ]

    @staticmethod
    def getLineStringOrientation(line):
        if not isinstance(line, LineString):
            raise IllegalArgumentTypeException(line, 'LineString')

        coords = list(line.coords)
        a, b = Point(coords[0]), Point(coords[-1])
        meanDir = (b.x - a.x, b.y - a.y)
        azimuth = AngleLib.normAzimuth(meanDir)
        if azimuth > pi:
            azimuth -= pi
        return AngleLib.toDegrees(azimuth)

    @staticmethod
    def getListOfShapelyPoints(obj):
        if isinstance(obj, Point):
            return [obj]
        elif isinstance(obj, LineString):
            return [Point(p) for p in obj.coords]
        elif isinstance(obj, Polygon):
            result = GeomLib.getListOfShapelyPoints(obj.exterior)
            for ring in obj.interiors:
                result += GeomLib.getListOfShapelyPoints(ring)
            return result
        elif GeomLib.isMultipart(obj):
            return reduce(lambda a, b: a + b, [GeomLib.getListOfShapelyPoints(g) for g in obj.geoms])            
        raise IllegalArgumentTypeException(obj, 'Shapely geometry')

    @staticmethod
    def getMidPoint(a, b):
        return [ (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0 ]

    @staticmethod
    def getNearestFeature(inputGdf, inputSpatialIndex, point, buffDist, incScale=sqrt(2)):
        if not isinstance(point, Point):
            raise IllegalArgumentTypeException(point, 'Point')

        minDist, nearestPoint, nearestRow = float('inf'), None, None

        ids = []
        while (0 == len(ids)):
            ids = list(inputSpatialIndex.intersection(point.buffer(buffDist, -1).bounds))
            buffDist *= incScale

        for _id in ids:
            row = inputGdf.loc[_id]
            rowGeom = row.geometry
            dist = point.distance(rowGeom)
            if (dist < minDist):
                minDist = dist
                _, nearestPoint = nearest_points(point, rowGeom)
                nearestRow = row

        return [minDist, nearestPoint, nearestRow]

    @staticmethod
    def getStraightLineEquation(line):
        # The input line is represented by a point and a vector
        # The output result is [a, b, c] 
        # where a * x + b * y + c = 0
        point, vector = line
        a = vector[1]
        b = -vector[0]
        c = -a * point[0] - b * point[1]
        return [a, b, c]

    @staticmethod
    def intersect_line_line(line1, line2):
        # The input lines are both represented by a point and a vector
        a1, b1, c1 = GeomLib.getStraightLineEquation(line1)
        a2, b2, c2 = GeomLib.getStraightLineEquation(line2)
        det = a1 * b2 - a2 * b1
        if (0.0 == det):
            return None
        return [(b1 * c2 - b2 * c1) / det, (a2 * c1 - a1 * c2) / det]

    @staticmethod
    def is3D(obj):
        if GeomLib.isAShapelyGeometry(obj):
            for coords in obj.coords:
                if (3 == len(coords)):
                    return True
        return False

    @staticmethod
    def isAShapelyGeometry(obj):
        return isinstance(obj, (GeometryCollection, LineString, MultiLineString,
                                MultiPoint, MultiPolygon, Point, Polygon))

    @staticmethod
    def isCCW(ring):
        return (0 < GeomLib.ringSignedArea(ring))

    @staticmethod
    def isMultipart(obj):
        return isinstance(obj, (GeometryCollection, MultiLineString, MultiPoint,
                                MultiPolygon))

    @staticmethod
    def isPolygonal(obj):
        return isinstance(obj, (MultiPolygon, Polygon))

    @staticmethod
    def removeHoles(obj):
        if isinstance(obj, Polygon):
            return Polygon(obj.exterior)
        elif isinstance(obj, MultiPolygon):
            return MultiPolygon([Polygon(p.exterior) for p in obj.geoms])
        return None
        # raise IllegalArgumentTypeException(obj, 'Polygon or MultiPolygon')

    @staticmethod
    def ringSignedArea(ring):
        # https://en.wikipedia.org/wiki/Shoelace_formula
        if (isinstance(ring, LineString) and ring.is_ring):
            ring = ring.coords
        area = 0.0
        if len(ring) < 3:
            return area
        x1, y1 = ring[0]
        for x2, y2 in ring[1:]:
            area += (x1 * y2 - x2 * y1)
            x1, y1 = x2, y2
        return area / 2.0

    @staticmethod
    def unitVector(a, b):
        ab = GeomLib.vector_to(a, b)
        invNorm = 1.0 / sqrt(ab[0] * ab[0] + ab[1] * ab[1])
        return [ab[0] * invNorm, ab[1] * invNorm]

    @staticmethod
    def vector_to(a, b):
        return [b[0] - a[0], b[1] - a[1]]
