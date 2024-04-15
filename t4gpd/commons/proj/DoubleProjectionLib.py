'''
Created on 22 mar. 2024

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
from numpy import asarray, sqrt
from shapely import Point
from shapely.coords import CoordinateSequence
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class DoubleProjectionLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def __first_projection(vp, rp):
        if (isinstance(vp, Point) and isinstance(rp, Point)):
            vp, rp = vp.coords, rp.coords
        if (isinstance(vp, CoordinateSequence) and isinstance(rp, CoordinateSequence)):
            vp, rp = vp[0], rp[0]

        vp, rp = asarray(vp), asarray(rp)
        vp2rp = rp - vp
        D = sqrt((vp2rp**2).sum())
        invD = 1 / D
        pp = invD * vp2rp

        return vp, pp, D

    @staticmethod
    def isoaire_projection(vp, rp, size=1):
        viewpoint, pp, D = DoubleProjectionLib.__first_projection(
            vp, rp)

        tmp = pp[0]**2 + pp[1]**2
        if (0 == tmp):
            # Projection of a point above the viewpoint
            return Point([
                viewpoint[0],
                viewpoint[1],
                D  # viewpoint[2]
            ])

        magn = size * sqrt((1-pp[2]) / tmp)
        return Point([
            viewpoint[0] + magn * pp[0],
            viewpoint[1] + magn * pp[1],
            D  # viewpoint[2]
        ])

    @staticmethod
    def orthogonal_projection(vp, rp, size=1):
        viewpoint, pp, D = DoubleProjectionLib.__first_projection(
            vp, rp)
        return Point([
            viewpoint[0] + size * pp[0],
            viewpoint[1] + size * pp[1],
            D  # viewpoint[2]
        ])

    @staticmethod
    def stereographic_projection(vp, rp, size=1):
        viewpoint, pp, D = DoubleProjectionLib.__first_projection(
            vp, rp)
        magn = size / (1.0 + pp[2])
        return Point([
            viewpoint[0] + magn * pp[0],
            viewpoint[1] + magn * pp[1],
            D  # viewpoint[2]
        ])

    @staticmethod
    def projectionSwitch(projectionName):
        projectionName = projectionName.lower()
        if ("stereographic" == projectionName):
            return DoubleProjectionLib.stereographic_projection
        elif ("orthogonal" == projectionName):
            return DoubleProjectionLib.orthogonal_projection
        elif ("isoaire" == projectionName):
            return DoubleProjectionLib.isoaire_projection
        raise IllegalArgumentTypeException(
            projectionName, "spherical projection as 'Stereographic', 'Orthogonal' or 'Isoaire'")
