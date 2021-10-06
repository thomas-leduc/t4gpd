'''
Created on 31 dec. 2020

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
from shapely.ops import polygonize, unary_union
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STPolygonize(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf
        
    def run(self):
        contours = []
        for geom in self.inputGdf.geometry:
            contours += GeomLib.toListOfLineStrings(geom)

        # Contour union
        contourUnion = unary_union(contours)
        # Contour network polygonization
        patches = polygonize(contourUnion)

        rows = [{'gid': i, 'geometry': patch} for i, patch in enumerate(patches)]
        return GeoDataFrame(rows, crs=self.inputGdf.crs)

