'''
Created on 25 juil. 2022

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
from os.path import basename, splitext
import re

from pandas import DataFrame
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.CSVLib import CSVLib
from t4gpd.io.AbstractReader import AbstractReader
from t4gpd.io.CirReader import CirReader


class ValReader(AbstractReader):
    '''
    classdocs
    '''
    RE1 = re.compile(r'^f(\d+)$')

    def __init__(self, inputFile):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.fieldname = basename(splitext(self.inputFile)[0])
        self.data = self.__initialParsing()
        self.ptr = 0

    def __initialParsing(self):
        result = []

        with ValReader.opener(self.inputFile) as f:
            for line in f:
                result += [CSVLib.readLexeme(value) for value in line.split()]

        return result

    def __read(self):
        self.ptr += 1
        return self.data[self.ptr - 1]

    def __readFace(self):
        faceNumber = self.__readFaceNumber()
        nbContours = self.__read()
        result = []
        for ctrNumber in range(nbContours):
            gid = ArrayCoding.encode([faceNumber] if (1 == nbContours) else [faceNumber, ctrNumber])
            result.append({
                'cir_id': gid,
                self.fieldname: self.__read()
                })
        return result

    def __readFaceNumber(self):
        word = self.__read()
        return int(self.RE1.search(word).group(1))

    def run(self):
        result = []

        if 6 < len(self.data):
            nbFaces = self.__read()
            supNumFaces = self.__read()
            minVal = self.__read()
            maxVal = self.__read()
            for _ in range(nbFaces):
                result += self.__readFace()

        return DataFrame(result)
