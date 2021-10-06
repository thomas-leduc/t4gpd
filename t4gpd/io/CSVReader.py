'''
Created on 3 juil. 2020

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
from shapely.geometry import Point
from t4gpd.commons.CSVLib import CSVLib
from t4gpd.commons.GeoProcess import GeoProcess


class CSVReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputFile, xFieldName='longitude', yFieldName='latitude',
                 fieldSep=',', srcEpsgCode='EPSG:4326', dstEpsgCode=None, decimalSep='.'):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.xFieldName = xFieldName
        self.yFieldName = yFieldName
        self.fieldSep = fieldSep
        self.crs = srcEpsgCode
        self.dstEpsgCode = dstEpsgCode
        self.decimalSep = decimalSep

    def run(self):
        _rows = CSVLib.read(self.inputFile, self.fieldSep, self.decimalSep)

        rows = []
        for row in _rows:
            row['geometry'] = Point(row[self.xFieldName], row[self.yFieldName])
            rows.append(row)

        outputGdf = GeoDataFrame(rows, crs=self.crs)

        if not self.dstEpsgCode is None:
            outputGdf = outputGdf.to_crs(self.dstEpsgCode)
        return outputGdf
