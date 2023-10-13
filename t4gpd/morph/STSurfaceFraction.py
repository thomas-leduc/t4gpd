'''
Created on 6 sep. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from geopandas import GeoDataFrame, overlay
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STSurfaceFraction(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, masks, grid, outputFieldName="bsf"):
        '''
        Constructor
        '''
        if not isinstance(masks, GeoDataFrame):
            raise IllegalArgumentTypeException(
                masks, "GeoDataFrame")
        if not isinstance(grid, GeoDataFrame):
            raise IllegalArgumentTypeException(
                grid, "GeoDataFrame")
        if outputFieldName in grid:
            raise Exception(
                f"Illegal argument: {outputFieldName} is an existing column of the grid!")

        if not GeoDataFrameLib.shareTheSameCrs(masks, grid):
            raise Exception(
                "Illegal argument: masks and grid must share shames CRS!")

        self.masks = masks
        # CLEAN GEOMETRIES
        self.masks.geometry = self.masks.geometry.apply(
            lambda g: g.buffer(0))
        self.grid = grid
        self.outputFieldName = outputFieldName

    @staticmethod
    def __overlay(masks, grid, outputFieldName):
        grid["__CELL_AREA__"] = grid.geometry.apply(lambda g: g.area)
        grid["__CELL_ID__"] = range(len(grid))
        masks2 = overlay(masks, grid, how="intersection", keep_geom_type=True)
        masks2 = masks2.dissolve(by="__CELL_ID__", as_index=False)
        masks2[outputFieldName] = masks2.apply(
            lambda row: row.geometry.area/row.__CELL_AREA__, axis=1)
        grid2 = grid.merge(
            masks2[["__CELL_ID__", outputFieldName]], on="__CELL_ID__")
        grid.drop(columns=["__CELL_AREA__", "__CELL_ID__"], inplace=True)
        grid2.drop(columns=["__CELL_AREA__", "__CELL_ID__"], inplace=True)
        return grid2

    def run(self):
        return STSurfaceFraction.__overlay(self.masks, self.grid, self.outputFieldName)
