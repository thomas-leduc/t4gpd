'''
Created on 19 juin 2020

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
from numpy import arctan2, degrees, pi, radians, r_


class AngleLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def angleBetween(direction1, direction2):
        angle = AngleLib.normAzimuth(
            direction2) - AngleLib.normAzimuth(direction1)
        return angle % (2 * pi)

    @staticmethod
    def angleBetweenNodes(node1, orig, node2):
        return AngleLib.angleBetween([node1[0] - orig[0], node1[1] - orig[1]], [node2[0] - orig[0], node2[1] - orig[1]])

    @staticmethod
    def eastCCW2northCW(angle, degree=True):
        return AngleLib.northCW2eastCCW(angle, degree)

    @staticmethod
    def fromEastCCWAzimuthToOppositeSliceIds(azim, nslices, offset=0, degree=True):
        quadrant = nslices // 4
        sliceId = AngleLib.fromEastCCWAzimuthToSliceId(azim, nslices, degree)
        start = (sliceId + quadrant + offset) % nslices
        stop = (sliceId + 3*quadrant - offset) % nslices
        if (start < stop):
            return slice(start, stop + 1)
        return r_[slice(start, nslices), slice(0, stop + 1)]

    @staticmethod
    def fromEastCCWAzimuthToSliceId(azim, nslices, degree=True):
        if not degree:
            azim = degrees(azim)
        azim = AngleLib.normalizeAngle(azim)
        offset = 360 / nslices
        return int((azim + offset/2) / offset) % nslices

    @staticmethod
    def normalizeAngle(angle, degree=True):
        modulo = 360 if degree else 2 * pi
        return angle % modulo

    @staticmethod
    def normAzimuth(direction):
        angle = arctan2(direction[1], direction[0])
        return angle % (2 * pi)

    @staticmethod
    def northCW2eastCCW(angle, degree=True):
        quarto = 90 if degree else pi / 2
        return AngleLib.normalizeAngle(5 * quarto - angle, degree)

    @staticmethod
    def southCCW2northCW(angle, degree=True):
        half = 180 if degree else pi
        return AngleLib.normalizeAngle(half - angle, degree)

    @staticmethod
    def toDegrees(angle):
        return degrees(angle)

    @staticmethod
    def toRadians(angle):
        return radians(angle)
