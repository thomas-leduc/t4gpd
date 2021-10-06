'''
Created on 20 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from t4gpd.commons.PointsDensifierLib import PointsDensifierLib


class STPointsDensifier(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, distance, pathidFieldname=None, adjustableDist=True, removeDuplicate=True):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, 'GeoDataFrame')
        if not ((pathidFieldname is None) or (pathidFieldname in gdf)):
            raise Exception(f'{pathidFieldname} is not a valid fieldname!')

        self.gdf = gdf
        self.pathidFieldname = pathidFieldname
        self.distance = distance
        self.adjustableDist = adjustableDist
        self.removeDuplicate = removeDuplicate

    def run(self):
        rows = []

        if self.removeDuplicate:
            alreadyRegistered = set()
            for rowId, row in self.gdf.iterrows():
                geom = row.geometry
                if not self.pathidFieldname is None:
                    rowId = row[self.pathidFieldname]

                result = PointsDensifierLib.densifyByDistance(
                    geom, self.distance, rowId, contourid=0,
                    adjustableDist=self.adjustableDist)

                for _row in result:
                    tmp = str(_row['geometry'])
                    if tmp not in alreadyRegistered:
                        alreadyRegistered.add(tmp)
                        rows.append(self.updateOrAppend(row, _row))

        else:
            for rowId, row in self.gdf.iterrows():
                geom = row.geometry
                if not self.pathidFieldname is None:
                    rowId = row[self.pathidFieldname]

                result = PointsDensifierLib.densifyByDistance(
                    geom, self.distance, rowId, contourid=0,
                    adjustableDist=self.adjustableDist)

                for _row in result:
                    rows.append(self.updateOrAppend(row, _row))

        return GeoDataFrame(rows, crs=self.gdf.crs)
