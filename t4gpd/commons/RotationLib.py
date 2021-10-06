'''
Created on 27 aug. 2020

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
from shapely.coords import CoordinateSequence
from shapely.geometry import GeometryCollection, MultiPoint, MultiLineString, MultiPolygon, LinearRing, LineString, Point, Polygon
from shapely.geometry.base import GeometrySequence

from numpy import cos, sin
from t4gpd.commons.GeomLib import GeomLib


class RotationLib(object):
    '''
    classdocs
    '''

    '''
    @staticmethod
    def rotation(axis, p, angle):
        axisNorm = sqrt(axis[0] * axis[0] + axis[1] * axis[1] + axis[2] * axis[2])
        u = (axis[0] / axisNorm, axis[1] / axisNorm, axis[2] / axisNorm)
        c, s = cos(angle), sin(angle)
        m = (
            (u[0] * u[0] * (1 - c) + c, u[0] * u[1] * (1 - c) - u[2] * s, u[0] * u[2] * (1 - c) + u[1] * s),
            (u[0] * u[1] * (1 - c) + u[2] * s, u[1] * u[1] * (1 - c) + c, u[1] * u[2] * (1 - c) - u[0] * s),
            (u[0] * u[2] * (1 - c) - u[1] * s, u[1] * u[2] * (1 - c) + u[0] * s, u[2] * u[2] * (1 - c) + c)
            )
        if isinstance(p, Point):
            p = [p.x, p.y, p.z]
        return (
            m[0][0] * p[0] + m[0][1] * p[1] + m[0][2] * p[2],
            m[1][0] * p[0] + m[1][1] * p[1] + m[1][2] * p[2],
            m[2][0] * p[0] + m[2][1] * p[1] + m[2][2] * p[2]
            )

    @staticmethod
    def xAxisRotation(p, angle):
        return RotationLib.rotation((1, 0, 0), p, angle)

    @staticmethod
    def yAxisRotation(p, angle):
        return RotationLib.rotation((0, 1, 0), p, angle)

    @staticmethod
    def zAxisRotation(p, angle):
        return RotationLib.rotation((0, 0, 1), p, angle)
    '''

    @staticmethod
    def rotate2DXYZ(point, angleInRad):
        c, s = cos(angleInRad), sin(angleInRad)

        if isinstance(point, Point):
            if point.has_z:
                p = [point.x, point.y, point.z]
            else:
                p = [point.x, point.y]
        else:
            p = point

        x, y = p[0] * c - p[1] * s, p[0] * s + p[1] * c
        if (2 == len(p)):
            return [x, y]
        elif (3 == len(p)):
            return [x, y, p[2]]
        return None

    @staticmethod
    def rotate2D(geom, angleInRad):
        if isinstance(geom, CoordinateSequence):
            return [RotationLib.rotate2DXYZ(p, angleInRad) for p in geom]

        elif isinstance(geom, GeometrySequence):
            return [RotationLib.rotate2D(g, angleInRad) for g in geom]

        elif GeomLib.isAShapelyGeometry(geom):
            if isinstance(geom, Point):
                return Point(RotationLib.rotate2DXYZ(geom, angleInRad))
            elif isinstance(geom, LinearRing):
                return LinearRing(RotationLib.rotate2D(geom.coords, angleInRad))
            elif isinstance(geom, LineString):
                return LineString(RotationLib.rotate2D(geom.coords, angleInRad))
            elif isinstance(geom, Polygon):
                extRing = RotationLib.rotate2D(geom.exterior.coords, angleInRad)
                intRings = [
                    RotationLib.rotate2D(r.coords, angleInRad) for r in geom.interiors
                    ]
                return Polygon(extRing, intRings)

            elif GeomLib.isMultipart(geom):
                if isinstance(geom, MultiPoint):
                    return MultiPoint(RotationLib.rotate2D(geom.geoms, angleInRad))
                elif isinstance(geom, MultiLineString):
                    return MultiLineString(RotationLib.rotate2D(geom.geoms, angleInRad))
                elif isinstance(geom, MultiPolygon):
                    return MultiPolygon(RotationLib.rotate2D(geom.geoms, angleInRad))
                elif isinstance(geom, GeometryCollection):
                    return GeometryCollection(RotationLib.rotate2D(geom.geoms, angleInRad))

        return None
