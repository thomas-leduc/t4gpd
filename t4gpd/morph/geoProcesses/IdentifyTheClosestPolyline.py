'''
Created on 17 sept. 2020

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
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class IdentifyTheClosestPolyline(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, roadsGdf, roadsIdFieldname, defaultBuffDist=40.0):
        '''
        Constructor
        '''
        if not isinstance(roadsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(roadsGdf, 'GeoDataFrame')
        self.roadsGdf = roadsGdf
        self.spatialIdx = roadsGdf.sindex

        if roadsIdFieldname not in roadsGdf:
            raise Exception('%s is not a relevant field name!' % (roadsIdFieldname))
        self.roadsIdFieldname = roadsIdFieldname

        self.buffDist = defaultBuffDist

    def __sign(self, x):
        if (0 == x):
            return 0
        return -1 if (x < 0) else 1

    def runWithArgs(self, row):
        geom = row.geometry

        self.buffDist = 40.0
        minDist, nearestPoint, nearestRow = GeomLib.getNearestFeature(
            self.roadsGdf, self.spatialIdx, geom, self.buffDist)

        nearestRoad = nearestRow.geometry
        curvilinearAbscissa = nearestRoad.project(nearestPoint)

        otherPoint = nearestRoad.interpolate(curvilinearAbscissa + 1e-2)
        roadSide = self.__sign(GeomLib.zCrossProduct(
            otherPoint.coords[0], nearestPoint.coords[0], geom.coords[0]))

        return { 
            # 'geometry': LineString((geom, nearestPoint)),
            'road_id': nearestRow[self.roadsIdFieldname],
            'road_dist': minDist,
            'road_absc': curvilinearAbscissa,
            'road_side': roadSide
            }
