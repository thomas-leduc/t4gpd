'''
Created on 26 oct. 2022

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
from datetime import timedelta


class DataFrameLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def interpolate(df, xfieldname, yfieldname, x):
        assert (df[xfieldname].is_monotonic_increasing or 
                df[xfieldname].is_monotonic_decreasing), \
                f'Column "{xfieldname}" must be monotonic'

        df.set_index(xfieldname, drop=False, inplace=True)

        row0 = df.iloc[ df.index.get_indexer([x], method='ffill') ]
        row1 = df.iloc[ df.index.get_indexer([x], method='bfill') ]

        x0, x1 = row0[xfieldname].squeeze(), row1[xfieldname].squeeze()
        y0, y1 = row0[yfieldname].squeeze(), row1[yfieldname].squeeze()
        delta, deltaX = x - x0, x1 - x0

        if isinstance(deltaX, timedelta):
            delta = delta.seconds
            deltaX = deltaX.seconds

        if (0 == deltaX):
            return y0
        return y0 + (delta * (y1 - y0)) / deltaX
