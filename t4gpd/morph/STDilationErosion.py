'''
Created on 19 juin 2020

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
from shapely.ops import unary_union

from geopandas.geodataframe import GeoDataFrame

from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STDilationErosion(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, buffDist):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')

        self.inputGdf = inputGdf
        self.buffDist = buffDist

    def run(self):
        sbuildings = list()
        for _, row in self.inputGdf.iterrows():
            envelop = GeomLib.removeHoles(row.geometry)
            if envelop is not None:
                sbuildings.append(envelop)
        unionOfSBuilding = unary_union(sbuildings)
        fullRegion = unionOfSBuilding.convex_hull

        ##### SQUARES IDENTIFICATION ####################
        uoSquares = fullRegion.difference(
            unionOfSBuilding.buffer(self.buffDist, -1)).buffer(self.buffDist, -1)
        
        rowsOfSquares = list()
        if GeomLib.isMultipart(uoSquares):
            for fid, g in enumerate(uoSquares.geoms):
                if GeomLib.isPolygonal(g):
                    rowsOfSquares.append({ 'FID': fid, 'geometry': g })
        else:
            rowsOfSquares.append({ 'FID': 0, 'geometry': uoSquares })
        squaresGdf = GeoDataFrame(rowsOfSquares, crs=self.inputGdf.crs)

        ##### STREETS IDENTIFICATION ####################
        uoStreets = fullRegion.difference(unionOfSBuilding).difference(uoSquares)

        rowsOfStreets = list()
        if (uoStreets is not None) and GeomLib.isMultipart(uoStreets):
            for fid, g in enumerate(uoStreets.geoms):
                if GeomLib.isPolygonal(g):
                    rowsOfStreets.append({ 'FID': fid, 'geometry': g })
        elif (uoStreets is not None):
            rowsOfStreets.append({ 'FID': 0, 'geometry': g })
        streetsGdf = GeoDataFrame(rowsOfStreets, crs=self.inputGdf.crs)

        return [ squaresGdf, streetsGdf ]
