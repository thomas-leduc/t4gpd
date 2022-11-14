'''
Created on 11 oct. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from os import access, R_OK
from os.path import isfile

from fiona import listlayers
from geopandas import read_file
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class GpkgLoader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gpkgInputFile, layernames=None, bbox=None, mask=None):
        '''
        Constructor
        '''
        if not (isfile(gpkgInputFile) and access(gpkgInputFile, R_OK)):
            raise IllegalArgumentTypeException(gpkgInputFile, 'readable filename')
        self.gpkgInputFile = gpkgInputFile

        self.layernames = layernames
        self.bbox = bbox
        self.mask = mask

    def listlayers(self):
        return listlayers(self.gpkgInputFile)

    def run(self):
        layernames = listlayers(self.gpkgInputFile) if self.layernames is None else self.layernames

        result = {}
        for layername in layernames:
            df = read_file(self.gpkgInputFile, layer=layername, bbox=self.bbox, mask=self.mask)
            result[layername] = df
        return result
