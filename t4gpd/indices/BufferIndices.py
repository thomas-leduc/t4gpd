"""
Created on 11 mar. 2025

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
from pandas import concat
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STHeightOfRoughness import STHeightOfRoughness
from t4gpd.morph.STSurfaceFraction import STSurfaceFraction


class BufferIndices(object):
    """
    classdocs
    """

    @staticmethod
    def indices(sensors, buildings, buffDist=None, merge_by_index=False):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, "GeoDataFrame")
        if DataFrameLib.hasAMultiIndex(sensors):
            raise IllegalArgumentTypeException(
                sensors, "GeoDataFrame without MultiIndex"
            )

        df = sensors.loc[:, ["geometry"]]
        if not buffDist is None:
            df.geometry = df.geometry.buffer(buffDist)

        df = STSurfaceFraction(buildings, df, "bsf").run()
        df = STHeightOfRoughness(buildings, df, "HAUTEUR", "hre").run()
        df.drop(columns=["geometry"], inplace=True)

        if merge_by_index:
            df = concat([sensors, df], axis=1)
        return df


"""
import matplotlib.pyplot as plt
from shapely import get_parts
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.isovist.STIsovistField2D import STIsovistField2D

buildings = GeoDataFrameDemos.ensaNantesBuildings()
sensors1 = STGrid(buildings, dx=80, indoor=False, intoPoint=True).run()
sensors1.set_index("gid", drop=False, inplace=True)
sensors2 = BufferIndices.indices(sensors1, buildings, buffDist=50, merge_by_index=True)

sensors3 = STGrid(buildings, dx=80, indoor=False, intoPoint=False).run()
sensors3.set_index("gid", drop=False, inplace=True)
sensors4 = BufferIndices.indices(sensors3, buildings, buffDist=None, merge_by_index=True)
"""
