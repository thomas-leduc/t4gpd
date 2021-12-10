'''
Created on 19 juil. 2021

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
from glob import glob
from os import chdir, getcwd, makedirs
from os.path import basename, dirname
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from geopandas import GeoDataFrame
from pandas import DataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class ZipWriter(GeoProcess):
    '''
    classdocs
    '''
    DRIVER_EXT = {
        'ESRI Shapefile': 'shp',
        'GPKG': 'gpkg',
        'GeoJSON': 'geojson'
        }

    def __init__(self, mapOfDf, zipOutputFile, driver='ESRI Shapefile'):
        '''
        Constructor
        '''
        if not isinstance(mapOfDf, dict):
            raise IllegalArgumentTypeException(mapOfDf, '{ "layername": DataFrame, ... }')
        for layername, df in mapOfDf.items():
            if not isinstance(layername, str):
                raise IllegalArgumentTypeException(mapOfDf, '{ "layername": DataFrame, ... }')
            if not isinstance(df, DataFrame):
                raise IllegalArgumentTypeException(mapOfDf, '{ "layername": DataFrame, ... }')
        self.mapOfDf = mapOfDf

        self.zipOutputBasename = basename(zipOutputFile)
        self.zipOutputDirname = dirname(zipOutputFile)
        if (0 == len(self.zipOutputDirname)):
            self.zipOutputDirname = '.'

        if driver not in ('ESRI Shapefile', 'GPKG', 'GeoJSON'):
            raise IllegalArgumentTypeException(driver, '{"ESRI Shapefile", "GPKG", "GeoJSON"}')
        self.driver = driver

    def __zip(self, rootdir):
        with ZipFile(f'{self.zipOutputDirname}/{self.zipOutputBasename}.zip', 'w') as myzip:
            cwd = getcwd()
            chdir(rootdir)
            # writing each file one by one
            _ifiles = glob(f'{self.zipOutputBasename}/*.*', recursive=False)
            for _ifile in _ifiles:
                myzip.write(_ifile)
                # print(f'*** {_ifile}')  # DEBUG
            chdir(cwd)

    def run(self):
        extension = self.DRIVER_EXT[self.driver]
        with TemporaryDirectory() as tmpdir:
            makedirs(f'{tmpdir}/{self.zipOutputBasename}', exist_ok=True)
            for _layername, _df in self.mapOfDf.items():
                if not isinstance(_df, GeoDataFrame):
                    _df['geometry'] = None
                    _df = GeoDataFrame(_df)
                _ofile = f'{tmpdir}/{self.zipOutputBasename}/{_layername}.{extension}'
                if not _df.empty:
                    _df.to_file(_ofile, driver=self.driver, encoding='utf-8')
                # print(f'=== {_ofile}')  # DEBUG

            self.__zip(tmpdir)

        print(f'{self.zipOutputDirname}/{self.zipOutputBasename}.zip has been written!')
        return None
