'''
Created on 18 juin 2020

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

import geopandas as gpd
from t4gpd.commons.BoundingBox import BoundingBox
from t4gpd.commons.GeoProcess import GeoProcess


class STLoadAndClip(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, filename, roi):
        '''
        Constructor
        '''
        self.inputGdf = gpd.read_file(filename)
        self.spatialIdx = self.inputGdf.sindex
        self.roi = BoundingBox(roi).asPolygon()

    def run(self):
        rows = []

        ids = list(self.spatialIdx.intersection(self.roi.bounds))
        for _id in ids:
            row = self.inputGdf.loc[_id]
            rowGeom = row.geometry
            if self.roi.intersects(rowGeom):
                _row = { 'geometry':rowGeom.intersection(self.roi) }
                rows.append(self.updateOrAppend(row, _row))
        return GeoDataFrame(rows, crs=self.inputGdf.crs)
