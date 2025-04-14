"""
Created on 6 mar. 2025

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

from geopandas import GeoDataFrame, overlay
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STProjectOnEdges(GeoProcess):
    """
    classdocs
    """

    def __init__(
        self, points, point_id, polygons, polygon_id, distToEdge=0, exteriorOnly=False
    ):
        """
        Constructor
        """
        if not isinstance(points, GeoDataFrame):
            raise IllegalArgumentTypeException(points, "GeoDataFrame")
        if not isinstance(polygons, GeoDataFrame):
            raise IllegalArgumentTypeException(polygons, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(points, polygons):
            raise Exception(
                "Illegal argument: points and polygons are expected to share the same crs!"
            )
        if not DataFrameLib.isAPrimaryKey(points, point_id):
            raise IllegalArgumentTypeException(point_id, "primary key for points")
        if not DataFrameLib.isAPrimaryKey(polygons, polygon_id):
            raise IllegalArgumentTypeException(polygon_id, "primary key for polygons")

        self.points_orig = points
        self.points = points.loc[:, [point_id, "geometry"]]
        self.point_id = point_id

        self.polygons = polygons.loc[:, [polygon_id, "geometry"]]
        self.polygon_id = polygon_id

        self.distToEdge = distToEdge
        self.exteriorOnly = exteriorOnly

    def __projectOnEdges(self):
        _within = overlay(self.points, self.polygons, how="intersection")
        _combine = _within.merge(self.polygons, on=self.polygon_id)
        _combine["geometry"] = _combine.apply(
            lambda row: GeomLib.projectOnEdges(
                row["geometry_x"],
                row["geometry_y"],
                distToEdge=self.distToEdge,
                exteriorOnly=self.exteriorOnly,
            ),
            axis=1,
        )
        _combine["dist_to_orig_point"] = _combine.apply(
            lambda row: row["geometry_x"].distance(row["geometry"]),
            axis=1,
        )
        _combine = _combine.set_index(self.point_id)[["dist_to_orig_point", "geometry"]]

        return _combine

    def run(self):
        prjPts = self.__projectOnEdges()
        result = self.points_orig.set_index(self.point_id)
        result["dist_to_orig_point"] = 0.0
        result.update(prjPts)
        result.reset_index(inplace=True)

        return result
