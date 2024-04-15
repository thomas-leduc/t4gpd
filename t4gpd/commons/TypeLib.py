'''
Created on 22 feb. 2024

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
from numpy import dtype, floating, integer, issubdtype
from pandas import Series


class TypeLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def are_both_floating_or_integer(data_type1, data_type2):
        return (
            (TypeLib.is_floating(data_type1) and TypeLib.is_floating(data_type2)) or
            (TypeLib.is_integer(data_type1) and TypeLib.is_integer(data_type2))
        )

    @staticmethod
    def is_floating(data_type):
        if not isinstance(data_type, (dtype, Series, type)):
            data_type = type(data_type)
        return issubdtype(data_type, floating)

    @staticmethod
    def is_integer(data_type):
        if not isinstance(data_type, (dtype, Series, type)):
            data_type = type(data_type)
        return issubdtype(data_type, integer)
