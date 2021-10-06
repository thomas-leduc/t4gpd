'''
Created on 21 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from numpy import cos, pi, sin
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.ellipse.EllipseLib import EllipseLib


class ShadowLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def __projectPointOntoShadowPlane(pA, radDir, altitudeOfShadowPlane):
        # M point one line (AB) iff: pM = (1-k).pA + k.pB
        pB = Point((pA.x + radDir[0], pA.y + radDir[1], pA.z + radDir[2]))
        if (pA.z == pB.z):
            if (altitudeOfShadowPlane == pA.z):
                return pA
            return None
        else:
            k = (altitudeOfShadowPlane - pA.z) / (pB.z - pA.z)
            xM = (1 - k) * pA.x + k * pB.x 
            yM = (1 - k) * pA.y + k * pB.y
            zM = altitudeOfShadowPlane
            return Point((xM, yM, zM))

    @staticmethod
    def __projectWallOntoShadowPlane(pA, pB, occluderElevation, radDir,
                                     altitudeOfShadowPlane):
        ppA = ShadowLib.__projectPointOntoShadowPlane(
            Point((pA.x, pA.y, occluderElevation)), radDir, altitudeOfShadowPlane)
        ppB = ShadowLib.__projectPointOntoShadowPlane(
            Point((pB.x, pB.y, occluderElevation)), radDir, altitudeOfShadowPlane)
        return Polygon([ (pA.x, pA.y), (pB.x, pB.y), (ppB.x, ppB.y), (ppA.x, ppA.y) ])

    @staticmethod
    def __projectRingOntoShadowPlane(ring, occluderElevation, exteriorRing,
                                     radDir, altitudeOfShadowPlane):
        if (0.0 < ring.length):
            n, shadows = len(list(ring.coords)), [Polygon(ring)] if exteriorRing else []
            for i in range(1, n):
                pA = Point(ring.coords[i - 1])
                pB = Point(ring.coords[i])
                shadows.append(ShadowLib.__projectWallOntoShadowPlane(
                    pA, pB, occluderElevation, radDir, altitudeOfShadowPlane))
            return unary_union(shadows)
        return None

    @staticmethod
    def projectBuildingOntoShadowPlane(polygon, occluderElevation, radDir, altitudeOfShadowPlane):
        _ring = polygon.exterior 
        shadow = ShadowLib.__projectRingOntoShadowPlane(
            _ring, occluderElevation, True, radDir, altitudeOfShadowPlane) 

        # Handle hole(s)
        for _ring in polygon.interiors:
            _shadow = ShadowLib.__projectRingOntoShadowPlane(
                _ring, occluderElevation, False, radDir, altitudeOfShadowPlane)
            if GeomLib.isHoled(_shadow):
                for _hole in _shadow.interiors:
                    shadow = shadow.difference(Polygon(_hole))

        return shadow

    @staticmethod
    def projectSphericalTreeOntoShadowPlane(treePosition, treeHeight, treeCrownRadius,
                                            treeTrunkRadius, radDir, solarAlti, solarAzim,
                                            altitudeOfShadowPlane, npoints):
        # Tree crown        
        # the projection of a sphere on a horizontal plane is an ellipse
        a = treeCrownRadius
        b = a / sin(solarAlti)
        c = Point((treePosition.x, treePosition.y, treeHeight - a))
        pc = Point(ShadowLib.__projectPointOntoShadowPlane(c, radDir, altitudeOfShadowPlane))
        treeCrownShadow = EllipseLib.getEllipseContour(pc, a, b, solarAzim, npoints)

        # Tree trunk
        if treeTrunkRadius is None:
            # Extrait de 
            # https://patternformation.wordpress.com/2013/01/08/la-hauteur-des-arbres-2/
            # h = 90.1 * a**(2/3)
            # a = (h / 90.1)**(3/2)
            a = max(0.1, (treeHeight / 90.1) ** (3 / 2))
        else:
            a = treeTrunkRadius
        c = Point((treePosition.x, treePosition.y, treeHeight - 2 * a))
        p1 = Point(c.x + a * cos(solarAzim + pi / 2), c.y + a * sin(solarAzim + pi / 2), c.z)
        p2 = Point(c.x + a * cos(solarAzim - pi / 2), c.y + a * sin(solarAzim - pi / 2), c.z)
        pp1 = ShadowLib.__projectPointOntoShadowPlane(p1, radDir, altitudeOfShadowPlane)
        pp2 = ShadowLib.__projectPointOntoShadowPlane(p2, radDir, altitudeOfShadowPlane)
        treeTrunkShadow = Polygon([(p1.x, p1.y, 0), (p2.x, p2.y, 0), pp2, pp1])

        return treeCrownShadow.union(treeTrunkShadow)

    @staticmethod
    def projectConicalTreeOntoShadowPlane(treePosition, treeHeight, treeCrownHeight,
                                          treeUpperCrownRadius, treeLowerCrownRadius,
                                          treeTrunkRadius, radDir, solarAlti, solarAzim,
                                          altitudeOfShadowPlane, npoints):
        # Tree crown
        cUp = Point((treePosition.x, treePosition.y, treeHeight))
        cDown = Point((treePosition.x, treePosition.y, treeHeight - treeCrownHeight))
        a, b = treeUpperCrownRadius, treeLowerCrownRadius

        incAngle, deltaAngle = 0, 2 * pi / npoints
        pPrevUp, pPrevDown = None, None

        treeCrownShadows, pUpperNodes = [], []
        for i in range(npoints + 1):
            _cos, _sin = cos(incAngle), sin(incAngle)
            currUp = Point((cUp.x + a * _cos, cUp.y + a * _sin, cUp.z))
            currDown = Point((cDown.x + b * _cos, cDown.y + b * _sin, cDown.z))

            pCurrUp = Point(ShadowLib.__projectPointOntoShadowPlane(
                currUp, radDir, altitudeOfShadowPlane))
            pCurrDown = Point(ShadowLib.__projectPointOntoShadowPlane(
                currDown, radDir, altitudeOfShadowPlane))

            pUpperNodes.append(pCurrUp)

            if 0 < i:
                treeCrownShadows.append(Polygon((pPrevUp, pCurrUp, pCurrDown, pPrevDown))) 

            pPrevUp, pPrevDown = pCurrUp, pCurrDown
            incAngle += deltaAngle
        treeCrownShadows.append(Polygon(pUpperNodes))
        treeCrownShadow = unary_union(treeCrownShadows)

        # Tree trunk
        if treeTrunkRadius is None:
            # Extrait de 
            # https://patternformation.wordpress.com/2013/01/08/la-hauteur-des-arbres-2/
            # h = 90.1 * a**(2/3)
            # a = (h / 90.1)**(3/2)
            a = max(0.1, (treeHeight / 90.1) ** (3 / 2))
        else:
            a = treeTrunkRadius
        c = Point((treePosition.x, treePosition.y, treeHeight - treeCrownHeight))
        p1 = Point(c.x + a * cos(solarAzim + pi / 2), c.y + a * sin(solarAzim + pi / 2), c.z)
        p2 = Point(c.x + a * cos(solarAzim - pi / 2), c.y + a * sin(solarAzim - pi / 2), c.z)
        pp1 = ShadowLib.__projectPointOntoShadowPlane(p1, radDir, altitudeOfShadowPlane)
        pp2 = ShadowLib.__projectPointOntoShadowPlane(p2, radDir, altitudeOfShadowPlane)
        treeTrunkShadow = Polygon([(p1.x, p1.y, 0), (p2.x, p2.y, 0), pp2, pp1])

        _result = treeCrownShadow.union(treeTrunkShadow)
        # Use a buffer to avoid slivers
        _result = _result.buffer(0.001, -1)

        return _result
