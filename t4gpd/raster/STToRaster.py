'''
Created on 31 mai 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
import cv2
from geopandas import GeoDataFrame, overlay
from numpy import zeros
from shapely.geometry import box
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STToRaster(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, nrows, ncols, bbox=None, threshold=0.5, outputFile=None):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, 'GeoDataFrame')
        self.gdf = gdf

        self.nrows, self.ncols = nrows, ncols
        self.minx, self.miny, maxx, self.maxy = gdf.total_bounds if bbox is None else bbox
        self.dx = (maxx - self.minx) / ncols
        self.dy = (self.maxy - self.miny) / nrows
        self.threshold = threshold
        self.outputFile = outputFile

    def __grid(self):
        result = []
        x0 = self.minx
        for c in range(self.ncols):
            x0pp, y0 = x0 + self.dx, self.maxy
            for r in range(self.nrows):
                y0pp = y0 - self.dy
                result.append({
                    'gid': r * self.ncols + c,
                    'row': r,
                    'col': c,
                    'geometry': box(x0, y0, x0pp, y0pp)
                })
                y0 = y0pp
            x0 = x0pp
        return GeoDataFrame(result, crs=self.gdf.crs)

    def __fromGridToArray(self, grid):
        img = zeros([self.nrows, self.ncols], dtype=int)
        for _, rowItem in grid.iterrows():
            if (self.threshold <= rowItem.cover):
                img[rowItem.row, rowItem.col] = 1
        return img

    def run(self):
        grid = self.__grid()

        grid = overlay(grid, self.gdf[['geometry']], how='intersection')
        grid = grid.dissolve(by='gid', as_index=False)
        cellArea = self.dx * self.dy
        grid['cover'] = grid.geometry.apply(lambda g: g.area / cellArea)

        img = self.__fromGridToArray(grid)

        if not self.outputFile is None:
            cv2.imwrite(self.outputFile, 255 * img)

        return img
