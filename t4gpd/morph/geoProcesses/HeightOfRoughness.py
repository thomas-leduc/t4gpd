'''
Created on 5 janv. 2021

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
from numpy import pi
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class HeightOfRoughness(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, itemsGdf, elevationFieldName='HAUTEUR', buffDist=None):
        '''
        Constructor
        '''
        if not isinstance(itemsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(itemsGdf, 'GeoDataFrame')
        self.itemsGdf = itemsGdf
        self.spatialIndex = itemsGdf.sindex

        self.elevationFieldName = elevationFieldName
        self.buffDist = buffDist

    def runWithArgs(self, row):
        rowGeom, zone, zoneArea = row.geometry, None, 0.0

        if (self.buffDist is None) and (GeomLib.isPolygonal(rowGeom)):
            zone, zoneArea = rowGeom, rowGeom.area

        elif isinstance(self.buffDist, (int, float)):
            zone, zoneArea = rowGeom.centroid.buffer(self.buffDist), pi * self.buffDist ** 2

        if (0.0 < zoneArea):
            _features = GeomLib.extractFeaturesWithin(zone, self.itemsGdf, self.spatialIndex)
            _vol = sum([f['geometry'].area * f[self.elevationFieldName] for f in _features])
            return { 'hre': float(_vol / zoneArea) }

        return { 'hre': None }
