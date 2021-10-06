'''
Created on 11 juin 2020

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
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point, Polygon
from t4gpd.commons.GeomLib import GeomLib
from numpy import ndarray
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class BoundingBox(object):
    '''
    classdocs
    '''

    def __init__(self, obj):
        '''
        Constructor
        '''
        if isinstance(obj, GeoDataFrame):
            self.minx, self.miny, self.maxx, self.maxy = obj.total_bounds
        elif GeomLib.isAShapelyGeometry(obj):
            self.minx, self.miny, self.maxx, self.maxy = obj.bounds
        elif (isinstance(obj, (ndarray, list, tuple)) and (4 == len(obj))):
            self.minx, self.miny, self.maxx, self.maxy = obj
        else:
            raise IllegalArgumentTypeException(obj, 'GeoDataFrame, a Shapely geometry or a 4-uple')
        self.__center = None

    def center(self):
        if self.__center is None:
            cx, cy = (self.minx + self.maxx) / 2.0, (self.miny + self.maxy) / 2.0
            self.__center = Point(cx, cy) 
        return self.__center

    def height(self):
        return (self.maxy - self.miny)

    def width(self):
        return (self.maxx - self.minx)
    
    def asPolygon(self):
        return Polygon([
            (self.minx, self.miny),
            (self.minx, self.maxy),
            (self.maxx, self.maxy),
            (self.maxx, self.miny)
            ])

    def __str__(self):
        return '%s:: (%f, %f) -> (%f, %f)' % (
            __name__,
            self.minx, self.miny,
            self.maxx, self.maxy
            )
