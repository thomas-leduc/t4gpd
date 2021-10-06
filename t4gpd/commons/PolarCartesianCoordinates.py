'''
Created on 22 juin 2020

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
from numpy import arctan2, cos, isnan, mean, pi, sin, sqrt

from t4gpd.commons.ListUtilities import ListUtilities


class PolarCartesianCoordinates(object):
    '''
    classdocs
    '''

    @staticmethod
    def fromCartesianToPolarCoordinates(x, y):
        r = sqrt((x * x) + (y * y))
        if (0 == x):
            if (0 < y):
                azimuth = pi / 2
            elif (0 > y):
                azimuth = (3 * pi) / 2
            else:
                azimuth = float('nan')
        else:
            azimuth = arctan2(y, x)
            if (0 > azimuth):
                azimuth += 2 * pi
        return [float(r), float(azimuth)]

    @staticmethod
    def fromPolarToCartesianCoordinates(r, azimuth):
        return [r * cos(azimuth), r * sin(azimuth)]

    @staticmethod
    def fromRayLengthsToPolarCoordinates(rayLengths):
        if isinstance(rayLengths, list) and (0 < len(rayLengths)):
            angularOffset = (2 * pi) / len(rayLengths)
            return [[r, i * angularOffset] for i, r in enumerate(rayLengths)]
        return None

    @staticmethod
    def fromRayLengthsToCartesianCoordinates(rayLengths):
        if isinstance(rayLengths, list) and (0 < len(rayLengths)):
            angularOffset = (2 * pi) / len(rayLengths)
            return [PolarCartesianCoordinates.fromPolarToCartesianCoordinates(r, i * angularOffset) for i, r in enumerate(rayLengths)]
        return None

    @staticmethod
    def normalizeRayLengths(rayLengths, threshold):
        if isinstance(rayLengths, list) and (0 < len(rayLengths)):
            cartesianCoords = PolarCartesianCoordinates.fromRayLengthsToCartesianCoordinates(rayLengths)
            xmean = mean([xy[0] for xy in cartesianCoords])
            ymean = mean([xy[1] for xy in cartesianCoords])
            rmean, azimuthMean = PolarCartesianCoordinates.fromCartesianToPolarCoordinates(xmean, ymean)

            if isnan(azimuthMean) or (rmean < threshold):
                return rayLengths
            offset = int(round((len(rayLengths) * azimuthMean) / (2 * pi)))
            return ListUtilities.rotate(rayLengths, offset)
        return None
