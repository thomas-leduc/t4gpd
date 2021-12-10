'''
Created on 12 juil. 2021

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
from tempfile import TemporaryDirectory

from geopandas import read_file
from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class Reloading(object):
    '''
    classdocs
    '''

    def __init__(self, gdf):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, 'GeoDataFrame')
        self.gdf = gdf

    def run(self):
        with TemporaryDirectory() as tmpdir:
            ofile = f'{tmpdir}/temporary.gpkg'
            self.gdf.to_file(ofile, driver='GPKG')
            return read_file(ofile)
        raise Exception('Unreachable instruction!')
