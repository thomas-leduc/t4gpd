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
from t4gpd.commons.morph.CircularityLib import CircularityLib
from t4gpd.commons.morph.ConvexityLib import ConvexityLib
from t4gpd.commons.morph.LinearRegressionLib import LinearRegressionLib
from t4gpd.commons.morph.RectangularityLib import RectangularityLib
from t4gpd.commons.morph.StarShapedLib import StarShapedLib
from t4gpd.morph.geoProcesses.OrientedSVF import OrientedSVF
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess


class IsovistIndices(object):
    """
    classdocs
    """

    @staticmethod
    def indices(isovRaysField, isovField, prefix=None, merge_by_index=False):
        if not isinstance(isovRaysField, GeoDataFrame):
            raise IllegalArgumentTypeException(isovRaysField, "GeoDataFrame")
        if not isinstance(isovField, GeoDataFrame):
            raise IllegalArgumentTypeException(isovField, "GeoDataFrame")
        if DataFrameLib.hasAMultiIndex(isovRaysField):
            raise IllegalArgumentTypeException(
                isovRaysField, "GeoDataFrame without MultiIndex"
            )
        if DataFrameLib.hasAMultiIndex(isovField):
            raise IllegalArgumentTypeException(
                isovField, "GeoDataFrame without MultiIndex"
            )

        df1 = StarShapedLib.indices(
            isovRaysField, with_geom=False, prefix=prefix, merge_by_index=False
        )

        df2 = CircularityLib.indices(
            isovField[["geometry"]], with_geom=False, prefix=prefix, merge_by_index=True
        )
        df2 = ConvexityLib.indices(
            df2, with_geom=False, prefix=prefix, merge_by_index=True
        )
        df2 = LinearRegressionLib.indices(
            df2, with_geom=False, prefix=prefix, merge_by_index=True
        )
        df2 = RectangularityLib.indices(
            df2, with_geom=False, prefix=prefix, merge_by_index=True
        )
        df2.drop(columns=["geometry"], inplace=True)

        df12 = concat([df1, df2], axis=1)

        if merge_by_index:
            df12 = concat([isovField, df12], axis=1)
            df12["geometry"] = df12.viewpoint
            df12.drop(columns=["viewpoint"], inplace=True)
            df12.set_geometry("geometry", inplace=True)
        return df12


"""
import matplotlib.pyplot as plt
from shapely import get_parts
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STGrid import STGrid
from t4gpd.isovist.STIsovistField2D import STIsovistField2D

buildings = GeoDataFrameDemos.ensaNantesBuildings()
sensors = STGrid(buildings, dx=80, indoor=False, intoPoint=True).run()
sensors.set_index("gid", drop=False, inplace=True)

isovRaysField, isovField = STIsovistField2D(
    buildings, sensors, nRays=32, rayLength=50, withIndices=False
).run()

df = IsovistIndices.indices(isovRaysField, isovField, prefix=None, merge_by_index=True)
dfbis = IsovistIndices.indices(
    isovRaysField, isovField, prefix=None, merge_by_index=False
)
"""
