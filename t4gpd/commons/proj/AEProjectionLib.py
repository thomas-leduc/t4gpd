'''
Created on 25 sep. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from numpy import cos, ndarray, pi, sin, sqrt
from shapely import Point
from shapely.coords import CoordinateSequence
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class AEProjectionLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def __to_point(vp):
        if isinstance(vp, (CoordinateSequence, list, ndarray, tuple)):
            vp = Point(vp)
        if not isinstance(vp, Point):
            raise IllegalArgumentTypeException(
                vp, "CoordinateSequence, list, ndarray, Point, or tuple")
        return vp

    @staticmethod
    def isoaire_projection(vp, azim, elev, size=1):
        # azim == lon, elev == lat
        vp = AEProjectionLib.__to_point(vp)
        radius = sqrt((1 - sin(elev)) / ((cos(elev)*cos(azim))
                      ** 2 + (cos(elev)*sin(azim))**2))
        radius *= (size * cos(elev))
        return (vp.x + radius * cos(azim), vp.y + radius * sin(azim))

    @staticmethod
    def orthogonal_projection(vp, azim, elev, size=1):
        # azim == lon, elev == lat
        vp = AEProjectionLib.__to_point(vp)
        radius = (size * cos(elev))
        return (vp.x + radius * cos(azim), vp.y + radius * sin(azim))

    @staticmethod
    def polar_projection(vp, azim, elev, size=1):
        # azim == lon, elev == lat
        vp = AEProjectionLib.__to_point(vp)
        radius = (size * (pi - 2 * elev)) / pi
        return (vp.x + radius * cos(azim), vp.y + radius * sin(azim))

    @staticmethod
    def stereographic_projection(vp, azim, elev, size=1):
        # azim == lon, elev == lat
        vp = AEProjectionLib.__to_point(vp)
        radius = (size * cos(elev)) / (1.0 + sin(elev))
        return (vp.x + radius * cos(azim), vp.y + radius * sin(azim))

    @staticmethod
    def reverse_isoaire_projection(vp, azim, elev, size=1):
        raise NotImplementedError("Must be implemented!")

    @staticmethod
    def reverse_orthogonal_projection(vp, pp, size=1):
        raise NotImplementedError("Must be implemented!")

    @staticmethod
    def reverse_polar_projection(vp, pp, size=1):
        raise NotImplementedError("Must be implemented!")

    @staticmethod
    def reverse_stereographic_projection(vp, pp, size=1):
        raise NotImplementedError("Must be implemented!")

    @ staticmethod
    def projection_switch(projectionName):
        projectionName = projectionName.lower()
        if ("stereographic" == projectionName):
            return AEProjectionLib.stereographic_projection
        elif ("orthogonal" == projectionName):
            return AEProjectionLib.orthogonal_projection
        elif ("polar" == projectionName):
            return AEProjectionLib.polar_projection
        elif ("isoaire" == projectionName):
            return AEProjectionLib.isoaire_projection
        raise IllegalArgumentTypeException(
            projectionName, "spherical projection as 'Stereographic', 'Orthogonal', 'Polar', or 'Isoaire'")

    @ staticmethod
    def reverse_projection_switch(projectionName):
        projectionName = projectionName.lower()
        if ("stereographic" == projectionName):
            return AEProjectionLib.reverse_stereographic_projection
        elif ("orthogonal" == projectionName):
            return AEProjectionLib.reverse_orthogonal_projection
        elif ("polar" == projectionName):
            return AEProjectionLib.reverse_polar_projection
        elif ("isoaire" == projectionName):
            return AEProjectionLib.reverse_isoaire_projection
        raise IllegalArgumentTypeException(
            projectionName, "spherical projection as 'Stereographic', 'Orthogonal', 'Polar', or 'Isoaire'")
