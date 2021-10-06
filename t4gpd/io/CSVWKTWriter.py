'''
Created on 31 aug. 2020

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
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class CSVWKTWriter(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, outputFile, fieldSep=';', decimalSep='.'):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf
        self.outputFile = outputFile
        self.fieldSep = fieldSep
        self.decimalSep = decimalSep

    def __getFields(self):
        fields = dict()
        for fname in self.inputGdf.columns:
            ftype = str(self.inputGdf.dtypes[fname])
            if 'geometry' != ftype:
                fields[fname] = ftype
        return fields

    def __printFieldValue(self, fields, row, fname):
        if ('.' != self.decimalSep) and ('float64' == fields[fname]):
            return str(row[fname]).replace('.', self.decimalSep)
        return str(row[fname])

    def run(self):
        fields = self.__getFields()

        with open(self.outputFile, 'w') as f:
            f.write('%s%sthe_geom\n' % (
                self.fieldSep.join([fname for fname in fields.keys()]),
                self.fieldSep
                ))

            for _, row in self.inputGdf.iterrows():
                wktGeom = row.geometry.wkt
                tmp = self.fieldSep.join([self.__printFieldValue(fields, row, fname) for fname in fields.keys()] + [wktGeom])
                f.write(tmp + '\n')
