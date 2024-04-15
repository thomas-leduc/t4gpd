'''
Created on 18 juin 2020

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from shapely import Point
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class BiggestInscribedDisc(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, masksGdf, nsegm=16):
        '''
        Constructor
        '''
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, "GeoDataFrame")
        self.masksGdf = masksGdf
        self.nsegm = nsegm

    def runWithArgs(self, row):
        geom = row.geometry
        if not isinstance(geom, Point):
            raise IllegalArgumentTypeException(geom, "GeoDataFrame of Point")

        minDist, _, _ = GeomLib.getNearestFeature(self.masksGdf, geom)

        return {
            "geometry": geom.buffer(minDist, quad_segs=self.nsegm),
            "insc_diam": 2 * minDist
        }
