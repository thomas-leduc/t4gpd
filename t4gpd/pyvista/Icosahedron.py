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
from numpy import sqrt
from shapely.affinity import scale
from t4gpd.commons.GeoProcess import GeoProcess

from t4gpd.pyvista.commons.Triangle3D import Triangle3D


class Icosahedron(GeoProcess):
    '''
    classdocs
    '''
    SQR5 = sqrt(5)
    INVSQR5 = 1.0 / SQR5
    ALPHA = sqrt((3 - SQR5) / 10)
    BETA = sqrt((5 + SQR5) / 10)
    GAMMA = -(1 + SQR5) / (2 * SQR5)
    DELTA = sqrt((5 - SQR5) / 10)

    def __init__(self, norecursions, radius=None):
        '''
        Constructor
        '''
        p = [
            (0, 0, 1),
            (2 * Icosahedron.INVSQR5, 0, Icosahedron.INVSQR5),
            (Icosahedron.ALPHA, Icosahedron.BETA, Icosahedron.INVSQR5),
            (Icosahedron.GAMMA, Icosahedron.DELTA, Icosahedron.INVSQR5),
            (Icosahedron.GAMMA, -Icosahedron.DELTA, Icosahedron.INVSQR5),
            (Icosahedron.ALPHA, -Icosahedron.BETA, Icosahedron.INVSQR5),
            
            (-Icosahedron.ALPHA, Icosahedron.BETA, -Icosahedron.INVSQR5),
            (-Icosahedron.GAMMA, Icosahedron.DELTA, -Icosahedron.INVSQR5),
            (-Icosahedron.GAMMA, -Icosahedron.DELTA, -Icosahedron.INVSQR5),
            (-Icosahedron.ALPHA, -Icosahedron.BETA, -Icosahedron.INVSQR5),
            (-2 * Icosahedron.INVSQR5, 0, -Icosahedron.INVSQR5),
            (0, 0, -1)
            ]
        # build faces
        self.listOfTriangles = [
            Triangle3D(p[0], p[1], p[2]),
            Triangle3D(p[0], p[2], p[3]),
            Triangle3D(p[0], p[3], p[4]),
            Triangle3D(p[0], p[4], p[5]),
            Triangle3D(p[0], p[5], p[1]),
            Triangle3D(p[1], p[7], p[2]),
            Triangle3D(p[2], p[6], p[3]),
            Triangle3D(p[3], p[10], p[4]),
            Triangle3D(p[4], p[9], p[5]),
            Triangle3D(p[5], p[8], p[1]),

            Triangle3D(p[11], p[9], p[10]),
            Triangle3D(p[11], p[8], p[9]),
            Triangle3D(p[11], p[7], p[8]),
            Triangle3D(p[11], p[6], p[7]),
            Triangle3D(p[11], p[10], p[6]),
            Triangle3D(p[10], p[9], p[4]),
            Triangle3D(p[9], p[5], p[8]),
            Triangle3D(p[8], p[1], p[7]),
            Triangle3D(p[7], p[2], p[6]),
            Triangle3D(p[6], p[3], p[10])
            ]
        self.norecursions = norecursions
        self.radius = radius

    @staticmethod
    def fromNRaysToNRecursions(nrays):
        return 0 if (20 >= nrays) else 1 + Icosahedron.fromNRaysToNRecursions(nrays / 4)

    @staticmethod
    def getNRaysOptions():
        return (20, 80, 320, 1280, 5120, 20480, 81920, 327680)

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

    def __divide(self, listOfTriangles, norecursions):
        result = []
        if (0 >= norecursions):
            for tri in listOfTriangles:
                result.append(tri)
        else:
            for tri in listOfTriangles:
                result += self.__divide(tri.divideBy4OnSphere(), norecursions - 1)
        return result

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
