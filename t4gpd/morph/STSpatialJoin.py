'''
Created on 20 juin 2020

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
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STSpatialJoin(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdfLeft, spatialRelationship, inputGdfRight):
        '''
        Constructor
        '''
        if not isinstance(inputGdfLeft, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdfLeft, 'GeoDataFrame')
        if not isinstance(inputGdfRight, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdfRight, 'GeoDataFrame')
        if not (inputGdfLeft.crs == inputGdfRight.crs):
            raise Exception('Illegal argument: both GeoDataFrame must share shames CRS!')

        self.inputGdfLeft = inputGdfLeft
        self.inputGdfRight = inputGdfRight

        if ('contains' == spatialRelationship):
            self.query = lambda geoms: geoms[0].contains(geoms[1])
        elif ('crosses' == spatialRelationship):
            self.query = lambda geoms: geoms[0].crosses(geoms[1])
        elif 'intersects' == spatialRelationship:
            self.query = lambda geoms: geoms[0].intersects(geoms[1])
        elif 'overlaps' == spatialRelationship:
            self.query = lambda geoms: geoms[0].overlaps(geoms[1])
        elif 'touches' == spatialRelationship:
            self.query = lambda geoms: geoms[0].touches(geoms[1])
        elif ('within' == spatialRelationship):
            self.query = lambda geoms: geoms[0].within(geoms[1])
        elif ('contains_centroid' == spatialRelationship):
            self.query = lambda geoms: geoms[0].contains(geoms[1].centroid)
        else:
            raise Exception('Unknown spatial relationship! It has to be chosen among: \
            "contains", "crosses", "intersects", "overlaps", \
            "touches", "within", and "contains_centroid".')

    def run(self):
        spatialIdx = self.inputGdfRight.sindex

        rows = []
        for _, rowLeft in self.inputGdfLeft.iterrows():
            geomLeft = rowLeft.geometry
            bbLeft = geomLeft.bounds

            idsRight = spatialIdx.intersection(bbLeft)
            for idRight in idsRight:
                rowRight = self.inputGdfRight.loc[idRight]
                geomRight = rowRight.geometry
                if self.query([geomLeft, geomRight]):
                    rows.append(self.appendNewItems(rowLeft, rowRight))

        return GeoDataFrame(rows, crs=self.inputGdfLeft.crs)
