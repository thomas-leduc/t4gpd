'''
Created on 17 fev. 2023

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
from shapely.geometry import box, CAP_STYLE, JOIN_STYLE
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STBBox(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, buffDist=0):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, 'GeoDataFrame')
        self.gdf = gdf
        self.buffDist = buffDist

    def run(self):
        bbox = box(*self.gdf.total_bounds).buffer(
            self.buffDist, cap_style=CAP_STYLE.square,
            join_style=JOIN_STYLE.mitre)
        return GeoDataFrame([{'geometry': bbox}], crs=self.gdf.crs)
