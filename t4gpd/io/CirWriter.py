'''
Created on 10 mars 2021

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
from shapely.geometry import MultiPolygon, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class CirWriter(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, outputFile, translate=False):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf
        self.outputFile = outputFile

        minx, miny, _, _ = self.inputGdf.total_bounds
        self.llc = [minx, miny] if translate else [0, 0]

    def __printCoordinates(self, coord, llc=[0, 0]):
        return '\t%g\t%g\t%g' % (coord[0] - llc[0], coord[1] - llc[1], coord[2])

    def __printHeader(self):
        return '%d\t%d\r\n%s' % (
            len(self.inputGdf),
            len(self.inputGdf),
            '\t99999\t99999\r\n' * 5)

    def __printGeometry(self, faceIdx, geometry):
        if GeomLib.isPolygonal(geometry):
            if isinstance(geometry, Polygon):
                nCtrs = 1
                _polygons = [geometry]

            elif isinstance(geometry, MultiPolygon):
                nCtrs = len(geometry.geoms)
                _polygons = geometry.geoms

            _normal = GeomLib3D.getFaceNormalVector(_polygons[0])
            result = 'f%d %d\r\n%s\r\n' % (faceIdx, nCtrs, self.__printCoordinates(_normal))
            for _geom in _polygons:
                result += self.__printPolygon(_geom)
            return result

        raise IllegalArgumentTypeException(geometry, 'Polygon or MultiPolygon')

    def __printPolygon(self, polygon):
        result = 'c%d\r\n' % (len(polygon.interiors))
        result += self.__printRing(polygon.exterior)
        for hole in polygon.interiors:
            result += 't\r\n'
            result += self.__printRing(hole)
        return result

    def __printRing(self, ring):
        ring = GeomLib.addZCoordinateIfNecessary(ring)
        return '%d\r\n%s\r\n' % (
            len(ring.coords),
            '\r\n'.join([self.__printCoordinates(c, self.llc) for c in ring.coords]))

    def run(self):
        with open(self.outputFile, 'w') as f:
            f.write(self.__printHeader())

            faceIdx = 1
            for _, row in self.inputGdf.iterrows():
                _geom = row.geometry
                f.write(self.__printGeometry(faceIdx, _geom))
                faceIdx += 1
