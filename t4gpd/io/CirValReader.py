'''
Created on 25 juil. 2022

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
from t4gpd.io.AbstractReader import AbstractReader
from t4gpd.io.CirReader import CirReader
from t4gpd.io.ValReader import ValReader


class CirValReader(AbstractReader):
    '''
    classdocs
    '''

    def __init__(self, cirFilename, *valFilenames):
        '''
        Constructor
        '''
        self.cirFilename = cirFilename
        self.valFilenames = valFilenames

    def run(self):
        gdf = CirReader(self.cirFilename).run()
        for filename in self.valFilenames:
            df = ValReader(filename).run()
            gdf = gdf.merge(df, how='left', on='cir_id')
        return gdf
