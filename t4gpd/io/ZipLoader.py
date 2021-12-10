'''
Created on 8 nov. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from geopandas import read_file
from os import access, R_OK
from os.path import isfile
from pathlib import Path
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from zipfile import is_zipfile, ZipFile


class ZipLoader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, zipInputFile, layernames=None, bbox=None, mask=None):
        '''
        Constructor
        '''
        self.zipInputFile = zipInputFile
        if not (isfile(self.zipInputFile) and access(self.zipInputFile, R_OK)):
            raise IllegalArgumentTypeException(zipInputFile, 'readable filename')
        if not is_zipfile(self.zipInputFile):
            raise IllegalArgumentTypeException(zipInputFile, 'Zip filename')

        self.layernames = layernames
        self.bbox = bbox
        self.mask = mask

    def __getTypeOfDataFrame(self, extension):
        if extension in ['.geojson', '.gpkg', '.shp']:
            return 'GeoDataFrame'
        return None

    def run(self):
        if self.layernames is None:
            layers = []
        else:
            layers = { _layername: None for _layername in self.layernames}

        with ZipFile(self.zipInputFile, 'r') as _archive:
            for _filename in _archive.namelist():
                _extension = Path(_filename).suffix.lower()
                _basename = Path(_filename).stem
                _tod = self.__getTypeOfDataFrame(_extension)

                if _tod is not None:
                    if self.layernames is None:
                        layers.append(_basename)

                    elif _basename in self.layernames:
                        _gdf = read_file(f'{self.zipInputFile}!{_filename}',
                                         bbox=self.bbox, mask=self.mask)
                        layers[_basename] = _gdf

        if self.layernames is None:
            if (0 < len(layers)):
                print(f'List of GeoDataFrame(s): {layers}')
            return None

        return [layers[_layername] for _layername in self.layernames]
