'''
Created on 12 nov. 2020

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
from shapely.geometry import Point

from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.ShortestPathLib import ShortestPathLib


class STShortestPath(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, roads, fromPoints, toPoints):
        '''
        Constructor
        '''
        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, 'GeoDataFrame')
        if not isinstance(fromPoints, (GeoDataFrame, Point)):
            raise IllegalArgumentTypeException(fromPoints, 'GeoDataFrame or single Point')
        if not isinstance(toPoints, (GeoDataFrame, Point)):
            raise IllegalArgumentTypeException(toPoints, 'GeoDataFrame or single Point')

        self.graph = ShortestPathLib(roads)
        self.roads = roads

        if isinstance(fromPoints, GeoDataFrame):
            self.fromPoints = list(fromPoints.centroid)
        else:
            self.fromPoints = [fromPoints]

        if isinstance(toPoints, GeoDataFrame):
            self.toPoints = list(toPoints.centroid)
        else:
            self.toPoints = [toPoints]

    def run(self):
        gid, rows = 0, []
        for fromPoint in self.fromPoints:
            for toPoint in self.toPoints:
                pathGeom, pathLen = self.graph.shortestPath(fromPoint, toPoint)
                if not pathGeom is None:
                    rows.append({'gid':gid, 'pathLen': pathLen, 'fromPoint': fromPoint.wkt,
                                 'toPoint': toPoint.wkt, 'geometry': pathGeom})
                    gid += 1

        return GeoDataFrame(rows, crs=self.roads.crs)
