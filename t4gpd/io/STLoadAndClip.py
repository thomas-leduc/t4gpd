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
from geopandas import clip, read_file
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
        self.inputGdf = read_file(filename, bbox=roi)
        self.roi = BoundingBox(roi).asPolygon()

    def run(self):
        return clip(self.inputGdf, self.roi)
