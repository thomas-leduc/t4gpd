'''
Created on 16 juin 2020

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
from inspect import isclass

from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class STGeoProcess(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, geoprocessToApply, inputGdf):
        '''
        Constructor
        '''
        if not (self.__is_a_geoprocess(geoprocessToApply) or 
                self.__is_a_collection_of_geoprocesses(geoprocessToApply)):
            raise IllegalArgumentTypeException(geoprocessToApply, '(list of) AbstractGeoprocess')

        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')

        if (self.__is_a_geoprocess(geoprocessToApply)):
            self.geoprocessToApply = [geoprocessToApply]
        else:
            self.geoprocessToApply = geoprocessToApply
        self.inputGdf = inputGdf

    def __is_a_geoprocess(self, obj):
        return (isinstance(obj, AbstractGeoprocess) or 
                (isclass(obj) and issubclass(obj, AbstractGeoprocess)))

    def __is_a_collection_of_geoprocesses(self, obj):
        return (isinstance(obj, (list, tuple)) and all([self.__is_a_geoprocess(_obj) for _obj in obj]))

    def run(self):
        rows = []
        for _, row in self.inputGdf.iterrows():
            result = dict()
            for op in self.geoprocessToApply:
                result.update(op.runWithArgs(row))
            rows.append(self.updateOrAppend(row, result))
        return GeoDataFrame(rows, crs=self.inputGdf.crs)
