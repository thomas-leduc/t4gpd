'''
Created on 12 sept. 2020

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
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.ArrayCoding import ArrayCoding


class STMultipleOverlaps(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, by=None):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf
        if (by is not None) and (by not in inputGdf):
            raise Exception('%s is not a relevant field name!' % (by))
        self.by = by

    def run(self):
        geoms = []
        for geom in self.inputGdf.geometry:
            geoms += [g.buffer(0.001) for g in GeomLib.flattenGeometry(geom) if 1.0 < g.area]

        contours = []
        for geom in geoms:
            contours += GeomLib.toListOfLineStrings(geom)
        # Contour union
        contourUnion = unary_union(contours)
        # Contour network polygonization
        patches = polygonize(contourUnion)

        rows = []

        if self.by is None:
            for patch in patches:
                hits = filter(patch.representative_point().within, self.inputGdf.geometry)
                nHits = len(list(hits))
                if (0 < nHits):
                    rows.append({'geometry': patch, 'nOverlap': nHits})
        else:
            for patch in patches:
                hits = []
                for _, row in self.inputGdf.iterrows():
                    if patch.representative_point().within(row.geometry):
                        hits.append(row[self.by])
                if (0 < len(hits)):
                    rows.append({'geometry': patch, 'nOverlap': len(hits),
                                 'matched_id': ArrayCoding.encode(hits)})

        return GeoDataFrame(rows, crs=self.inputGdf.crs)
