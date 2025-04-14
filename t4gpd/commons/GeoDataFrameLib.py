"""
Created on 13 mai 2022

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
from pandas import read_csv
from shapely import LineString
from shapely.wkt import loads


class GeoDataFrameLib(object):
    """
    classdocs
    """

    @staticmethod
    def getBBoxDiagonal(gdf):
        xmin, ymin, xmax, ymax = gdf.total_bounds
        return LineString([(xmin, ymin), (xmax, ymax)])

    @staticmethod
    def isAGeoDataFrameOfBipoints(gdf):
        return (
            isinstance(gdf, GeoDataFrame)
            and all(gdf.geometry.apply(lambda g: isinstance(g, LineString)))
            and all(gdf.geometry.apply(lambda g: 2 == len(g.coords)))
        )

    @staticmethod
    def read_csv(inputFile, decimal=".", sep=";", crs="epsg:2154", index_col=None):
        df = read_csv(inputFile, decimal=decimal, index_col=index_col, sep=sep)
        df.geometry = df.geometry.apply(lambda g: loads(g))
        return GeoDataFrame(df, crs=crs)

    @staticmethod
    def shareTheSameCrs(*gdfs):
        return (
            (0 == len(gdfs))
            or all(
                [
                    (isinstance(gdf, GeoDataFrame) and (gdfs[0].crs == gdf.crs))
                    for gdf in gdfs
                ]
            )
            or all(
                [(isinstance(gdf, GeoDataFrame) and (gdf.crs is None)) for gdf in gdfs]
            )
        )
