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
from numpy import arctan2, cos, linspace, pi, round, sin
from numpy.random import uniform
from shapely.geometry import LineString, Point, Polygon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class SequenceRadii(object):
    '''
    classdocs
    '''

    def __init__(self, nbranchs=8, width=12.0, length=100.0, varLength=None):
        '''
        Constructor
        '''
        self.nbranchs = nbranchs
        self.width = 0.5 * float(width)
        self.length = length - self.width
        self.incAngle = arctan2(self.width, self.length)
        self.angles = linspace(0, 2 * pi, num=nbranchs, endpoint=False)
        self.mainDirs = list(zip(cos(self.angles), sin(self.angles)))

        if varLength is None:
            self.lowerBoundary = 1.0
        elif (0 <= varLength <= 1.0):
            self.lowerBoundary = 1.0 - varLength
        else:
            raise IllegalArgumentTypeException(varLength, "Float value between 0.0 and 1.0 or None")

    def getBranch(self, i, centre=[0, 0]):
        length = uniform(low=self.lowerBoundary, high=1) * self.length
        ux, uy = self.mainDirs[i]
        p = (centre[0] + length * ux, centre[1] + length * uy)
        return LineString([centre, p])

    def getSector(self, sector, centre=[0, 0]):
        length = uniform(low=self.lowerBoundary, high=1) * self.length
        i, j = sector

        if ((0 == i) and (self.nbranchs == j)):
            result = Point(centre).buffer(length)
        else:
            cx, cy = centre
            angle0, angle1 = self.angles[i], self.angles[j]
            npts = round((angle1 - angle0) / self.incAngle).astype(int)

            result = [centre]
            for angle in linspace(angle0, angle1, num=npts, endpoint=True):
                p = (cx + length * cos(angle), cy + length * sin(angle))
                result.append(p)
            result.append(centre)
            result = Polygon(result)

        return result

    def getWidth(self):
        return self.width
