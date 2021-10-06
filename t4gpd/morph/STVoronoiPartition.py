'''
Created on 25 sept. 2020

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
from shapely.ops import polygonize, triangulate, unary_union
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, MultiPoint
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STVoronoiPartition(object):
    '''
    classdocs
    '''

    def __init__(self, points, crs=None):
        '''
        Constructor
        '''
        if isinstance(points, MultiPoint):
            _points = points
            self.crs = crs
        elif isinstance(points, GeoDataFrame):
            _points = []
            for geom in points.geometry:
                _points += GeomLib.getListOfShapelyPoints(geom)
            _points = MultiPoint(_points)
            self.crs = points.crs if crs is None else crs
        else:
            raise IllegalArgumentTypeException(points, 'MultiPoint or GeoDataFrame')

        self.tin = triangulate(_points)

    def __append(self, myDict, a, b, circumCircleCenter):
        if a in myDict:
            if b in myDict[a]:
                myDict[a][b].append(circumCircleCenter)
            else:
                myDict[a][b] = [circumCircleCenter]
        else:
            myDict[a] = dict({ b:[circumCircleCenter] })
        
    def __getCircumCircleCenter(self, a, b, c):
        if GeomLib.areAligned(a, b, c):
            ab = GeomLib.distFromTo(a, b)
            bc = GeomLib.distFromTo(b, c)
            ca = GeomLib.distFromTo(c, a)
            if Epsilon.EPSILON > min([ab, bc, ca]):
                return a
            diam = max([ab, bc, ca])
            if diam == ab:
                return GeomLib.getMidPoint(a, b) 
            elif diam == bc:
                return GeomLib.getMidPoint(b, c) 
            elif diam == ca:
                return GeomLib.getMidPoint(c, a)

        line1 = GeomLib.getLineSegmentBisector(a, b)
        line2 = GeomLib.getLineSegmentBisector(b, c)
        return GeomLib.intersect_line_line(line1, line2)

    def getDelaunayTriangles(self):
        return GeoDataFrame([{'geometry':t} for t in self.tin], crs=self.crs)

    def run(self):
        myDict = dict()
        for t in self.tin:
            a, b, c = sorted(t.exterior.coords[:-1])
            circumCircleCenter = self.__getCircumCircleCenter(a, b, c)

            self.__append(myDict, a, b, circumCircleCenter)
            self.__append(myDict, b, c, circumCircleCenter)
            self.__append(myDict, a, c, circumCircleCenter)

        edges = []
        for a in myDict.keys():
            for b in myDict[a].keys():
                if (2 == len(myDict[a][b])):
                    edges.append(LineString(myDict[a][b]))
        edgesUnion = unary_union(edges)

        # Contour network polygonization
        patches = polygonize(edgesUnion)

        # rows = [{ 'geometry':edges }]
        rows = [{ 'gid':gid, 'geometry':patch } for gid, patch in enumerate(patches)]
        return GeoDataFrame(rows, crs=self.crs)
