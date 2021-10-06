'''
Created on 23 juin 2020

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
from geopandas.geodataframe import GeoDataFrame
import itertools

from numpy import arccos, arctan2, array, cos, dot, flip, imag, log, matmul, ones, pi, polyadd, polyder, polymul, polyval, real, sin, sqrt, zeros
from numpy.linalg import cond, det, LinAlgError, solve, inv  # VARIANTE: from scipy.linalg import cond, det, inv, solve
from numpy.polynomial.polynomial import polyroots
from shapely.geometry import MultiPoint, Point

from t4gpd.commons.BoundingBox import BoundingBox
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.ellipse.EllipseLib import EllipseLib


class EllipticHullLib(object):
    '''
    classdocs
    '''

    def __init__(self, threshold=None, debug=False):
        '''
        Constructor
        '''
        self.threshold = threshold
        self.debug = debug

    def getMinimumAreaBoundingEllipse(self, qgsGeom):
        return self.getMinimumBoundingEllipse(qgsGeom, constraint='area')

    def getMinimumPerimeterBoundingEllipse(self, qgsGeom):
        return self.getMinimumBoundingEllipse(qgsGeom, constraint='perimeter')

    def getMinimumBoundingEllipse(self, geom, constraint='area'):
        if not GeomLib.isAShapelyGeometry(geom):
            raise IllegalArgumentTypeException(geom, 'Shapely geometry')
        coords = geom.convex_hull.exterior.coords[:-1]  # Clockwise order
        # coords = list(reversed(geom.convex_hull.exterior.coords[:-1]))  # Counter-clockwise order

        bbox = BoundingBox(geom)
        magnitude = 1.0 / max(bbox.width(), bbox.height())
        invMagnitude = 1.0 / magnitude

        if (self.debug):
            print('Nb sommets env. conv. : %d' % len(coords))
            print('\t[%s]' % '; '.join(['%.5f, %.5f' % (x, y) for x, y in coords])) 
            EllipticHullLib.__layerOfNodes(coords, 'convex hull', 'cross', 'black', '4.2')

        coords = EllipticHullLib.flatEdgesPruning(coords, self.threshold)
        if (self.debug):
            print('Nb sommets env. conv. simplifiee : %d' % len(coords))
            EllipticHullLib.__layerOfNodes(coords, 'simple convex hull', 'pentagon', 'red', '1.8')

        orderedIndices, centroid = EllipticHullLib.orderNodesAndIdentifyTheCentroid(coords)

        coords = EllipticHullLib.homotheticTransformation(EllipticHullLib.translateNodes(coords, [-centroid[0], -centroid[1]]), magnitude)

        if ('area' == constraint):
            nodes, centre, semiXAxis, semiYAxis, azim, methName = self.__getMinimumAreaBoundingEllipseAux(coords, orderedIndices)
        elif ('perimeter' == constraint):
            nodes, centre, semiXAxis, semiYAxis, azim, methName = self.__getMinimumPerimeterBoundingEllipseAux(coords, orderedIndices)
        else:
            raise Exception('The "constraint" parameter value must be chosen among [area, perimeter]!')
        centre = EllipticHullLib.translateNodes(EllipticHullLib.homotheticTransformation([centre], invMagnitude), centroid)[0]
        semiXAxis, semiYAxis = invMagnitude * semiXAxis, invMagnitude * semiYAxis 

        nodes = EllipticHullLib.translateNodes(EllipticHullLib.homotheticTransformation(nodes, invMagnitude), centroid)

        '''
        if (self.debug):
            semiAxis = semiXAxis if (semiXAxis >= semiYAxis) else semiYAxis
            p1 = Point((centre[0] - semiAxis * cos(azim), centre[1] - semiAxis * sin(azim)))
            p2 = Point((centre[0] + semiAxis * cos(azim), centre[1] + semiAxis * sin(azim)))

            memDriver = MemoryDriver('LineString', 'main axis', [], crs=QgsCoordinateReferenceSystem(2154))
            memDriver.addFeatures([ {'the_geom': [ p1, p2 ]} ])
            layer = memDriver.getVectorLayer()
            setLineSymbol(layer, color='green', penstyle='dot', width='0.35')
            structLayer = EllipticHullLib.__layerOfNodes(nodes, 'structuring nodes', 'circle', 'blue', '3.2')
            setLabelSymbol(structLayer, 'gid', overPoint=False, size='24', color='black')
            print('\ncentre = {:.5f}, {:.5f}, semiXAxis = {:.5f}, semiYAxis = {:.5f}, azim = {:.5f}, methName = {:s}'.format(centre[0], centre[1], semiXAxis, semiYAxis, azim, methName))
            print('\tnodes = [%s]' % (', '.join(['({:.5f}, {:.5f})'.format(x, y) for x, y in nodes])))
            print('\tarea = %.5f, perimeter = %.5f' % (pi * semiXAxis * semiYAxis, EllipseUtilities.getEllipsePerimeter(semiXAxis, semiYAxis)))
        '''

        return [Point(centre), semiXAxis, semiYAxis, azim, nodes, methName]

    def __getMinimumAreaBoundingEllipseAux(self, coords, orderedIndices, epsilon=Epsilon.EPSILON):
        ncoords = len(coords)
        allIndices = list(range(ncoords))

        if 3 <= ncoords:
            cnt = 0
            for indices in itertools.combinations(allIndices, 3):
                cnt += 1
                [A, B, C], pivots, centre, methName = self.__aux(coords, orderedIndices, indices)
                if EllipticHullLib.areInside(coords, centre, A, B, C, epsilon):
                    semiXAxis, semiYAxis, azim = EllipticHullLib.getSemiAxesAndAzim([A, B, C])   
                    return [pivots, centre, semiXAxis, semiYAxis, azim, methName]

        maxInvAreaMulSquarePi, solution = float('-inf'), None
        if 4 <= ncoords:
            cnt = 0
            for indices in list(itertools.combinations(allIndices, 4)) + list(itertools.combinations(allIndices, 5)):
                cnt += 1
                result = self.__aux(coords, orderedIndices, indices)
                if result is None:
                    continue
                [A, B, C], pivots, centre, methName = result
                currInvAreaMulSquarePi = 4 * A * C - B * B
                if (maxInvAreaMulSquarePi < currInvAreaMulSquarePi):
                    if EllipticHullLib.areInside(coords, centre, A, B, C, epsilon):
                        maxInvAreaMulSquarePi = currInvAreaMulSquarePi
                        solution = result
        if solution is not None:
            [A, B, C], pivots, centre, methName = solution
            semiXAxis, semiYAxis, azim = EllipticHullLib.getSemiAxesAndAzim([A, B, C])
            return [pivots, centre, semiXAxis, semiYAxis, azim, methName]
        raise Exception('__getMinimumAreaBoundingEllipseAux(...): Unreachable instruction!')

    def __getAllMinimumAreaBoundingEllipse(self, coords, orderedIndices, epsilon=Epsilon.EPSILON):
        ncoords = len(coords)
        allIndices = list(range(ncoords))
        solutions = []

        if 3 <= ncoords:
            cnt = 0
            for indices in list(itertools.combinations(allIndices, 3)) + list(itertools.combinations(allIndices, 4)) + list(itertools.combinations(allIndices, 5)):
                cnt += 1
                result = self.__aux(coords, orderedIndices, indices)
                if result is None:
                    continue
                [A, B, C], pivots, centre, methName = result
                semiXAxis, semiYAxis, azim = EllipticHullLib.getSemiAxesAndAzim([A, B, C])   
                if EllipticHullLib.areInside(coords, centre, A, B, C, epsilon):
                    solutions.append([pivots, centre, semiXAxis, semiYAxis, azim, methName])
        return solutions
        
    def __getMinimumPerimeterBoundingEllipseAux(self, coords, orderedIndices, epsilon=Epsilon.EPSILON):
        ncoords = len(coords)
        allIndices = list(range(ncoords))

        minPerim, solution = float('inf'), None
        if 3 <= ncoords:
            cnt = 0
            for indices in list(itertools.combinations(allIndices, 3)) + list(itertools.combinations(allIndices, 4)) + list(itertools.combinations(allIndices, 5)):
                cnt += 1
                result = self.__aux(coords, orderedIndices, indices)
                if result is None:
                    continue
                [A, B, C], pivots, centre, methName = result

                semiXAxis, semiYAxis, azim = EllipticHullLib.getSemiAxesAndAzim([A, B, C])   

                currPerim = EllipseLib.getEllipsePerimeter(semiXAxis, semiYAxis)
                if (minPerim > currPerim):
                    if EllipticHullLib.areInside(coords, centre, A, B, C, epsilon):
                        minPerim = currPerim
                        solution = [pivots, centre, semiXAxis, semiYAxis, azim, methName]

        if solution is not None:
            return solution
        raise Exception('__getMinimumPerimeterBoundingEllipseAux(...): Unreachable instruction!')

    def __aux(self, coords, orderedIndices, indices):
        # The polygon must be topologically valid:
        indices = sorted([orderedIndices[i] for i in indices])
        coords = [coords[i] for i in indices]
        nindices = len(indices)

        # The initial centering is by no means universal. It is 
        # necessary to refocus locally using an isobarycentre.
        if (3 <= nindices):
            centroid = (
                sum([coords[k][0] for k in range(nindices)]) / float(nindices),
                sum([coords[k][1] for k in range(nindices)]) / float(nindices)
                )
            coords = EllipticHullLib.translateNodes(coords, [-centroid[0], -centroid[1]])

        centre, quadraticCoeffs = None, None
        if (3 == nindices):
            quadraticCoeffs = EllipticHullLib.tri(coords[0], coords[1], coords[2])
            centre, methName = centroid, 'tri'
        elif (4 == nindices):
            centre, quadraticCoeffs, methName = EllipticHullLib.quadri(coords[0], coords[1], coords[2], coords[3])
        elif (5 == nindices):
            centre, quadraticCoeffs = EllipticHullLib.penta(coords[0], coords[1], coords[2], coords[3], coords[4])
            methName = 'penta'

        if centre is None:
            return None
        if quadraticCoeffs is None:
            quadraticCoeffs = EllipticHullLib.getQuadraticCoeffs(coords, (0, 0))
            if quadraticCoeffs is None:
                return None

        if (3 <= nindices):
            if (3 < nindices):
                centre = EllipticHullLib.translateNodes([centre], centroid)[0]
            coords = EllipticHullLib.translateNodes(coords, centroid)

        return [quadraticCoeffs, coords, centre, methName]

    @staticmethod
    def penta(p1, p2, p3, p4, p5):
        # The initial translation ensures that the origin of the coordinates system is an inner point of the ellipse
        # After such a translation it is legal to write the following linear system
        matrixA, vectorB = zeros((5, 5)), ones(5)
        for nline, (x, y) in enumerate([p1, p2, p3, p4, p5]):
            # A x2 + B xy + C y2 + D x + E y = 1
            matrixA[nline] = [x * x, x * y, y * y, x, y]

        # matrixA * vectorX = vectorB (with: vectorX = [a2, b2, c2, d2, e2])
        a2, b2, c2, d2, e2 = solve(matrixA, vectorB)

        # Based on formulas provided by: https://en.wikipedia.org/wiki/Ellipse
        discriminant = b2 * b2 - 4 * a2 * c2
        # ellipse (discriminant < 0); parabola (discriminant = 0); hyperbola (discriminant > 0) 
        if (discriminant < 0):
            x0 = (2.0 * c2 * d2 - b2 * e2) / discriminant
            y0 = (2.0 * a2 * e2 - b2 * d2) / discriminant
            magn = 1.0 / (1.0 - (a2 * x0 * x0 + b2 * x0 * y0 + c2 * y0 * y0 + d2 * x0 + e2 * y0))
            a, b, c = a2 * magn, b2 * magn , c2 * magn  
            return (x0, y0), [a, b, c]
        return None, None

    def getMinimumAreaBoundingEllipseValue(self, qgsGeom):
        _, semiXAxis, semiYAxis, _, _, _ = self.getMinimumAreaBoundingEllipse(qgsGeom)
        return pi * semiXAxis * semiYAxis

    def plotMinimumAreaBoundingEllipse(self, qgsGeom, npoints=40):
        centre, semiXAxis, semiYAxis, azim, _, _ = self.getMinimumAreaBoundingEllipse(qgsGeom)
        return [ EllipseLib.getEllipseContour(centre, semiXAxis, semiYAxis, azim, npoints) ]

    def plotMinimumAreaBoundingEllipseAxis(self, qgsGeom):
        centre, semiXAxis, semiYAxis, azim, _, _ = self.getMinimumAreaBoundingEllipse(qgsGeom)
        return EllipseLib.getEllipseMainAxis(centre, semiXAxis, semiYAxis, azim)

    def plotAllMinimumAreaBoundingEllipses(self, geom, npoints=40):
        if not GeomLib.isAShapelyGeometry(geom):
            raise IllegalArgumentTypeException(geom, 'Shapely geometry')
        coords = geom.convex_hull.exterior.coords[:-1]  # Clockwise order
        # coords = list(reversed(geom.convex_hull.exterior.coords[:-1]))  # Counter-clockwise order

        bbox = BoundingBox(geom)
        magnitude = 1.0 / max(bbox.width(), bbox.height())
        invMagnitude = 1.0 / magnitude

        coords = EllipticHullLib.flatEdgesPruning(coords, self.threshold)
        orderedIndices, centroid = EllipticHullLib.orderNodesAndIdentifyTheCentroid(coords)
        coords = EllipticHullLib.homotheticTransformation(EllipticHullLib.translateNodes(coords, [-centroid[0], -centroid[1]]), magnitude)
        solutions = self.__getAllMinimumAreaBoundingEllipse(coords, orderedIndices)

        for solution in solutions:
            _, centre, semiXAxis, semiYAxis, azim, methName = solution

            x0, y0 = EllipticHullLib.translateNodes(EllipticHullLib.homotheticTransformation([centre], invMagnitude), centroid)[0]
            semiXAxis, semiYAxis = invMagnitude * semiXAxis, invMagnitude * semiYAxis 
            # nodes = EllipticHullLib.translateNodes(EllipticHullLib.homotheticTransformation(nodes, invMagnitude), centroid)
            '''
            ellipticHull = STEllipse(x0, y0, semiXAxis, semiYAxis, azim, npoints, outputLayername='ellipse_%s' % methName).run()
            setSimpleOutlineFillSymbol(ellipticHull, color='red', width='0.2', penstyle='solid')
            '''

    @staticmethod
    def __flatEdgesPruning(p, q, r, s, threshold):
        pq = GeomLib.unitVector(p, q)
        qr = GeomLib.unitVector(q, r)
        rs = GeomLib.unitVector(r, s)
        a_pqr = arccos(GeomLib.dotProduct(pq, qr))
        a_qrs = arccos(GeomLib.dotProduct(qr, rs))
        if (threshold > a_pqr + a_qrs):
            return EllipticHullLib.intersect_line_line(p, q, r, s)
        return None

    @staticmethod
    def flatEdgesPruning(nodes, threshold=None):
        # IL FAUT QUE : nodes[0] == nodes[-1]
        result = [x for x in nodes]
        if (threshold is not None) and (0 < threshold):
            i, n = 0, len(result)
            while (i + 3 < n):
                # print('i = %d, n = %d, result[i:i + 4] : %s' % (i, n, result[i:i + 4]))
                p, q, r, s = result[i:i + 4]
                ans = EllipticHullLib.__flatEdgesPruning(p, q, r, s, threshold)
                if ans is None:
                    i += 1
                else:
                    del(result[i + 2])
                    result[i + 1] = ans
                    n = len(result)
        return result

    @staticmethod
    def applyLinearMapToNodes(linearMap, coords):
        return [dot(linearMap, coord) for coord in coords]

    @staticmethod
    def areInside(coords, centre, A, B, C, epsilon=Epsilon.EPSILON):
        # A x2 + B xy + C y2 <= 1
        one = 1.0 + epsilon
        coords = EllipticHullLib.translateNodes(coords, -array(centre))
        for x, y in coords:
            if (one < (A * x * x + B * x * y + C * y * y)):
                return False
        return True

    @staticmethod
    def getQuadraticCoeffs(coords, centre):
        # A x2 + B xy + C y2 = 1
        tcoords = EllipticHullLib.translateNodes(coords, -array(centre))

        minCondNumber, bestMatrix = float('inf'), None
        for a, b, c in itertools.combinations(tcoords, 3):
            matrix = [
                [a[0] * a[0], a[0] * a[1], a[1] * a[1]],
                [b[0] * b[0], b[0] * b[1], b[1] * b[1]],
                [c[0] * c[0], c[0] * c[1], c[1] * c[1]]
            ]
            currCondNumber = cond(matrix)
            if (minCondNumber > currCondNumber):
                minCondNumber = currCondNumber
                bestMatrix = matrix

        try:
            A, B, C = solve(bestMatrix, [1.0, 1.0, 1.0])
            return list(map(float, [A, B, C]))
        except LinAlgError as error:
            print('EllipticHullLib.getQuadraticCoeffs(...): %s' % error)
        return None

    @staticmethod
    def getSemiAxesAndAzim(quadraticCoeffs, epsilon=Epsilon.EPSILON):
        # A x2 + B xy + C y2 = 1
        A, B, C = quadraticCoeffs

        if Epsilon.equals(A, C, epsilon):
            if Epsilon.isZero(B):
                semiAxis = 1.0 / sqrt(A)
                return [semiAxis, semiAxis, float('nan')]
            azim = pi / 4.0
        else:
            azim = 0.5 * arctan2(B, A - C)

        cosAzim, sinAzim = cos(azim), sin(azim)
        sqCosAzim, sqSinAzim = cosAzim * cosAzim, sinAzim * sinAzim
        sinCos = cosAzim * sinAzim
        semiXAxis = 1.0 / sqrt(A * sqCosAzim + B * sinCos + C * sqSinAzim)
        semiYAxis = 1.0 / sqrt(C * sqCosAzim - B * sinCos + A * sqSinAzim)

        if (semiXAxis < semiYAxis):
            azim = (azim + pi / 2.0) if (azim < 0) else (azim - pi / 2.0)

        return [semiXAxis, semiYAxis, azim]

    @staticmethod
    def homotheticTransformation(coords, magnitude):
        if 1.0 == magnitude:
            return coords
        return [[magnitude * coord[0], magnitude * coord[1]] for coord in coords]

    @staticmethod
    def intersect_line_line(a, b, c, d):
        line1 = [a, GeomLib.vector_to(a, b)]
        line2 = [c, GeomLib.vector_to(c, d)]
        return GeomLib.intersect_line_line(line1, line2)

    @staticmethod
    def isParallelogram(a, b, c, d, epsilon=Epsilon.EPSILON):
        centre = (0.25 * (a[0] + b[0] + c[0] + d[0]), 0.25 * (a[1] + b[1] + c[1] + d[1]))
        a, b, c, d = EllipticHullLib.translateNodes([a, b, c, d], -array(centre))
        M21 = [[a[0], c[0]], [a[1], c[1]]]
        M22 = [[b[0], d[0]], [b[1], d[1]]]
        return (max(abs(det(M21)), abs(det(M22))) <= epsilon)

    @staticmethod
    def orderNodesAndIdentifyTheCentroid(coords):
        s, n, indices = coords, len(coords), list(range(len(coords)))

        edges = []
        for k in indices:
            dx = s[k][0] - s[k - 1][0]
            dy = s[k][1] - s[k - 1][1]
            magn = 1.0 / sqrt(dx * dx + dy * dy)
            edges.append((magn * dx, magn * dy))

        weights = [arccos(
            edges[k][0] * edges[(k + 1) % n][0] + 
            edges[k][1] * edges[(k + 1) % n][1]
            ) for k in indices]
        '''
        for w in weights:
            if w < 0:
                raise Exception('Each weight must be positive!')
        if not (Epsilon.equals(sum(weights), 2 * pi)):
            raise Exception('The sum of weights must be equal to 2pi!')
        ''' 
        invSumOfWeights = 1.0 / sum(weights)

        centroid = (
            sum([weights[k] * coords[k][0] for k in indices]) * invSumOfWeights,
            sum([weights[k] * coords[k][1] for k in indices]) * invSumOfWeights
            )

        orderedIndices = sorted(indices, key=lambda k: weights[k],
                                reverse=False)
        return [orderedIndices, centroid]

    @staticmethod
    def __parall(a, b, c, d):
        [m11, m12], [m21, m22] = inv([[a[0], b[0]], [a[1], b[1]]])
        centre = (0.0, 0.0)
        A = m11 * m11 + m21 * m21
        B = 2.0 * (m11 * m12 + m21 * m22)
        C = m12 * m12 + m22 * m22
        return [centre, [A, B, C]]
    
    @staticmethod
    def __other_quadri(a, b, c, d, epsilon):
        # m0 = [ (a[0] + b[0] + c[0] + d[0]) / 4.0, (a[1] + b[1] + c[1] + d[1]) / 4.0]
        P = [[a[0], b[0], c[0], d[0]], [a[1], b[1], c[1], d[1]]]

        M21 = [[a[0], c[0]], [a[1], c[1]]]
        M22 = [[b[0], d[0]], [b[1], d[1]]]

        # STEP 1
        if Epsilon.isZero(det(M21), epsilon):
            u1, v1 = float('inf'), float('inf')
        else:
            M21 = inv(M21)
            P1 = matmul(M21, P)
            if 0 < P1[0][1]:
                u1, v1 = P1[0][1], P1[1][1]
            else:
                u1, v1 = P1[0][3], P1[1][3]

        if Epsilon.isZero(det(M22), epsilon):
            u2, v2 = float('inf'), float('inf')
        else:
            M22 = inv(M22)
            P2 = matmul(M22, P)
            if 0 < P2[0][0]:
                u2, v2 = P2[0][0], P2[1][0]
            else:
                u2, v2 = P2[0][2], P2[1][2]
        
        # STEP 2
        if abs(u1 + v1 - 2) < abs(u2 + v2 - 2):
            u, v, M2, P = u1, v1, M21, P1
        else:
            u, v, M2, P = u2, v2, M22, P2

        # STEP 3
        if abs(log(u * (u + 1) * (1 + 3 * v - u))) > abs(log(v * (v + 1) * (1 + 3 * u - v))):
            u, v = v, u
            P = matmul([[0.0, 1.0], [1.0, 0.0]], P)
            M2 = matmul([[0.0, 1.0], [1.0, 0.0]], M2)

        du = u * (u + 1.0) * (1.0 + 3.0 * v - u)
        dv = v * (v + 1.0) * (1.0 + 3.0 * u - v)
        d2 = 2.0 / du
        a = [dv / du, ((v - 1.0) * ((1.0 + v) ** 2.0 - u * v) + (1.0 + 2.0 * v) * u ** 2.0) / du]
        b = [d2 * (v - u) * (2.0 * u * v + u + v - 1.0), d2 * ((1.0 - u) * ((1.0 + u) ** 2.0 - u * v) - (1.0 + 2.0 * u) * v ** 2.0)]
        c = [-1.0, 1.0]
        d = [-a[0], 1.0 - a[1]]

        den = polyadd(4.0 * polymul(a, c), -polymul(b, b))
        den2 = [0.0] + list(polymul(den, den))

        polt = [1.0, 0.0]
        m1 = polyadd(polymul(b, polt), -2.0 * polymul(c, d))
        m2 = polyadd(polymul(b, d), -2.0 * polymul(a, polt))

        num = polyadd(polymul(d, polymul(den, m1)), polymul(polt, polymul(den, m2)))
        num = polyadd(polymul(c, polymul(m2, m2)), num)
        num = polyadd(polymul(b, polymul(m1, m2)), num)
        num = polyadd(polymul(a, polymul(m1, m1)), num)
        num = polyadd(den2, -num)

        t6 = polyadd(2.0 * polymul(polyder(num), den), -5.0 * polymul(polyder(den), num))

        # DEBUG : FORCE THE MOST SIGNIFICANT FACTOR TO BE EQUAL TO 0 (EXACT EQUALITY)
        if 7 == len(t6):
            t6[0] = 0.0
        # t6 = roots(t6)
        t6 = polyroots(flip(t6, axis=0))

        v0, tt = float('inf'), None
        for t in t6:
            if Epsilon.isZero(abs(imag(t)), epsilon):
                t = real(t)
                if 1e-12 < polyval(den, t):
                    x, y = polyval(num, t), polyval(den, t)  
                    v = (x * x) / (y ** 5)
                    if v0 > v:
                        v0, tt = v, t

        if tt is None:
            # print('.')
            return [None, []]

        mm = array([[polyval(m1, tt)], [polyval(m2, tt)]]) / polyval(den, tt)

        for l in range(2):
            for k in range(4):
                P[l][k] = P[l][k] - mm[l][0]

        m = matmul(inv(M2), mm);

        dd = polyval(num, tt) / polyval(den2, tt)
        aa = polyval(a, tt) / dd
        bb = polyval(b, tt) / dd
        cc = polyval(c, tt) / dd;

        [m11, m12], [m21, m22] = M2

        aa1 = aa * m11 * m11 + bb * m11 * m21 + cc * m21 * m21
        bb1 = 2.0 * (aa * m11 * m12 + cc * m21 * m22) + bb * (m11 * m22 + m21 * m12)
        cc1 = aa * m12 * m12 + bb * m12 * m22 + cc * m22 * m22
        aa, bb, cc = float(aa1), float(bb1), float(cc1)

        centre = (real(m[0])[0], real(m[1])[0])
        return [centre, [aa, bb, cc]]

    @staticmethod
    def quadri(a, b, c, d, epsilon=Epsilon.EPSILON):
        if EllipticHullLib.isParallelogram(a, b, c, d, epsilon):
            return EllipticHullLib.__parall(a, b, c, d) + ['parall']
        return EllipticHullLib.__other_quadri(a, b, c, d, epsilon) + ['quadri']

    @staticmethod
    def rotateNodes(azim, coords):
        cosAzim, sinAzim = cos(azim), sin(azim)
        return [[coord[0] * cosAzim - coord[1] * sinAzim,
                    coord[0] * sinAzim + coord[1] * cosAzim] for coord in coords]

    @staticmethod
    def translateNodes(coords, t):
        if (0.0 == t[0]) and (0.0 == t[1]):
            return coords
        return [[coord[0] + t[0], coord[1] + t[1]] for coord in coords]

    @staticmethod
    def tri(a, b, c):
        '''
        Triangle a, b, c is transformed, via a linear map, into the equilateral triangle: 
        (1 0), (-1/2 V3/2), (-1/2 -V3/2)
        '''
        [m11, m12], [m21, m22] = matmul([[1.0, -0.5], [0.0, 0.5 * sqrt(3)]], inv([[a[0], b[0]], [a[1], b[1]]]))
        A = m11 * m11 + m21 * m21
        B = 2.0 * (m11 * m12 + m21 * m22)
        C = m12 * m12 + m22 * m22
        return A, B, C

    @staticmethod
    def __layerOfNodes(coords, label, symbolType, symbolColor, symbolSize):
        return GeoDataFrame({'geometry': MultiPoint(coords)}, crs='EPSG:2154')
