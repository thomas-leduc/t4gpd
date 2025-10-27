"""
Created on 19 juin 2025

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

from numpy import asarray, floating, issubdtype, ndarray


class ArrayLib(object):
    """
    classdocs
    """

    @staticmethod
    def cast_compact_dtype(arr):
        """
        Casts the input array to the smallest possible dtype that can hold its values.
        :param arr: Input array (list, tuple, or numpy ndarray)
        :return: Numpy ndarray with the smallest dtype
        """
        compact_dtype = ArrayLib.get_compact_dtype(arr)
        return asarray(arr, dtype=compact_dtype)

    @staticmethod
    def get_compact_dtype(arr):
        """
        Returns the smallest numpy dtype that can hold the values in the input array.
        :param arr: Input array (list, tuple, or numpy ndarray)
        :return: Numpy dtype (e.g., float16, float32, int8, int16, uint8, etc.)
        :raises TypeError: If the input is not a list, tuple, or numpy ndarray
        """

        def __find_min_float_dtype(arr):
            import warnings
            from numpy import float16, float32, float64, allclose

            warnings.filterwarnings("ignore", message="overflow encountered in cast")
            for dtype in [float16, float32, float64]:
                arr_casted = arr.astype(dtype)
                if allclose(arr, arr_casted, rtol=1e-05, atol=1e-08, equal_nan=True):
                    return dtype
            return float64  # par défaut si aucun plus petit type ne suffit

        def __find_min_int_dtype(arr):
            from numpy import iinfo
            from numpy import int8, int16, int32, int64, uint8, uint16, uint32, uint64

            dtypes = [uint8, int8, uint16, int16, uint32, int32, uint64, int64]
            vmin, vmax = arr.min(), arr.max()

            for dtype in dtypes:
                info = iinfo(dtype)
                if vmin >= info.min and vmax <= info.max:
                    return dtype
            return int64  # par défaut si aucun plus petit type ne suffit

        if isinstance(arr, (list, tuple)):
            arr = asarray(arr)
        if isinstance(arr, ndarray):
            if issubdtype(arr.dtype, floating):
                return __find_min_float_dtype(arr)
            elif issubdtype(arr.dtype, int):
                return __find_min_int_dtype(arr)
            elif issubdtype(arr.dtype, bool):
                return bool
        raise TypeError(
            "ArrayLib.get_compact_dtype() requires a list, tuple, or numpy ndarray of int, float, or bool values"
        )
