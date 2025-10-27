"""
Created on 26 oct. 2022

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

from datetime import timedelta
from hashlib import md5
from pandas import DataFrame, MultiIndex, Series, concat
from random import choices


class DataFrameLib(object):
    """
    classdocs
    """

    @staticmethod
    def equals(df1, df2):
        def row_hash(row):
            return md5(str(row.values).encode()).hexdigest()

        if not df1.equals(df2):
            set1 = set(df1.apply(row_hash, axis=1))
            set2 = set(df2.apply(row_hash, axis=1))
            return set1 == set2
        return True

    @staticmethod
    def fillWithMissingRows(df1, df2, on):
        # Return df1 completed with the missing lines from df2
        # according to the "on" columns.
        if not isinstance(on, (list, tuple)):
            on = [on]

        """
        # Identifies the lines in df2 that are absent from df1.
        missing = df2.merge(df1, on=on, how="left", indicator=True)
        missing = missing.loc[missing["_merge"] == "left_only", df2.columns]
        """
        # Creates a multi-key index (tuple per row)
        keys1 = set(zip(*(df1[col] for col in on)))
        mask = ~Series(list(zip(*(df2[col] for col in on)))).isin(keys1)

        # Select only lines not present in df1
        missing = df2.loc[mask]

        # Concatenate without duplicates
        return concat([df1, missing], ignore_index=True)

    @staticmethod
    def getNewColumnName(df):
        assert isinstance(df, DataFrame), "df must be a DataFrame"

        abet = "abcdefghijklmnopqrstuvwxyz"
        while True:
            colname = "".join(choices(abet, k=10))
            if colname not in df:
                return colname

    @staticmethod
    def hasAMultiIndex(df):
        return isinstance(df.index, MultiIndex)

    @staticmethod
    def hasAPrimaryKeyIndex(gdf):
        return gdf.index.is_unique

    @staticmethod
    def interpolate(df, xfieldname, yfieldname, x):
        assert (
            df[xfieldname].is_monotonic_increasing
            or df[xfieldname].is_monotonic_decreasing
        ), f'Column "{xfieldname}" must be monotonic'

        df.set_index(xfieldname, drop=False, inplace=True)

        row0 = df.iloc[df.index.get_indexer([x], method="ffill")]
        row1 = df.iloc[df.index.get_indexer([x], method="bfill")]

        x0, x1 = row0[xfieldname].squeeze(), row1[xfieldname].squeeze()
        y0, y1 = row0[yfieldname].squeeze(), row1[yfieldname].squeeze()
        delta, deltaX = x - x0, x1 - x0

        if isinstance(deltaX, timedelta):
            delta = delta.seconds
            deltaX = deltaX.seconds

        if 0 == deltaX:
            return y0
        return y0 + (delta * (y1 - y0)) / deltaX

    @staticmethod
    def isAPrimaryKey(gdf, key):
        return key in gdf.columns and gdf[key].is_unique
