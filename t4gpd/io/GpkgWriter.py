'''
Created on 11 oct. 2022

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
from geopandas import GeoDataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class GpkgWriter(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, mapOfGdf, gpkgOutputFile):
        '''
        Constructor
        '''
        if not isinstance(mapOfGdf, dict):
            raise IllegalArgumentTypeException(mapOfGdf, '{ "layername": GeoDataFrame, ... }')
        for layername, gdf in mapOfGdf.items():
            if not isinstance(layername, str):
                raise IllegalArgumentTypeException(layername, 'layername')
            if not isinstance(gdf, GeoDataFrame):
                raise IllegalArgumentTypeException(gdf, 'GeoDataFrame')
        self.mapOfGdf = mapOfGdf

        self.gpkgOutputFile = gpkgOutputFile

    def run(self):
        for layername, df in self.mapOfGdf.items():
            df.to_file(self.gpkgOutputFile, driver='GPKG', layer=layername)

        print(f'{self.gpkgOutputFile} has been written!')
        return None
