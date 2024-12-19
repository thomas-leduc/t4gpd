'''
Created on 31 dec. 2020

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
from shapely import get_parts, union_all
from shapely.ops import polygonize
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STPolygonize(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, patchid="gid"):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        self.gdf = gdf
        self.patchid = patchid

    def run(self):
        contours = [GeomLib.toListOfLineStrings(geom) for geom in self.gdf.geometry]

        # Contour union
        contourUnion = union_all(contours)

        # Contour network polygonization
        patches = polygonize(get_parts(contourUnion))

        rows = [{self.patchid: i, "geometry": patch}
                for i, patch in enumerate(patches)]
        return GeoDataFrame(rows, crs=self.gdf.crs)
