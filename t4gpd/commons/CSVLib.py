'''
Created on 6 juil. 2020

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
import re


class CSVLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def readLexeme(s, decimalSep='.'):
        if ('.' != decimalSep):
            s = s.replace(decimalSep, '.')
        try:
            nb = float(s)
            if nb.is_integer():
                return int(nb)
            return nb
        except ValueError:
            pass
        try:
            import unicodedata
            nb = unicodedata.numeric(s)
            if nb.is_integer():
                return int(nb)
            return nb
        except (TypeError, ValueError):
            pass
        return s
