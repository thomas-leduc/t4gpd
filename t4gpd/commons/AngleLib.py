'''
Created on 19 juin 2020

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
from numpy import arctan2, pi 


class AngleLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def toDegrees(angle):
        return (180.0 * angle) / pi

    @staticmethod
    def toRadians(angle):
        return (pi * angle) / 180.0

    @staticmethod
    def normAzimuth(direction):
        result = arctan2(direction[1], direction[0])
        if (result < 0.0):
            return (2.0 * pi + result)
        else:
            return result

    @staticmethod
    def angleBetween(direction1, direction2):
        result = AngleLib.normAzimuth(direction2) - AngleLib.normAzimuth(direction1)
        if (result < 0.0):
            return (2.0 * pi + result)
        else:
            return result

    @staticmethod
    def angleBetweenNodes(node1, orig, node2):
        return AngleLib.angleBetween([ node1[0] - orig[0] , node1[1] - orig[1] ], [ node2[0] - orig[0] , node2[1] - orig[1] ])
