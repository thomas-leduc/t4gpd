'''
Created on 10 mars 2021

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
from numpy import sqrt
from shapely.geometry import LinearRing, Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class GeomLib3D(object):
    '''
    classdocs
    '''

    @staticmethod
    def crossProduct(u, v):
        return [
            (u[1] * v[2]) - (u[2] * v[1]),
            (u[2] * v[0]) - (u[0] * v[2]),
            (u[0] * v[1]) - (u[1] * v[0])
            ]

    @staticmethod
    def dotProduct(u, v):
        return ((u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2]))

    @staticmethod
    def __getArea(ring):
        # ring is a 3D contour
        coords = ring.coords
        _first = coords[0]

        _sum = [0, 0, 0]
        for i in range(1, len(coords) - 1):
            _curr, _next = coords[i], coords[i + 1]
            _product = GeomLib3D.crossProduct(
                GeomLib3D.vector_to(_first, _curr),
                GeomLib3D.vector_to(_first, _next))
            for j in range(3):
                _sum[j] += _product[j]

        _normal = GeomLib3D.getFaceNormalVector(ring)

        return 0.5 * GeomLib3D.dotProduct(_sum, _normal)

    @staticmethod
    def getArea(geom):
        if not GeomLib.isPolygonal(geom):
            raise IllegalArgumentTypeException(geom, 'Polygon or MultiPolygon')

        if (not GeomLib.is3D(geom)):
            return geom.area

        polygons = [geom] if isinstance(geom, Polygon) else geom.geoms

        result = 0
        for polygon in polygons:
            result += GeomLib3D.__getArea(polygon.exterior)
            for hole in polygon.interiors:
                result += GeomLib3D.__getArea(hole)
        return result

    @staticmethod
    def getFaceNormalVector(geom):
        if (not isinstance(geom, (LinearRing, Polygon))):
            raise IllegalArgumentTypeException(geom, 'LinearRing or Polygon')

        geom = geom.exterior if isinstance(geom, Polygon) else geom

        if (not GeomLib.is3D(geom)):
            _ccw = 1 if GeomLib.isCCW(geom) else -1
            return [0, 0, _ccw]

        coords = geom.coords

        # Maximize radius starting from first node
        _maxDiam, _maxDiamIdx = -float('inf'), None
        for i in range(1, len(coords) - 1):
            _currDiam = GeomLib3D.squaredDistance3D(coords[0], coords[i])
            if (_maxDiam < _currDiam):
                _maxDiam, _maxDiamIdx = _currDiam, i

        _firstRadius = GeomLib3D.vector_to(coords[0], coords[_maxDiamIdx])

        # Maximize surface area (absolute) value using first radius
        _maxNorm, _maxCrossProduct, _secondRadius = 0.0, None, None
        for i in range(1, len(coords) - 1):
            if (i != _maxDiamIdx):
                _currRadius = GeomLib3D.vector_to(coords[0], coords[i])
                _currCrossProduct = GeomLib3D.crossProduct(_firstRadius, _currRadius)
                _currNorm = GeomLib3D.squaredNorm3D(_currCrossProduct)
                if (abs(_maxNorm) < abs(_currNorm)):
                    _maxNorm, _maxCrossProduct, _secondRadius = _currNorm, _currCrossProduct, _currRadius

        return GeomLib3D.unitVector(_maxCrossProduct)

    @staticmethod
    def norm3D(u):
        return sqrt(GeomLib3D.squaredNorm3D(u))

    @staticmethod
    def squaredDistance3D(p, q):
        dx, dy, dz = GeomLib3D.vector_to(p, q)
        return ((dx * dx) + (dy * dy) + (dz * dz))

    @staticmethod
    def squaredNorm3D(u):
        return ((u[0] * u[0]) + (u[1] * u[1]) + (u[2] * u[2]))

    @staticmethod
    def unitVector(u):
        _norm = GeomLib3D.norm3D(u)
        if (0 < _norm):
            _invNorm = 1.0 / _norm
            return (_invNorm * u[0], _invNorm * u[1], _invNorm * u[2])
        raise IllegalArgumentTypeException(u, 'Must be non-null vector!')

    @staticmethod
    def vector_to(p, q):
        dx = q[0] - p[0]
        dy = q[1] - p[1]
        dz = q[2] - p[2]
        return (dx, dy, dz)
