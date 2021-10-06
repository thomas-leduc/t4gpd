'''
Created on 14 dec. 2020

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
from shapely.ops import unary_union
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STExtractOpenSpaces(GeoProcess):
    '''
    classdocs
    '''
    EPSILON = 1e-3

    def __init__(self, envelopeGdf, buildings, removeCourtyards=False):
        '''
        Constructor
        '''
        if not isinstance(envelopeGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(envelopeGdf, 'GeoDataFrame')
        self.envelopeGdf = envelopeGdf

        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame')
        self.buildings = buildings

        self.removeCourtyards = removeCourtyards

    def run(self):
        # Use a buffer to avoid slivers
        xunion = lambda gdf: unary_union([g.buffer(self.EPSILON) for g in gdf.geometry]).buffer(self.EPSILON)

        envelope = xunion(self.envelopeGdf)
        buildings = xunion(self.buildings)
        if self.removeCourtyards:
            buildings = GeomLib.removeHoles(buildings)

        result = envelope.difference(buildings)
        # Use a buffer to avoid slivers
        result = result.buffer(self.EPSILON)

        return GeoDataFrame([{'geometry':result}], crs=self.buildings.crs)
