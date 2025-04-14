"""
Created on 10 mar. 2025

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

from geopandas import GeoDataFrame
from pandas import DataFrame, concat
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class AbstractIndicesLib(object):
    """
    classdocs
    """

    @classmethod
    def indices(cls, gdf, with_geom=False, prefix=None, merge_by_index=False):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        df = DataFrame(
            gdf.apply(
                lambda row: cls._indices(row, with_geom=with_geom), axis=1
            ).tolist(),
            index=gdf.index,
        )

        if not prefix is None:
            df.rename(
                columns={col: f"{prefix}_{col}" for col in df.columns}, inplace=True
            )

        if merge_by_index:
            df = concat([gdf, df], axis=1)

        return df

    def indices2(self, merge_by_index=False):
        # if not isinstance(self.gdf, GeoDataFrame):
        #     raise IllegalArgumentTypeException(self.gdf, "GeoDataFrame")

        df = DataFrame(
            self.gdf.apply(lambda row: self._indices(row), axis=1).tolist(),
            index=self.gdf.index,
        )

        if merge_by_index:
            df = concat([self.gdf, df], axis=1)

        return df

    @classmethod
    def getColumns(cls, with_geom=False):
        columns = cls._getColumns()
        if with_geom:
            columns.append("geometry")
        return columns

    @staticmethod
    def _getColumns(geom, with_geom=False):
        raise NotImplementedError("_getColumns(...) must be overridden!")

    @staticmethod
    def _indices(geom, with_geom=False):
        raise NotImplementedError("_indices(...) must be overridden!")
