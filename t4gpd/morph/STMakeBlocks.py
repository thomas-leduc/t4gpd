'''
Created on 12 feb. 2021

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
from pandas import concat
from t4gpd.commons.ConcaveLib import ConcaveLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STPolygonize import STPolygonize


class STMakeBlocks(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, roads, roi=None):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, "GeoDataFrame")
        self.buildings = buildings

        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, "GeoDataFrame")
        if not ((roi is None) or isinstance(roi, GeoDataFrame)):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame or None")
        self.linestrings = STMakeBlocks.__prepare_linestrings(roads, roi)

    @staticmethod
    def __prepare_linestrings(roads, roi):
        if roi is None:
            return roads
        roi.geometry = roi.geometry.boundary
        return GeoDataFrame(concat([roads[["geometry"]], roi[["geometry"]]]), crs=roads.crs)

    def __mkBlocks(self):
        # POLYGONIZE LINESTRINGS
        polygons = STPolygonize(self.linestrings).run()

        # GROUP BUILDINGS PER URBAN BLOCKS
        buildings = overlay(
            self.buildings[["geometry"]], polygons, how="intersection")
        blocks = buildings.dissolve(by="gid", as_index=False)

        # GROUP LINESTRINGS PER URBAN BLOCKS
        linestrings = overlay(
            self.linestrings, polygons, how="intersection", keep_geom_type=True)
        linestrings = linestrings.dissolve(by="gid", as_index=False)

        # TRY TO REMOVE CONCAVITIES IN EACH BLOCK
        blocks.geometry = blocks.apply(
            lambda row: ConcaveLib.fillInTheConcavities(
                row.geometry, linestrings.at[row.gid, "geometry"]), axis=1)

        return blocks

    def run(self):
        return self.__mkBlocks()
