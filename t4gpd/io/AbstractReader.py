'''
Created on 22 juin 2022

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
from io import StringIO

from t4gpd.commons.GeoProcess import GeoProcess


class AbstractReader(GeoProcess):
    '''
    classdocs
    '''

    @staticmethod
    def opener(inputFile):
        if isinstance(inputFile, StringIO):
            # There is no way to re-open a StringIO object, so let's duplicate it
            return StringIO(inputFile.getvalue())
        else:
            return open(inputFile, 'r')
