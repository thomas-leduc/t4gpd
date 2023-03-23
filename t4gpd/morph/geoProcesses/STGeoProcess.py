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

from geopandas import GeoDataFrame
from pandas import concat, DataFrame
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

        if not isinstance(inputGdf, DataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'DataFrame')

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

        if isinstance(self.inputGdf, GeoDataFrame):
            return GeoDataFrame(rows, crs=self.inputGdf.crs)
        return DataFrame(rows)
    '''
    def srun(self):
        fieldnames = [op.ofieldname() for op in self.geoprocessToApply]
        df2 = DataFrame(self.inputGdf.apply(
            lambda row: [op.srunWithArgs(row) for op in self.geoprocessToApply],
            axis=1).to_list(),
            columns=fieldnames)
        df1 = self.inputGdf.copy(deep=True)
        df1.drop(columns=fieldnames, inplace=True)
        df2 = concat([df1, df2], axis=1)
        return GeoDataFrame(df2)

    def _run(self, inputGdf):
        rows = []
        for _, row in inputGdf.iterrows():
            result = dict()
            for op in self.geoprocessToApply:
                result.update(op.runWithArgs(row))
            rows.append(self.updateOrAppend(row, result))
        return GeoDataFrame(rows, crs=inputGdf.crs)

    def parallel(self):
        ncpu, nrows = cpu_count(), len(self.inputGdf)
        loi = unique(linspace(0, nrows, ncpu).astype(int))
        gdfs = [self.inputGdf.iloc[loi[i - 1]:loi[i]] for i in range(1, len(loi))]
        with Pool(processes=ncpu) as pool:
            gdfs = pool.map(self._run, gdfs)
        return concat(gdfs)
    '''
