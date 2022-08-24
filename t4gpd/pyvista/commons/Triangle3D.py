'''
Created on 23 juin 2022

self.author: tleduc

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
from numpy import arccos, pi, sqrt
from shapely.geometry import Polygon
from t4gpd.commons.GeomLib3D import GeomLib3D


class Triangle3D(object):
    '''
    classdocs
    '''

    def __init__(self, ptA, ptB, ptC):
        '''
        Constructor
        '''
        self.ptA, self.ptB, self.ptC = ptA, ptB, ptC  # A REVOIR

    def centroid(self):
        x = (self.ptA[0] + self.ptB[0] + self.ptC[0]) / 3.0
        y = (self.ptA[1] + self.ptB[1] + self.ptC[1]) / 3.0
        z = (self.ptA[2] + self.ptB[2] + self.ptC[2]) / 3.0
        return [ x, y, z ]

    def divideBy4OnSphere(self):
        midAB = self.__midOfEdgeOnSphere(self.ptA, self.ptB)
        midBC = self.__midOfEdgeOnSphere(self.ptB, self.ptC)
        midCA = self.__midOfEdgeOnSphere(self.ptC, self.ptA)
        return [
            Triangle3D(self.ptA, midAB, midCA),
            Triangle3D(midAB, self.ptB, midBC),
            Triangle3D(midCA, midBC, self.ptC),
            Triangle3D(midBC, midCA, midAB)
            ]

    def __midOfEdgeOnSphere(self, pt1, pt2):
        x = (pt1[0] + pt2[0]) / 2.0
        y = (pt1[1] + pt2[1]) / 2.0
        z = (pt1[2] + pt2[2]) / 2.0
        invNorm = 1.0 / sqrt(x ** 2 + y ** 2 + z ** 2)
        return [ x * invNorm, y * invNorm, z * invNorm ]

    def area3D(self):
        # Heron's formula
        len1 = GeomLib3D.distFromTo(self.ptA, self.ptB)
        len2 = GeomLib3D.distFromTo(self.ptB, self.ptC)
        len3 = GeomLib3D.distFromTo(self.ptC, self.ptA)
        sp = (len1 + len2 + len3) / 2.0
        return sqrt(sp * (sp - len1) * (sp - len2) * (sp - len3))

    def sphericalArea(self, mockupCentre=[0, 0, 0], radius=1.0):
        # Girard's theorem - area of the spherical triangle
        oa = GeomLib3D.vector_to(mockupCentre, self.ptA)
        ob = GeomLib3D.vector_to(mockupCentre, self.ptB)
        oc = GeomLib3D.vector_to(mockupCentre, self.ptC)

        normalOAB = GeomLib3D.unitVector(GeomLib3D.crossProduct(oa, GeomLib3D.vector_to(self.ptA, self.ptB)))
        normalOBC = GeomLib3D.unitVector(GeomLib3D.crossProduct(ob, GeomLib3D.vector_to(self.ptB, self.ptC)))
        normalOCA = GeomLib3D.unitVector(GeomLib3D.crossProduct(oc, GeomLib3D.vector_to(self.ptC, self.ptA)))

        alpha = arccos(GeomLib3D.dotProduct(
            GeomLib3D.unitVector(GeomLib3D.crossProduct(oa, normalOAB)),
            GeomLib3D.unitVector(GeomLib3D.crossProduct(oa, normalOCA))
            ))
        beta = arccos(GeomLib3D.dotProduct(
            GeomLib3D.unitVector(GeomLib3D.crossProduct(ob, normalOAB)),
            GeomLib3D.unitVector(GeomLib3D.crossProduct(ob, normalOBC))
            ))
        gamma = arccos(GeomLib3D.dotProduct(
            GeomLib3D.unitVector(GeomLib3D.crossProduct(oc, normalOBC)),
            GeomLib3D.unitVector(GeomLib3D.crossProduct(oc, normalOCA))
            ))

        return (alpha + beta + gamma - pi) * radius ** 2

    def toPolygon(self):
        return Polygon([self.ptA, self.ptB, self.ptC, self.ptA])
