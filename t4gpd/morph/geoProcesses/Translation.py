'''
Created on 14 sept. 2020

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
from builtins import isinstance

from shapely.affinity import translate
from shapely.geometry import Point
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class Translation(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, vector):
        '''
        Constructor
        '''
        if not (isinstance(vector, Point) or isinstance(vector, (list, tuple))):
            raise IllegalArgumentTypeException(vector, 'Point, list or tuple') 
        self.xoff = vector.x if isinstance(vector, Point) else vector[0]
        self.yoff = vector.y if isinstance(vector, Point) else vector[1]
        if (isinstance(vector, Point) and vector.has_z):
            self.zoff = vector.z
        elif (isinstance(vector, (list, tuple)) and (3 == len(vector))):
            self.zoff = vector[2]
        else:
            self.zoff = None

    def runWithArgs(self, row):
        if self.zoff is None:
            return { 
                'geometry': translate(row.geometry, xoff=self.xoff, yoff=self.yoff) 
                }
        return { 
            'geometry': translate(row.geometry, xoff=self.xoff, yoff=self.yoff, zoff=self.zoff)
            }
