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
from geopandas.geodataframe import GeoDataFrame

from t4gpd.commons.DensifierLib import DensifierLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STDensifier(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, distance, adjustableDist=True, removeDuplicate=True):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')

        self.inputGdf = inputGdf
        self.distance = distance
        self.adjustableDist = adjustableDist
        self.removeDuplicate = removeDuplicate

    def run(self):
        rows = []

        gid, pathid = 0, 0

        if self.removeDuplicate:
            alreadyRegistered = set()
            for _, row in self.inputGdf.iterrows():
                geom = row.geometry
                gid, pathid, result = DensifierLib.densifyByDistance(geom, self.distance, gid, pathid, self.adjustableDist)
                for _row in result:
                    tmp = str(_row['geometry'])
                    if tmp not in alreadyRegistered:
                        alreadyRegistered.add(tmp)
                        # rows.append(_row)
                        rows.append(self.updateOrAppend(row, _row))
        else:
            for _, row in self.inputGdf.iterrows():
                geom = row.geometry
                gid, pathid, result = DensifierLib.densifyByDistance(geom, self.distance, gid, pathid, self.adjustableDist)
                for _row in result:
                    # rows.append(_row)
                    rows.append(self.updateOrAppend(row, _row))

        return GeoDataFrame(rows, crs=self.inputGdf.crs)
