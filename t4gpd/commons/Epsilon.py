'''
Created on 17 juin 2020

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

from shapely.geometry import Point

from numpy import ceil, float64, floor


class Epsilon(object):
    '''
    classdocs
    '''
    EPSILON = 1E-6

    @staticmethod
    def equals(x, y, epsilon=EPSILON):
        # print 'compare:', x, y, type(x), type(y)
        if ((isinstance(x, int) or isinstance(x, float) or isinstance(x, float64)) and
            (isinstance(y, int) or isinstance(y, float) or isinstance(y, float64))):
            if (abs(x - y) <= epsilon):
                return True
        elif (isinstance(x, Point) and isinstance(y, Point)):
            if ((abs(x.x - y.x) < epsilon) and (abs(x.y - y.y) < epsilon)):
                return True
        elif (isinstance(x, list) or isinstance(x, tuple)) and (isinstance(y, list) or isinstance(y, tuple)):
            if len(x) == len(y):
                return all([Epsilon.equals(x[i], y[i], epsilon) for i in range(len(x))])
        return False

    @staticmethod
    def isANonDecimalValue(value, epsilon=EPSILON):
        aa = abs(value)
        aaa = aa - int(aa)
        return Epsilon.isZero(aaa, epsilon) or Epsilon.isZero(aaa - 1, epsilon)

    @staticmethod
    def isAMultipleOf(a, b, epsilon=EPSILON):
        return Epsilon.isANonDecimalValue(a / b, epsilon)

    @staticmethod
    def isZero(x, epsilon=EPSILON):
        if (isinstance(x, int) or isinstance(x, float) or isinstance(x, float64)):
            return Epsilon.equals(x, 0, epsilon)
        elif isinstance(x, Point):
            return (Epsilon.equals(x.x, 0, epsilon) and Epsilon.equals(x.y, 0, epsilon))
        elif (isinstance(x, list) or isinstance(x, tuple)):
            return all([Epsilon.isZero(item, epsilon) for item in x])
        raise Exception('Illegal argument: x must be int, float, QgsPoint, list, or tuple (of int, float or QgsPoint)!')

    @staticmethod
    def round(x, decimals, flag):
        x, flag = x * 10 ** decimals, flag.upper()
        if 'UP' == flag:
            return ceil(x) * 10 ** (-decimals)
        elif 'DOWN' == flag:
            return floor(x) * 10 ** (-decimals)
        raise Exception('Illegal argument: flag must be "up" or "down"!')
