'''
Created on 23 juin 2022

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
from geopandas import GeoDataFrame
from numpy import sum 
from shapely.affinity import scale 
from t4gpd.commons.GeoProcess import GeoProcess

from t4gpd.pyvista.commons.Triangle3D import Triangle3D


class GeodeCiel(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, norecursions, radius=None):
        '''
        Constructor
        '''
        self.listOfTriangles = [
            Triangle3D([0, 1, 0], [0, 0, 1], [1, 0, 0]),
            Triangle3D([0, 1, 0], [0, 0, -1], [1, 0, 0])
            ]
        self.norecursions = norecursions
        self.radius = radius

    def __divide(self, listOfTriangles, norecursions):
        result = []
        if (0 >= norecursions):
            for tri in listOfTriangles:
                a, b, c = tri.ptA, tri.ptB, tri.ptC
                # Add NE triangle
                result.append(tri)
                # Add NW triangle
                result.append(Triangle3D(self.__mirrorX(a), self.__mirrorX(b), self.__mirrorX(c)))
                # Add SE triangle
                result.append(Triangle3D(self.__mirrorY(a), self.__mirrorY(b), self.__mirrorY(c)))
                # Add SW triangle
                result.append(Triangle3D(self.__mirrorXY(a), self.__mirrorXY(b), self.__mirrorXY(c)))
        else:
            for tri in listOfTriangles:
                result += self.__divide(tri.divideBy4OnSphere(), norecursions - 1)
        return result

    def __mirrorX(self, pt):
        return [ -pt[0], pt[1], pt[2] ]

    def __mirrorY(self, pt):
        return [ pt[0], -pt[1], pt[2] ]

    def __mirrorXY(self, pt):
        return [ -pt[0], -pt[1], pt[2] ]

    @staticmethod
    def fromNRaysToNRecursions(nrays):
        return 0 if (8 >= nrays) else 1 + GeodeCiel.fromNRaysToNRecursions(nrays / 4)

    @staticmethod
    def getNRaysOptions():
        # return (4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144)
        return (8, 32, 128, 512, 2048, 8192, 32768, 131072, 524288)

    def getRays(self):
        listOfTriangles = self.__divide(self.listOfTriangles, self.norecursions)
        return [tri.centroid() for tri in listOfTriangles]

    def getRaysAndWeights(self):
        listOfTriangles = self.__divide(self.listOfTriangles, self.norecursions)
        rays = [tri.centroid() for tri in listOfTriangles]
        _areas = [tri.sphericalArea() for tri in listOfTriangles]
        _sumOfAreas = sum(_areas)
        weights = [_area / _sumOfAreas for _area in _areas]
        return rays, weights

    def run(self):
        listOfTriangles = self.__divide(self.listOfTriangles, self.norecursions)
        if (self.radius is None) or (1 == self.radius):
            rows = [{'geometry': tri.toPolygon()} for tri in listOfTriangles]
        else:
            rows = [{'geometry': scale(
                tri.toPolygon(),
                xfact=self.radius,
                yfact=self.radius,
                zfact=self.radius,
                origin=(0, 0, 0))} for tri in listOfTriangles]
        return GeoDataFrame(rows)
