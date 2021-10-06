'''
Created on 8 oct. 2020

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
import re
from shapely.geometry import Polygon

from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.CSVLib import CSVLib
from t4gpd.commons.GeoProcess import GeoProcess


class CirReader(GeoProcess):
    '''
    classdocs
    '''
    RE1 = re.compile(r'^f(\d+)$')
    RE2 = re.compile(r'^c(\d+)$')
    
    def __init__(self, inputFile):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.data = self.__initialParsing()
        self.dataLen = len(self.data)
        self.ptr = 0

    def __eof(self):
        return (self.dataLen <= self.ptr)

    def __initialParsing(self):
        result = []
        with open(self.inputFile, 'r') as f:
            for line in f:
                result += [CSVLib.readLexeme(value) for value in line.split()]
        return result

    def __read(self):
        self.ptr += 1
        return self.data[self.ptr - 1]
 
    def __read3Coords(self):
        return self.__read(), self.__read(), self.__read()

    def __readBBox(self):
        self.ptr += 10

    def __readContour(self):
        nbHoles = self.__readNumberOfHoles()
        extRing = self.__readPolyline()
        intRings = []
        for _ in range(nbHoles):
            if 't' == self.__read():
                intRings.append(self.__readPolyline())
        if 0 < nbHoles:
            return Polygon(extRing, intRings)
        return Polygon(extRing)

    def __readFace(self):
        faceNumber = self.__readFaceNumber()
        nbContours = self.__read()
        normal = self.__read3Coords()
        result = []
        for _ in range(nbContours):
            result.append(self.__readContour())
        return result

    def __readFaceNumber(self):
        word = self.__read()
        return int(self.RE1.search(word).group(1))

    def __readNumberOfHoles(self):
        word = self.__read()
        return int(self.RE2.search(word).group(1))

    def __readPolyline(self):
        nbOfNodes, result = self.__read(), []
        for _ in range(nbOfNodes):
            result.append(self.__read3Coords())
        return result[:-1]

    def __rewind(self):
        self.ptr -= 1

    def run(self):
        result = []

        if 30 < len(self.data):
            nbFaces = self.__read()
            supNumFaces = self.__read()
            self.__readBBox()
            for _ in range(nbFaces):
                result += self.__readFace()

        return GeoDataFrame(
            [{'geometry': geom} for geom in result]
            )
