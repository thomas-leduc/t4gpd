'''
Created on 15 dec. 2020

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
from shapely.geometry import LineString, Polygon

from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class CaliperLib(object):
    '''
    classdocs
    '''

    def __init__(self, criteria=None):
        '''
        Constructor
        '''
        if criteria in (None, 'min', 'max'):
            self.maximize = True if criteria in [None, 'max'] else False
        else:
            raise IllegalArgumentTypeException(criteria, '{None, "min", "max"}')

    @staticmethod
    def __getDistanceToAntipodalVertex(pairOfVertices, vertices):
        listOfQuintuplets = CaliperLib.__getListOfQuintuplets(pairOfVertices, vertices)
        return max([dist for _, _, _, _, dist in listOfQuintuplets])

    @staticmethod
    def __getListOfQuintuplets(pairOfVertices, vertices):
        result = list()
        for vertex in vertices:
            # projP, distFromAToProjP, distFromPToLine = GeomUtilities.projectOntoStraightLine(vertex, pairOfVertices)
            result.append([vertex, pairOfVertices] + GeomLib.projectOntoStraightLine(vertex, pairOfVertices))
        return result

    @staticmethod
    def __getListOfListOfQuintuplets(geom):
        vertices, nVertices = CaliperLib.__preprocess(geom)
        result = list()
        for i in range(nVertices):
            nextI = (i + 1) % nVertices
            v1, v2 = vertices[i], vertices[nextI]
            result.append(CaliperLib.__getListOfQuintuplets([v1, v2], vertices))
        return result

    @staticmethod
    def __getListOfMaxOfQuintuplets(geom):
        listOfListOfQuintuplets = CaliperLib.__getListOfListOfQuintuplets(geom)
        result = list()
        for listOfQuintuplets in listOfListOfQuintuplets:
            maxDist = -1.0
            for quintuplet in listOfQuintuplets:
                if (maxDist < quintuplet[4]):
                    maxDist, currResult = quintuplet[4], quintuplet
            result.append(currResult)
        return result

    @staticmethod
    def __getEnclosingRectangle(pairOfVertices, vertices):
        listOfQuintuplets = CaliperLib.__getListOfQuintuplets(pairOfVertices, vertices)

        a, b = pairOfVertices
        u = GeomLib.unitVector(a, b)
        v = [-u[1], u[0]]

        minDu = min([distFromAToProjP for _, _, _, distFromAToProjP, _ in listOfQuintuplets])
        maxDu = max([distFromAToProjP for _, _, _, distFromAToProjP, _ in listOfQuintuplets])
        maxDv = max([distFromPToLine for _, _, _, _, distFromPToLine in listOfQuintuplets])

        p1 = [ a[0] + u[0] * minDu, a[1] + u[1] * minDu ]
        p2 = [ a[0] + u[0] * maxDu, a[1] + u[1] * maxDu ]
        p3 = [ p2[0] + v[0] * maxDv, p2[1] + v[1] * maxDv ]
        p4 = [ p1[0] + v[0] * maxDv, p1[1] + v[1] * maxDv ]

        return [Polygon([p1, p2, p3, p4, p1]), max(maxDu - minDu, maxDv), min(maxDu - minDu, maxDv)]

    @staticmethod
    def __getAntipodalVertex(pairOfVertices, vertices):
        listOfQuintuplets = CaliperLib.__getListOfQuintuplets(pairOfVertices, vertices)

        maxDist, result = -1.0, None
        for p, _, _, _, distFromPToLine in listOfQuintuplets:
            if (maxDist < distFromPToLine):
                maxDist, result = distFromPToLine, p
        return maxDist, result

    @staticmethod
    def __getDistances(geom):
        listOfListOfQuintuplets = CaliperLib.__getListOfListOfQuintuplets(geom)
        distances = [
            max([dist for _, _, _, _, dist in listOfQuintuplets])
            for listOfQuintuplets in listOfListOfQuintuplets
            ]
        return distances

    @staticmethod
    def __preprocess(geom):
        convexHull = geom.convex_hull
        if convexHull is None:
            return None, 0
        # vertices = list(convexHull.exterior.coords)[:-1]  # Clockwise order
        vertices = list(reversed(list(convexHull.exterior.coords)[:-1]))  # Counter-clockwise order
        return vertices, len(vertices)

    def diameter(self, geom):
        listOfMaxOfQuintuplets = CaliperLib.__getListOfMaxOfQuintuplets(geom)

        pairOfVertices, oppVertex, projOppVertex = None, None, None
        if self.maximize:
            maxDist = -1.0
            for p, pairOfV, projP, _, dist in listOfMaxOfQuintuplets:
                if (maxDist < dist):
                    maxDist, pairOfVertices, oppVertex, projOppVertex = dist, pairOfV, p, projP
        else:
            minDist = float('inf')
            for p, pairOfV, projP, _, dist in listOfMaxOfQuintuplets:
                if (minDist > dist):
                    minDist, pairOfVertices, oppVertex, projOppVertex = dist, pairOfV, p, projP
        # return [pairOfVertices, [oppVertex, projOppVertex]]
        return [oppVertex, projOppVertex]

    def length(self, geom):
        distances = CaliperLib.__getDistances(geom)
        if self.maximize:
            return max(distances)
        return min(distances)

    def orientation(self, geom):
        pairOfVertices = self.diameter(geom)
        if pairOfVertices is None:
            return None
        segment = LineString(pairOfVertices)
        return float(GeomLib.getLineStringOrientation(segment))

    @staticmethod
    def stretching(geom):
        distances = CaliperLib.__getDistances(geom)
        minDist, maxDist = min(distances), max(distances)
        if (0.0 >= maxDist):
            return None
        return float(minDist / maxDist)

    @staticmethod
    def getBoundingRectangles(geom):
        vertices, nVertices = CaliperLib.__preprocess(geom)
        result = list()
        for i in range(nVertices):
            nextI = (i + 1) % nVertices
            v1, v2 = vertices[i], vertices[nextI]
            result.append(CaliperLib.__getEnclosingRectangle([v1, v2], vertices))
        return result

    @staticmethod
    def mabr(geom):
        rectangles = CaliperLib.getBoundingRectangles(geom)
        minArea, result = float('inf'), None
        for rect, len1, len2 in rectangles:
            currArea = len1 * len2
            if currArea < minArea:
                minArea = currArea
                result = [rect, len1, len2]
        return result

    @staticmethod
    def mpbr(geom):
        rectangles = CaliperLib.getBoundingRectangles(geom)
        minHalfPerim, result = float('inf'), None
        for rect, len1, len2 in rectangles:
            currHalfPerim = len1 + len2
            if currHalfPerim < minHalfPerim:
                minHalfPerim = currHalfPerim
                result = [rect, len1, len2]
        return result
