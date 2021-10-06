'''
Created on 15 dec. 2020

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
from numpy import inf, pi
from shapely.geometry import Point

from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeomLib import GeomLib


class ChrystalAlgorithm(object):
    '''
    classdocs
    '''
    DPI = 2.0 * pi
    PI_DIV_2 = pi / 2.0

    def __init__(self, geom):
        '''
        Constructor
        '''
        self.coords = list(geom.convex_hull.exterior.coords)[:-1]
        self.ncoords = len(self.coords)

    def __angleBetweenNodes(self, i, j, k):
        result = AngleLib.angleBetweenNodes(self.coords[i], self.coords[j], self.coords[k])
        return result if (result <= pi) else self.DPI - result

    def __getThirdNodeWithLowestAngleValue(self, idA, idB):
        minAngle, idC = inf, None
        for i in range(self.ncoords):
            if i not in (idA, idB):
                tmp = self.__angleBetweenNodes(idA, i, idB)
                if tmp < minAngle:
                    minAngle, idC = tmp, i

        return [ idC, minAngle ]

    def __getCircleViaCenterRadius(self, center, radius):
        center = Point(center)
        circle = center.buffer(radius)
        return [circle, center, radius]

    def __getCircleViaDiameter(self, diameter):
        center = GeomLib.getMidPoint(diameter[0], diameter[1])
        radius = GeomLib.distFromTo(center, diameter[1])
        return self.__getCircleViaCenterRadius(center, radius)

    def __aux(self, idA, idB):
        idC, bca_angle = self.__getThirdNodeWithLowestAngleValue(idA, idB)

        if self.PI_DIV_2 <= bca_angle:
            # Un triangle obtusangle est un triangle qui a un angle obtus
            return self.__getCircleViaDiameter([self.coords[idA], self.coords[idB]])
        else:
            abc_angle = self.__angleBetweenNodes(idA, idB, idC)
            cab_angle = self.__angleBetweenNodes(idC, idA, idB)
            maxAngle = max([abc_angle, bca_angle, cab_angle])

            if self.PI_DIV_2 > maxAngle:
                # Un triangle acutangle est un triangle dont tous les angles sont aigus
                center, radius = GeomLib.getCircumcircle(self.coords[idA], self.coords[idB], self.coords[idC])
                return self.__getCircleViaCenterRadius(center, radius)

            elif self.PI_DIV_2 <= abc_angle:
                # Un triangle obtusangle est un triangle qui a un angle obtus
                return self.__aux(idA, idC)

            else:  # elif self.PI_DIV_2 <= cab_angle:
                # Un triangle obtusangle est un triangle qui a un angle obtus
                return self.__aux(idB, idC)

    def run(self):
        if 1 == self.ncoords:
            return self.__getCircleViaCenterRadius(self.coords[0], 0.0)

        elif 2 == self.ncoords:
            return self.__getCircleViaDiameter(self.coords)

        elif 3 == self.ncoords:
            a, b, c = self.coords

            abc_angle = self.__angleBetweenNodes(0, 1, 2)
            bca_angle = self.__angleBetweenNodes(1, 2, 0)
            cab_angle = self.__angleBetweenNodes(2, 0, 1)
            maxAngle = max([abc_angle, bca_angle, cab_angle])

            if self.PI_DIV_2 <= maxAngle:
                # Un triangle obtusangle est un triangle qui a un angle obtus
                if maxAngle == abc_angle:
                    return self.__getCircleViaDiameter([a, c])
                elif maxAngle == bca_angle:
                    return self.__getCircleViaDiameter([b, a])
                else:  # elif maxAngle == cab_angle
                    return self.__getCircleViaDiameter([b, c])
            else:
                # Un triangle acutangle est un triangle dont tous les angles sont aigus
                center, radius = GeomLib.getCircumcircle(a, b, c)
                return self.__getCircleViaCenterRadius(center, radius)

        else:
            idA, idB = [0, 1]
            return self.__aux(idA, idB)
