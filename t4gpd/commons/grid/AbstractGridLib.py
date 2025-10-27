"""
Created on 9 avr. 2021

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
from geopandas import GeoDataFrame, overlay, sjoin_nearest
from shapely import MultiLineString
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class AbstractGridLib(object):
    """
    classdocs
    """

    __slots__ = ("gdf", "dx", "dy", "encode")

    def __init__(self, gdf, dx, dy=None, encode=True):
        """
        Constructor
        """
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        self.gdf = gdf
        self.dx = dx
        self.dy = dx if (dy is None) else dy
        self.encode = encode

    def distanceToNearestContour(self, grid):
        gdf = self.gdf.copy(deep=True)
        gdf.geometry = gdf.geometry.apply(
            lambda geom: MultiLineString(GeomLib.toListOfLineStrings(geom))
        )
        grid2 = sjoin_nearest(
            grid,
            gdf[["geometry"]],
            how="inner",
            distance_col="dist_to_ctr",
            max_distance=None,
        )
        if ("index_right" not in gdf) and ("index_right" in grid2):
            grid2.drop(columns="index_right", inplace=True)
        grid2.drop_duplicates(
            subset=["gid"], keep="first", ignore_index=True, inplace=True
        )
        return grid2

    def grid(self):
        raise NotImplementedError("grid() must be overridden!")

    def __overlayWithGrid(self, grid, how="difference"):
        _result = grid.loc[:, ["gid", "geometry"]]
        _result.geometry = _result.geometry.apply(lambda geom: geom.centroid)
        _result = overlay(_result, self.gdf, how)
        _result = set(_result.gid.to_list())
        return _result

    def indoorGrid(self):
        _grid = self.indoorOutdoorGrid()
        _grid = _grid.loc[_grid[_grid.indoor == 1].index]
        _grid.reset_index(drop=True, inplace=True)
        return _grid

    def indoorOutdoorGrid(self):
        _grid = self.grid()
        _gids = self.__overlayWithGrid(_grid, how="difference")
        _grid["indoor"] = _grid.gid.apply(lambda gid: 0 if (gid in _gids) else 1)
        return _grid

    def outdoorGrid(self):
        _grid = self.indoorOutdoorGrid()
        _grid = _grid.loc[_grid[_grid.indoor == 0].index]
        _grid.reset_index(drop=True, inplace=True)
        return _grid
