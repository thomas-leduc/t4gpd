'''
Created on 15 oct. 2024

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
from numpy import ndarray
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class IntervalLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def merge(intervals):
        if not isinstance(intervals, (list, ndarray, tuple)):
            raise IllegalArgumentTypeException(
                intervals, "list, numpy ndarray, or tuple of intervals")
        # Sort by start time
        _intervals = sorted(intervals, key=lambda x: x[0])

        result = []
        for interval in _intervals:
            if not result or result[-1][1] < interval[0]:  # No overlap
                result.append(interval)
            else:  # Overlap, merge intervals
                result[-1][1] = max(result[-1][1], interval[1])

        return result
