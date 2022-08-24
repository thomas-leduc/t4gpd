'''
Created on 27 juil. 2022

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
from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.pyqgis.AddMemoryLayer import AddMemoryLayer


class Emphasizer(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, layer, fieldname, fieldvalues, bufferRadius):
        '''
        Constructor
        '''
        if not isinstance(layer, GeoDataFrame):
            raise IllegalArgumentTypeException(layer, 'GeoDataFrame')

        if fieldname not in layer:
            raise Exception(f'{fieldname} is not a relevant field name!')

        self.layer = layer[ layer[fieldname].isin(fieldvalues) ].copy(deep=True)
        self.layer.geometry = self.layer.geometry.apply(
            lambda g: g.centroid.buffer(bufferRadius)) 

    def run(self):
        return AddMemoryLayer(self.layer, 'highlighted layer').run()
