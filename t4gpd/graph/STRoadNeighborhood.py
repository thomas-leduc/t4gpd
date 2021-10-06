'''
Created on 16 nov. 2020

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
from shapely.geometry import MultiLineString, Point
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.NeighborhoodLib import NeighborhoodLib


class STRoadNeighborhood(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, roads, fromPoints, maxDists):
        '''
        Constructor
        '''
        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, 'GeoDataFrame')
        if not isinstance(fromPoints, (GeoDataFrame, Point)):
            raise IllegalArgumentTypeException(fromPoints, 'GeoDataFrame or single Point')
        if not isinstance(maxDists, (str, float, int)):
            raise IllegalArgumentTypeException(maxDists, 'String fieldname, float or int values')

        self.roads = roads

        if isinstance(fromPoints, GeoDataFrame):
            if maxDists in fromPoints:
                self.fromPointsAndMaxDists = list(zip(fromPoints.centroid, fromPoints[maxDists]))
            elif isinstance(maxDists, (float, int)):
                self.fromPointsAndMaxDists = list(zip(fromPoints.centroid, [maxDists] * len(fromPoints)))
        elif isinstance(maxDists, (float, int)):
            self.fromPointsAndMaxDists = [fromPoints, maxDists]
        else:
            raise Exception('%s is neither a float value nor a fromPoints fieldname!' % maxDists)

    def run(self):
        rows = []
        for gid, (fromPoint, maxDist) in enumerate(self.fromPointsAndMaxDists):
            gdf = NeighborhoodLib.neighborhood(self.roads, fromPoint, maxDist)
            rows.append({
                'gid':gid, 'fromPoint': fromPoint.wkt, 'maxDist': maxDist,
                'geometry': MultiLineString([geom for geom in gdf.geometry])
                })
            gid += 1
        return GeoDataFrame(rows, crs=self.roads.crs)
