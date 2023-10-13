'''
Created on 22 aug. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
import rasterio
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class RTLoad(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        if not isinstance(filename, str):
            raise IllegalArgumentTypeException(
                filename, "input filename (str)")
        self.filename = filename

    def run(self):
        return rasterio.open(self.filename)


"""
r = RTLoad("/home/tleduc/data/mnt_asc/mnt_nantes_2005_1m/MNT_L93_0354_6690.asc").run()
print(type(r))
"""
