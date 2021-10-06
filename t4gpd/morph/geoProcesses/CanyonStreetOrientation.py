'''
Created on 7 oct. 2020

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
from shapely.geometry import LineString

from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCastingLib import RayCastingLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess
from t4gpd.commons.AngleLib import AngleLib


class CanyonStreetOrientation(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, buildings, magnitude=10.0):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame')
        self.buildings = buildings
        self.spatialIndex = buildings.sindex
        self.magnitude = magnitude

    def runWithArgs(self, row):
        vp = row.geometry.centroid

        (ux, uy), _ = RayCastingLib.prepareOrientedRays(self.buildings, self.spatialIndex, vp)

        p1 = (vp.x - self.magnitude * uy, vp.y + self.magnitude * ux)
        p2 = (vp.x + self.magnitude * uy, vp.y - self.magnitude * ux)

        azim = AngleLib.toDegrees(AngleLib.normAzimuth([-uy, ux]))
        azim = azim - (180 if (180 <= azim) else 0)

        return {
            'geometry': LineString((p1, p2)),
            'azimuth': azim
            }
