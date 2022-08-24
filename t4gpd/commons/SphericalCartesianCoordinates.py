'''
Created on 19 juil. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from numpy import arcsin, arctan2, cos, sin, sqrt


class SphericalCartesianCoordinates(object):
    '''
    classdocs
    '''

    @staticmethod
    def fromCartesianToSphericalCoordinates(x, y, z):
        r = sqrt((x ** 2) + (y ** 2) + (z ** 2))
        if (0 == r):
            return 0, 0, 0
        lon = arctan2(y, x)  # LONGITUDE
        lat = arcsin(z / r)  # LATITUDE
        return r, lon, lat

    @staticmethod
    def fromSphericalToCartesianCoordinates(r, lon, lat):
        x = r * cos(lon) * cos(lat)
        y = r * sin(lon) * cos(lat)
        z = r * sin(lat)
        return x, y, z
