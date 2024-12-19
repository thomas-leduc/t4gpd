'''
Created on 16 juin 2020

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from numpy import nan
from pandas import isna


class ArrayCoding(object):
    '''
    classdocs
    '''

    @staticmethod
    def encode(listOfValues, separator="#"):
        try:
            iter(listOfValues)
            return separator.join([str(v) for v in listOfValues])
        except TypeError:
            if isna(listOfValues) or (listOfValues is None):
                return nan
            return str(listOfValues)

    @staticmethod
    def decode(argument, outputType=float, separator="#"):
        if isna(argument) or (argument is None):
            return nan
        if (0 == len(argument)):
            return []
        return [outputType(v) for v in argument.split(separator)]
