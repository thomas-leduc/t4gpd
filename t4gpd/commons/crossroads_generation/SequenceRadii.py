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
from numpy import arctan2, cos, pi, sin
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union


class SequenceRadii(object):
    '''
    classdocs
    '''

    def __init__(self, nbranchs=8, width=12.0, length=100.0):
        '''
        Constructor
        '''
        self.nbranchs = nbranchs
        self.width = 0.5 * float(width)
        self.length = float(length)
        # self.alpha = arcsin(self.width / self.length)
        self.alpha = 2 * arctan2(self.width, self.length)
        self.angles = [((2.0 * pi * i) / nbranchs) for i in range(nbranchs)]
        self.mainDirs = [(cos(angle), sin(angle)) for angle in self.angles]
        self.incAngle = self.alpha / 2.0

    def getBranch(self, i, centre=[0, 0]):
        w, hw, l = self.width, 0.0, (self.length * cos(self.alpha))
        cx, cy = centre
        ux, uy = self.mainDirs[i]
        vx, vy = -uy, ux
        p0 = (cx + hw * ux - w * vx, cy + hw * uy - w * vy)
        p1 = (cx + l * ux - w * vx, cy + l * uy - w * vy)
        p2 = (cx + l * ux + w * vx, cy + l * uy + w * vy)
        p3 = (cx + hw * ux + w * vx, cy + hw * uy + w * vy)
        return Polygon([p0, p1, p2, p3, p0])

    def getSector(self, sector, centre=[0, 0]):
        i, j = sector

        if ((0 == i) and (self.nbranchs == j)):
            result = Point(centre).buffer(self.length)
        else:
            angle0, angle1 = self.angles[i], self.angles[j]
            angle1 = angle1 + 2.0 * pi if (angle0 > angle1) else angle1
            l = self.length * cos(self.alpha)
            cx, cy = centre

            result = [centre]
            angle = angle0
            while angle < angle1:
                p = (cx + cos(angle) * l, cy + sin(angle) * l)
                result.append(p)
                angle += self.incAngle
            result.append(centre)

            br1 = self.getBranch(i, centre)
            br2 = self.getBranch(j, centre)
            polygons = [br1, br2, Polygon(result)]

            # Use a buffer to avoid slivers
            result = unary_union(polygons).buffer(0.001)

        return result
