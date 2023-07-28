'''
Created on 24 avr. 2023

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
from os.path import basename, splitext


class WarnUtils(object):
    '''
    classdocs
    '''

    @staticmethod
    def format_Warning(message, category, filename, lineno, line=""):
        '''
        import warnings
        warnings.formatwarning = WarnUtils.format_Warning
        warnings.warn(msg)
        '''
        # return f"{basename(filename)}:{lineno}: {category.__name__}: {message}\n"
        return f"{filename}:{lineno}: {category.__name__}: {message}\n"

    @staticmethod
    def format_Warning_alt(message, category, filename, lineno, line=""):
        '''
        import warnings
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn(msg)
        '''
        filename = basename(splitext(filename)[0])
        return f"{filename}: {message}\n"
