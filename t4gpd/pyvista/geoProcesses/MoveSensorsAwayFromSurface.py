'''
Created on 22 juin 2022

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
from shapely.geometry import Point
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class MoveSensorsAwayFromSurface(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, normalFieldname, dist=1e-6):
        '''
        Constructor
        '''
        assert isinstance(sensorsGdf, GeoDataFrame), 'sensorsGdf must be a GeoDataFrame'
        assert (normalFieldname in sensorsGdf), 'f{normalFieldname} must be a sensorsGdf field name'
        self.sensorsGdf = sensorsGdf
        self.normalFieldname = normalFieldname
        self.dist = dist

    def runWithArgs(self, row):
        p = row.geometry
        assert isinstance(p, Point), 'sensorsGdf must be a GeoDataFrame of Points'
        n = row[self.normalFieldname]

        return { 'geometry': Point([
            p.x + self.dist * n[0],
            p.y + self.dist * n[1],
            p.z + self.dist * n[2],
            ]) }
