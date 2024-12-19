'''
Created on 25 sept. 2020

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from shapely import MultiPoint
from shapely.ops import triangulate, voronoi_diagram
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STVoronoiPartition(object):
    '''
    classdocs
    '''

    def __init__(self, gdf):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        _multiPoints = []
        for geom in gdf.geometry:
            _multiPoints += GeomLib.getListOfShapelyPoints(geom, withoutClosingLoops=True)
        _multiPoints = MultiPoint(_multiPoints)

        self.gdf = gdf
        self.crs = gdf.crs
        self.multiPoints = _multiPoints

    def getDelaunayTriangles(self):
        return GeoDataFrame([{"geometry": t} for t in triangulate(self.multiPoints)], crs=self.crs)

    def run(self):
        vor = GeoDataFrame([{"geometry": v} for v in voronoi_diagram(
            self.multiPoints).geoms], crs=self.crs)
        vor = vor.sjoin(self.gdf, how="inner", predicate="intersects", rsuffix="right01234567889")
        vor.drop(columns="index_right01234567889", inplace=True)
        return vor
