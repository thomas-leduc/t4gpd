'''
Created on 7 juin 2023

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
from geopandas.geodataframe import GeoDataFrame
from shapely import union_all
from shapely.geometry import box, JOIN_STYLE
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.GeomLib import GeomLib


class STMakeGroundSurface(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, buffDist=10.0, holed=False):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        self.gdf = gdf
        self.buffDist = buffDist
        self.holed = holed

    def run(self):
        bbox = box(*self.gdf.total_bounds).buffer(self.buffDist, join_style=JOIN_STYLE.mitre)

        if self.holed:
            bbox = bbox.difference(union_all(self.gdf.geometry))

        bbox = GeomLib.forceZCoordinateToZ0(bbox, z0=0.0)
        return GeoDataFrame([{'geometry': bbox}], crs=self.gdf.crs)
