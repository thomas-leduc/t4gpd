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

from geopandas import GeoDataFrame, overlay, sjoin_nearest
from numpy import cos, sin, sqrt, pi
from pandas.core.common import flatten
from shapely.geometry import CAP_STYLE, GeometryCollection, LinearRing, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon
from shapely.ops import nearest_points, transform, unary_union
from shapely.prepared import prep
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.ListUtilities import ListUtilities


class GeomLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def addZCoordinateIfNecessary(obj):
        if GeomLib.isAShapelyGeometry(obj):
            if GeomLib.is3D(obj):
                return obj
            return transform(lambda x, y, z=None: (x, y, 0.0), obj)
        raise IllegalArgumentTypeException(obj, 'Shapely geometry')

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
    def cutsLineStringByCurvilinearDistance(geom, curvDistance):
        if isinstance(geom, LineString):
            if (0 < curvDistance < geom.length):
                # The following instruction is not robust:
                # result = split(geom, geom.interpolate(curvDistance))
                # return list(result.geoms)
                coords = list(geom.coords)
                for i, p in enumerate(coords):
                    pdist = geom.project(Point(p))
                    if (curvDistance == pdist):
                        return [LineString(coords[:i + 1]), LineString(coords[i:])]
                    elif (curvDistance < pdist):
                        cp = geom.interpolate(curvDistance)
                        cp = (cp.x, cp.y, cp.z) if geom.has_z else (cp.x, cp.y)
                        return [
                            LineString(coords[:i] + [cp]),
                            LineString([cp] + coords[i:])]
            return [geom]
        raise IllegalArgumentTypeException(geom, 'LineString')

    @staticmethod
    def distFromTo(a, b):
        dx = b[0] - a[0]
        dy = b[1] - a[1]
        return sqrt(dx * dx + dy * dy)

    @staticmethod
    def dotProduct(u, v):
        return u[0] * v[0] + u[1] * v[1]

    @staticmethod
    def extractFeaturesWithin(zone, inputGdf):
        pzone = prep(zone)

        # outputGdf = inputGdf[pzone.intersects(inputGdf.geometry)].copy(deep=True)
        outputGdf = inputGdf.loc[inputGdf.geometry.apply(
            lambda g: pzone.intersects(g))].copy(deep=True)
        outputGdf.reset_index(drop=True, inplace=True)
        # Use buffers to avoid slivers
        outputGdf.geometry = outputGdf.geometry.apply(
            lambda geom: geom.intersection(zone).buffer(0.001))

        return outputGdf

    @staticmethod
    def extractGeometriesWithin(zone, geometries):
        pzone = prep(zone)
        candidates = list(filter(pzone.intersects, geometries))
        if (0 < len(candidates)):
            result = unary_union(candidates)
            result = result.buffer(0.0)
            result = result.intersection(zone)
            # Use a buffer to avoid slivers
            return result.buffer(0.001)
        return Polygon()

    @staticmethod
    def flattenGeometry(obj):
        def _develop(geom): return [_develop(
            g) for g in geom.geoms] if GeomLib.isMultipart(geom) else [geom]

        if GeomLib.isAShapelyGeometry(obj):
            return list(flatten(_develop(obj)))

        return None

    @staticmethod
    def forceZCoordinateToZ0(obj, z0=0.0):
        if GeomLib.isAShapelyGeometry(obj):
            return transform(lambda x, y, z=None: (x, y, z0), obj)
        raise IllegalArgumentTypeException(obj, 'Shapely geometry')

    @staticmethod
    def fromMultiLineStringToLengths(multiline):
        if not isinstance(multiline, MultiLineString):
            raise IllegalArgumentTypeException(multiline, 'MultiLineString')
            # return []
        return [line.length for line in multiline.geoms]

    @staticmethod
    def fromRayLengthsToPolygon(rayLengths, origin=Point((0.0, 0.0))):
        nRays = len(rayLengths)
        offset = 2 * pi / nRays
        return Polygon([(origin.x + rayLengths[i] * cos(i * offset),
                         origin.y + rayLengths[i] * sin(i * offset)
                         ) for i in range(nRays)])

    @staticmethod
    def fromPolygonToListOfTriangles(polygon):
        if not isinstance(polygon, Polygon):
            raise IllegalArgumentTypeException(polygon, 'Polygon')
        if GeomLib.isHoled(polygon):
            raise Exception(
                'The processing of polygons with holes remains to be developed!')

        p = list(GeomLib.normalizeRingOrientation(
            polygon).exterior.coords)[:-1]
        i, n, result = 0, len(p), []
        while n > 0:
            if (3 >= n):
                result.append(Polygon(p))
                n, p = 0, []
            else:
                i, ip1, ip2 = i % n, (i + 1) % n, (i + 2) % n

                if ((0 <= GeomLib.zCrossProduct(p[i], p[ip1], p[ip2])) and
                        LineString([p[i], p[ip2]]).within(Polygon(p))):
                    result.append(Polygon([p[i], p[ip1], p[ip2]]))
                    del (p[ip1])
                    n = n - 1

                i += 1

        return result

    @staticmethod
    def getEnclosingFeatures(inputGdf, point):
        otherGdf = GeoDataFrame({"geometry": [point]}, crs=inputGdf.crs)
        result = overlay(inputGdf, otherGdf,
                         how="intersection", keep_geom_type=False)
        return result.to_dict("records")

    @staticmethod
    def getCircumcircle(a, b, c):
        if GeomLib.areAligned(a, b, c):
            ab = GeomLib.distFromTo(a, b)
            bc = GeomLib.distFromTo(b, c)
            ca = GeomLib.distFromTo(c, a)
            if Epsilon.EPSILON > min([ab, bc, ca]):
                return [a, 0]
            diam = max([ab, bc, ca])
            if diam == ab:
                return [GeomLib.getMidPoint(a, b), diam / 2.0]
            elif diam == bc:
                return [GeomLib.getMidPoint(b, c), diam / 2.0]
            elif diam == ca:
                return [GeomLib.getMidPoint(c, a), diam / 2.0]
        else:
            line1 = GeomLib.getLineSegmentBisector(a, b)
            line2 = GeomLib.getLineSegmentBisector(b, c)
            center = GeomLib.intersect_line_line(line1, line2)
            return [center, GeomLib.distFromTo(a, center)]

    @staticmethod
    def getInteriorPoint(geom):
        if isinstance(geom, Point):
            return geom
        elif isinstance(geom, Polygon):
            centroid = geom.centroid
            if centroid.within(geom):
                return centroid
            extPts = geom.exterior.coords
            dists = [{'dist': centroid.distance(
                Point(v)), 'v': Point(v)} for v in extPts]
            # dists = sorted(dists, key=lambda l: l['dist'], reverse=True)
            dists = sorted(dists, key=lambda l: l['dist'], reverse=False)

            for q in [dist['v'] for dist in dists]:
                p = Point((centroid.x + q.x) / 2.0, (centroid.y + q.y) / 2.0)
                while not p.within(geom):
                    if (0.5 > p.distance(q)):
                        break
                    p = Point((p.x + q.x) / 2.0, (p.y + q.y) / 2.0)
                if p.within(geom):
                    return p
            return dists[0]['v']
        raise Exception(
            'GeomLib.getInteriorPoint(...): implementation to be continued!')

    @staticmethod
    def getLineSegmentBisector(a, b):
        # The resulting line is represented by a point and a vector
        ab = GeomLib.vector_to(a, b)
        c = GeomLib.getMidPoint(a, b)
        return [c, [-ab[1], ab[0]]]

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
    def getListOfShapelyPoints(obj, withoutClosingLoops=False):
        if isinstance(obj, Point):
            return [obj]
        elif isinstance(obj, LineString):
            if withoutClosingLoops and (obj.coords[0] == obj.coords[-1]):
                return [Point(p) for p in obj.coords[:-1]]
            return [Point(p) for p in obj.coords]
        elif isinstance(obj, Polygon):
            result = GeomLib.getListOfShapelyPoints(
                obj.exterior, withoutClosingLoops)
            for ring in obj.interiors:
                result += GeomLib.getListOfShapelyPoints(
                    ring, withoutClosingLoops)
            return result
        elif GeomLib.isMultipart(obj):
            return reduce(lambda a, b: a + b, [GeomLib.getListOfShapelyPoints(g, withoutClosingLoops) for g in obj.geoms])
        raise IllegalArgumentTypeException(obj, 'Shapely geometry')

    @staticmethod
    def getMidPoint(a, b):
        return [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0]

    @staticmethod
    def getNearestFeature(inputGdf, point):
        if not isinstance(point, Point):
            raise IllegalArgumentTypeException(point, "Point")

        otherGdf = GeoDataFrame({"geometry": [point]}, crs=inputGdf.crs)
        tmp = sjoin_nearest(inputGdf, otherGdf, distance_col="dist_to_pt")
        nearestRow = tmp.loc[tmp.dist_to_pt.idxmin()]
        minDist = nearestRow.dist_to_pt
        nearestPoint = nearest_points(point, nearestRow.geometry)[1]

        return [minDist, nearestPoint, nearestRow]

    @staticmethod
    def getNearestFeature3(gdf, point, buffDist, incScale=sqrt(2)):
        if not isinstance(point, Point):
            raise IllegalArgumentTypeException(point, 'Point')

        minDist, nearestPoint, nearestRow = float('inf'), None, None

        candidates = []
        while (0 == len(candidates)):
            pzone = prep(point.buffer(buffDist, cap_style=CAP_STYLE.square))
            # candidates = gdf[pzone.intersects(gdf.geometry)].copy(deep=True)
            candidates = gdf.loc[gdf.geometry.apply(
                lambda g: pzone.intersects(g))].copy(deep=True)
            buffDist *= incScale

        for _, row in candidates.iterrows():
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
    def hashCoords(x, y, z=0):
        _hash = 17
        _hash = 37 * _hash + hash(x)
        _hash = 37 * _hash + hash(y)
        _hash = 37 * _hash + hash(z)
        return _hash

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
        return GeomLib.isAShapelyGeometry(obj) and obj.has_z

    @staticmethod
    def getAnchoringBuildingId(point, buildings, spatialIndex):
        # isAnAnchoringPolygon = isABorderPoint OR isAnInsidePoint
        def isAnAnchoringPolygon(point, polygon): return (
            point.relate(polygon) in ['F0FFFF212', '0FFFFF212'])
        buildingsIds = list(spatialIndex.intersection(point.bounds))
        for buildingId in buildingsIds:
            buildingGeom = buildings.loc[buildingId].geometry
            if isAnAnchoringPolygon(point, buildingGeom):
                return buildingId
        return None

    @staticmethod
    def getAnchoringBuildingId3(point, buildings):
        # isAnAnchoringPolygon = isABorderPoint OR isAnInsidePoint
        def isAnAnchoringPolygon(point, polygon): return (
            point.relate(polygon) in ['F0FFFF212', '0FFFFF212'])

        pgeom = prep(point.buffer(0.1, cap_style=CAP_STYLE.square))
        # gdf = buildings[pgeom.intersects(buildings.geometry)]
        gdf = buildings.loc[buildings.geometry.apply(
            lambda g: pgeom.intersects(g))]
        gdf = gdf.loc[gdf.geometry.apply(
            lambda g: isAnAnchoringPolygon(point, g))]

        return gdf.index[0] if (0 < len(gdf)) else None

    @staticmethod
    def isABorderPoint(point, buildings):
        def isAPointOnTheBorder(point, polygon): return (
            'F0FFFF212' == point.relate(polygon))
        pgeom = prep(point.buffer(0.1, cap_style=CAP_STYLE.square))
        candidates = filter(pgeom.intersects, buildings.geometry)
        for candidate in candidates:
            if isAPointOnTheBorder(point, candidate):
                return True
        return False

    @staticmethod
    def isAnIndoorPoint(point, buildings):
        def isAnInsidePoint(point, polygon): return (
            '0FFFFF212' == point.relate(polygon))
        pgeom = prep(point.buffer(0.1, cap_style=CAP_STYLE.square))
        candidates = filter(pgeom.intersects, buildings.geometry)
        for candidate in candidates:
            if isAnInsidePoint(point, candidate):
                return True
        return False

    @staticmethod
    def isAnOutdoorPoint(point, buildings):
        def isAnOutsidePoint(point, polygon): return (
            'FF0FFF212' == point.relate(polygon))
        pgeom = prep(point.buffer(0.1, cap_style=CAP_STYLE.square))
        candidates = filter(pgeom.intersects, buildings.geometry)
        for candidate in candidates:
            if not isAnOutsidePoint(point, candidate):
                return False
        return True

    @staticmethod
    def isAShapelyGeometry(obj):
        return isinstance(obj, (GeometryCollection, LineString, MultiLineString,
                                MultiPoint, MultiPolygon, Point, Polygon))

    @staticmethod
    def isCCW(ring):
        return (0 < GeomLib.ringSignedArea(ring))

    @staticmethod
    def isConvex(obj):
        if isinstance(obj, Polygon) and not GeomLib.isHoled(obj):
            coords = list(obj.exterior.coords)[:-1]
            if 3 >= len(coords):
                return True
            signs = [GeomLib.zCrossProduct(a, b, c) > 0 for a, b, c in zip(
                ListUtilities.rotate(coords, 2), ListUtilities.rotate(coords, 1), coords)]
            return all(signs) or not any(signs)
        return False

    @staticmethod
    def isHoled(obj):
        return (isinstance(obj, Polygon) and (0 < len(obj.interiors)))

    @staticmethod
    def isInFrontOf(viewpoint, bipointAsLinestring):
        if not isinstance(viewpoint, Point):
            raise IllegalArgumentTypeException(viewpoint, 'Point')
        if (not isinstance(bipointAsLinestring, LineString) or
                (2 != len(bipointAsLinestring.coords))):
            raise IllegalArgumentTypeException(
                bipointAsLinestring, 'LineString of 2 points')
        a, b = bipointAsLinestring.coords
        ab = GeomLib.vector_to(a, b)
        n2ab = [ab[1], -ab[0]]
        ca = GeomLib.vector_to((viewpoint.x, viewpoint.y), a)
        return (GeomLib.dotProduct(n2ab, ca) < 0)

    @staticmethod
    def isLineal(obj):
        return isinstance(obj, (MultiLineString, LinearRing, LineString))

    @staticmethod
    def isMultipart(obj):
        return isinstance(obj, (GeometryCollection, MultiLineString, MultiPoint,
                                MultiPolygon))

    @staticmethod
    def isPolygonal(obj):
        return isinstance(obj, (MultiPolygon, Polygon))

    @staticmethod
    def isPuntal(obj):
        return isinstance(obj, (MultiPoint, Point))

    @staticmethod
    def normalizeRingOrientation(obj, ccw=True):
        # All exterior/interiors rings must be CCW oriented
        if (isinstance(obj, LineString) and obj.is_ring):
            _orientation = GeomLib.isCCW(obj)
            if (ccw == _orientation):
                return obj
            return LinearRing(reversed(obj.coords))

        elif isinstance(obj, Polygon):
            extRing = GeomLib.normalizeRingOrientation(obj.exterior, ccw)
            intRings = [GeomLib.normalizeRingOrientation(
                hole, not ccw) for hole in obj.interiors]
            return Polygon(extRing, intRings)

        elif isinstance(obj, MultiLineString):
            result = []
            for geom in obj.geoms:
                result.append(GeomLib.normalizeRingOrientation(geom, ccw))
            return MultiLineString(result)

        elif isinstance(obj, MultiPolygon):
            result = []
            for geom in obj.geoms:
                result.append(GeomLib.normalizeRingOrientation(geom, ccw))
            return MultiPolygon(result)

    @staticmethod
    def projectOntoStraightLine(p, line):
        # This method returns the projection 'projP' of point p on the
        # given line but also the distance from p to the given line
        # ('distFromPToLine') and the distance from the projection
        # 'projP' to the first point of the input line. The input
        # line is represented by two points.
        a, b = line
        ap = GeomLib.vector_to(a, p)
        unitAB = GeomLib.unitVector(a, b)
        orthoUnitAB = [-unitAB[1], unitAB[0]]
        distFromAToProjP = GeomLib.dotProduct(ap, unitAB)
        projP = [a[0] + distFromAToProjP * unitAB[0],
                 a[1] + distFromAToProjP * unitAB[1]]
        distFromPToLine = GeomLib.dotProduct(ap, orthoUnitAB)
        return [projP, distFromAToProjP, distFromPToLine]

    @staticmethod
    def removeHoles(obj):
        if isinstance(obj, Polygon):
            return Polygon(obj.exterior)
        elif isinstance(obj, MultiPolygon):
            return MultiPolygon([Polygon(p.exterior) for p in obj.geoms])
        return None
        # raise IllegalArgumentTypeException(obj, 'Polygon or MultiPolygon')

    @staticmethod
    def removeZCoordinate(obj):
        if GeomLib.isAShapelyGeometry(obj):
            return transform(lambda x, y, z=None: (x, y), obj)
        raise IllegalArgumentTypeException(obj, 'Shapely geometry')

    @staticmethod
    def reverseRingOrientation(obj):
        # if (isinstance(obj, LineString) and obj.is_ring):
        if isinstance(obj, LineString):
            return LineString(reversed(obj.coords))

        elif isinstance(obj, Polygon):
            extRing = GeomLib.reverseRingOrientation(obj.exterior)
            intRings = [GeomLib.reverseRingOrientation(
                hole) for hole in obj.interiors]
            return Polygon(extRing, intRings)

        elif isinstance(obj, MultiLineString):
            result = []
            for geom in obj.geoms:
                result.append(GeomLib.reverseRingOrientation(geom))
            return MultiLineString(result)

        elif isinstance(obj, MultiPolygon):
            result = []
            for geom in obj.geoms:
                result.append(GeomLib.reverseRingOrientation(geom))
            return MultiPolygon(result)

    @staticmethod
    def ringSignedArea(ring):
        # https://en.wikipedia.org/wiki/Shoelace_formula
        if (isinstance(ring, LineString)):  # and ring.is_ring):
            ring = ring.coords
            area = 0.0
            if len(ring) < 3:
                return area
            x1, y1 = ring[0][0:2]
            for xyz in ring[1:]:
                x2, y2 = xyz[0:2]
                area += (x1 * y2 - x2 * y1)
                x1, y1 = x2, y2
            return area / 2.0
        raise IllegalArgumentTypeException(ring, 'LineString')

    @staticmethod
    def splitSegmentAccordingToTheDistanceToViewpoint(segm, viewpt, dist):
        if not (isinstance(segm, LineString) and (2 == len(segm.coords))):
            raise IllegalArgumentTypeException(segm, '2-point LineString')
        if not isinstance(viewpt, Point):
            raise IllegalArgumentTypeException(viewpt, 'Point')
        p0, p1 = segm.coords

        # CHECK IF THE RESULTING POINT IS ON THE SEGMENT
        _maxDist = max(viewpt.distance(Point(p0)), viewpt.distance(Point(p1)))
        if ((dist < viewpt.distance(segm)) or (_maxDist < dist)):
            return []

        # LET'S SOLVE THE FOLLOWING SYSTEM:
        # x = x0 + (x1 - x0) * t
        # y = y0 + (y1 - y0) * t
        # (x - xv)**2 + (y - yv)**2 = dist**2
        # 0 <= t <= 1
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        vx, vy = p0[0] - viewpt.x, p0[1] - viewpt.y

        a = (dx * dx + dy * dy)
        b = 2 * (dx * vx + dy * vy)
        c = (vx * vx + vy * vy - dist * dist)
        discr = b * b - 4 * a * c

        if (0 < discr):
            t1 = (-b + sqrt(discr)) / (2 * a)
            t2 = (-b - sqrt(discr)) / (2 * a)

            result = []
            if (0 <= t1 <= 1):
                result.append(Point([p0[0] + dx * t1, p0[1] + dy * t1]))
            if (0 <= t2 <= 1):
                result.append(Point([p0[0] + dx * t2, p0[1] + dy * t2]))
            return result

        elif (0 == discr):
            t0 = -b / (2 * a)
            if (0 <= t0 <= 1):
                return [Point([p0[0] + dx * t0, p0[1] + dy * t0])]

        raise Exception('Unreachable instruction!')

    @staticmethod
    def toListOfLineStrings(obj):
        if GeomLib.isAShapelyGeometry(obj) and (not GeomLib.isPuntal(obj)):
            if isinstance(obj, LinearRing):
                return [LineString(obj.coords)]
            elif isinstance(obj, LineString):
                return [obj]
            elif isinstance(obj, Polygon):
                result = [LineString(obj.exterior.coords)]
                for r in obj.interiors:
                    result.append(LineString(r.coords))
                return result
            elif GeomLib.isMultipart(obj):
                result = []
                for g in obj.geoms:
                    result += GeomLib.toListOfLineStrings(g)
                return result
        return []

    @staticmethod
    def toListOfBipointsAsLineStrings(obj):
        result = []
        for geom in GeomLib.toListOfLineStrings(obj):
            prev = None
            for curr in geom.coords:
                if not prev is None:
                    result.append(LineString([prev, curr]))
                prev = curr
        return result

    @staticmethod
    def toListOfBipointsAsLineStringsInFrontOf(viewpoint, obj):
        if not isinstance(viewpoint, Point):
            raise IllegalArgumentTypeException(viewpoint, "Point")
        if not GeomLib.isPolygonal(obj):
            raise IllegalArgumentTypeException(
                obj, "Polygon or MultiPolygon")
        segments = GeomLib.toListOfBipointsAsLineStrings(obj)
        segments = [
            segm for segm in segments if GeomLib.isInFrontOf(viewpoint, segm)]
        return segments

    @staticmethod
    def toListOfPolygons(obj):
        if GeomLib.isAShapelyGeometry(obj):
            if isinstance(obj, Polygon):
                return [obj]
            elif isinstance(obj, MultiPolygon):
                return obj.geoms
            elif isinstance(obj, GeometryCollection):
                result = []
                for g in obj.geoms:
                    result += GeomLib.toListOfPolygons(g)
                return result
        return []

    @staticmethod
    def toMultiPolygon(obj):
        if GeomLib.isAShapelyGeometry(obj):
            if isinstance(obj, Polygon):
                return MultiPolygon([obj])
            elif isinstance(obj, MultiPolygon):
                return obj
            elif isinstance(obj, GeometryCollection):
                return MultiPolygon(GeomLib.toListOfPolygons(obj))
        return MultiPolygon()

    @staticmethod
    def unitVector(a, b):
        ab = GeomLib.vector_to(a, b)
        invNorm = 1.0 / sqrt(ab[0] * ab[0] + ab[1] * ab[1])
        return [ab[0] * invNorm, ab[1] * invNorm]

    @staticmethod
    def vector_to(a, b):
        return [b[0] - a[0], b[1] - a[1]]

    @staticmethod
    def zCrossProduct(a, b, c):
        return (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
