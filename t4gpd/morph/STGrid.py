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
from builtins import len

from geopandas.geodataframe import GeoDataFrame
from numpy import ceil
from shapely.geometry import Point, Polygon

from t4gpd.commons.BoundingBox import BoundingBox
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STGrid(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, dx, dy=None, indoor=None, intoPoint=True):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')

        self.inputGdf = inputGdf
        self.bbox = BoundingBox(inputGdf)
        self.dx = dx
        self.dy = dx if dy is None else dy
        self.nbx = int(ceil(self.bbox.width() / self.dx))
        self.nby = int(ceil(self.bbox.height() / self.dy))
        if indoor in [None, True, False, 'both']:
            self.indoor = indoor
        else:
            raise Exception('Illegal argument: indoor must be chosen in  [None, True, False, "both"]!')
        self.intoPoint = intoPoint

    def __isAnIndoorPoint(self, x, y):
        p = Point(x, y)
        self.inputGdf.sindex
        subGdf = self.inputGdf[self.inputGdf.intersects(p)]
        result = subGdf[subGdf.contains(p)]
        return False if (0 == len(result)) else True 

    def __sample(self):
        dxDiv2 = self.dx / 2.0
        dyDiv2 = self.dy / 2.0

        items = []
        gid = 0
        x = self.bbox.center().x - (self.dx * (self.nbx - 1)) / 2
        for _ in range(self.nbx):
            y = self.bbox.center().y - (self.dy * (self.nby - 1)) / 2
            for _ in range(self.nby):
                if self.intoPoint:
                    geom = Point(x, y)
                else:
                    geom = Polygon([
                        [x - dxDiv2, y - dyDiv2], [x + dxDiv2, y - dyDiv2],
                        [x + dxDiv2, y + dyDiv2], [x - dxDiv2, y + dyDiv2]
                        ])
                if self.indoor is None:
                    items.append({ 'geometry': geom, 'gid': gid })
                else:
                    isIndoor = self.__isAnIndoorPoint(x, y)
                    if (isIndoor == self.indoor) or ('both' == self.indoor):
                        items.append({ 'geometry': geom, 'gid': gid, 'indoor':isIndoor })
                gid += 1
                y += self.dy
            x += self.dx
        return GeoDataFrame(items, crs=self.inputGdf.crs)

    def run(self):
        return self.__sample()
