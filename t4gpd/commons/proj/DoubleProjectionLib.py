"""
Created on 22 mar. 2024

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

from numpy import asarray, cos, pi, sin, sqrt
from shapely import Point
from shapely.coords import CoordinateSequence
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.SphericalCartesianCoordinates import SphericalCartesianCoordinates


class DoubleProjectionLib(object):
    """
    classdocs
    """

    @staticmethod
    def __to_pair_of_arrays(vp, rp):
        if isinstance(vp, Point) and isinstance(rp, Point):
            vp, rp = vp.coords, rp.coords
        if isinstance(vp, CoordinateSequence) and isinstance(rp, CoordinateSequence):
            vp, rp = vp[0], rp[0]
        vp, rp = asarray(vp), asarray(rp)
        return vp, rp

    @staticmethod
    def __first_projection(vp, rp):
        vp, rp = DoubleProjectionLib.__to_pair_of_arrays(vp, rp)

        vp2rp = rp - vp
        D = sqrt((vp2rp**2).sum())
        invD = 1 / D
        pp = invD * vp2rp

        return vp, pp, D

    @staticmethod
    def isoaire_projection(vp, rp, size=1):
        viewpoint, pp, D = DoubleProjectionLib.__first_projection(vp, rp)

        tmp = pp[0] ** 2 + pp[1] ** 2
        if 0 == tmp:
            # Projection of a point above the viewpoint
            return Point([viewpoint[0], viewpoint[1], D])  # viewpoint[2]

        magn = size * sqrt((1 - pp[2]) / tmp)
        return Point(
            [
                viewpoint[0] + magn * pp[0],
                viewpoint[1] + magn * pp[1],
                D,  # viewpoint[2]
            ]
        )

    @staticmethod
    def orthogonal_projection(vp, rp, size=1):
        viewpoint, pp, D = DoubleProjectionLib.__first_projection(vp, rp)
        return Point(
            [
                viewpoint[0] + size * pp[0],
                viewpoint[1] + size * pp[1],
                D,  # viewpoint[2]
            ]
        )

    @staticmethod
    def polar_projection(vp, rp, size=1):
        viewpoint, pp, D = DoubleProjectionLib.__first_projection(vp, rp)
        _, lon, lat = SphericalCartesianCoordinates.fromCartesianToSphericalCoordinates(
            *pp
        )
        magn = (size * (pi - 2 * lat)) / pi
        return Point(
            [
                viewpoint[0] + magn * cos(lon),
                viewpoint[1] + magn * sin(lon),
                D,  # viewpoint[2]
            ]
        )

    @staticmethod
    def stereographic_projection(vp, rp, size=1):
        viewpoint, pp, D = DoubleProjectionLib.__first_projection(vp, rp)
        magn = size / (1.0 + pp[2])
        return Point(
            [
                viewpoint[0] + magn * pp[0],
                viewpoint[1] + magn * pp[1],
                D,  # viewpoint[2]
            ]
        )

    @staticmethod
    def reverse_isoaire_projection(vp, pp, size=1):
        vp, pp = DoubleProjectionLib.__to_pair_of_arrays(vp, pp)
        pp = (pp - vp) / size
        tmp1 = 1 - pp[0] ** 2 - pp[1] ** 2
        tmp2 = sqrt(1 + tmp1)
        return Point([vp[0] + pp[0] * tmp2, vp[1] + pp[1] * tmp2, vp[2] + tmp1])

    @staticmethod
    def reverse_orthogonal_projection(vp, pp, size=1):
        vp, pp = DoubleProjectionLib.__to_pair_of_arrays(vp, pp)
        pp = (pp - vp) / size
        return Point(
            [vp[0] + pp[0], vp[1] + pp[1], vp[2] + sqrt(1.0 - pp[0] ** 2 - pp[1] ** 2)]
        )

    @staticmethod
    def reverse_polar_projection(vp, pp, size=1):
        raise NotImplementedError("Must be implemented!")

    @staticmethod
    def reverse_stereographic_projection(vp, pp, size=1):
        vp, pp = DoubleProjectionLib.__to_pair_of_arrays(vp, pp)
        pp = (pp - vp) / size
        magn = 2 / (1.0 + pp[0] ** 2 + pp[1] ** 2)
        return Point([vp[0] + magn * pp[0], vp[1] + magn * pp[1], vp[2] + magn - 1])

    @staticmethod
    def projection_switch(projectionName):
        match projectionName.lower():
            case "stereographic":
                return DoubleProjectionLib.stereographic_projection
            case "orthogonal":
                return DoubleProjectionLib.orthogonal_projection
            case "polar":
                return DoubleProjectionLib.polar_projection
            case "isoaire" | "equiareal":
                return DoubleProjectionLib.isoaire_projection
            case _:
                raise IllegalArgumentTypeException(
                    projectionName,
                    "spherical projection as 'Stereographic', 'Orthogonal', 'Polar', or 'Isoaire'",
                )

    @staticmethod
    def reverse_projection_switch(projectionName):
        match projectionName.lower():
            case "stereographic":
                return DoubleProjectionLib.reverse_stereographic_projection
            case "orthogonal":
                return DoubleProjectionLib.reverse_orthogonal_projection
            case "polar":
                return DoubleProjectionLib.reverse_polar_projection
            case "isoaire" | "equiareal":
                return DoubleProjectionLib.reverse_isoaire_projection
            case _:
                raise IllegalArgumentTypeException(
                    projectionName,
                    "spherical projection as 'Stereographic', 'Orthogonal', 'Polar', or 'Isoaire'",
                )
