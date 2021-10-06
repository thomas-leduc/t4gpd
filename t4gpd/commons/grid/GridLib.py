'''
Created on 31 mars 2021

@author: tleduc

Copyright 2020 Thomas Leduc

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
from geopandas.geodataframe import GeoDataFrame
from numpy import ceil
from shapely.geometry import box
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.grid.AbstractGridLib import AbstractGridLib


class GridLib(AbstractGridLib):
    '''
    classdocs
    '''

    def __init__(self, gdf, dx, dy=None, encode=True):
        '''
        Constructor
        '''
        super().__init__(gdf, dx, dy, encode)

        self.minx, self.miny, maxx, maxy = gdf.total_bounds
        self.ncols = int(ceil((maxx - self.minx) / self.dx))
        self.nrows = int(ceil((maxy - self.miny) / self.dy))

        self.xOffset = ((self.ncols * self.dx) - (maxx - self.minx)) / 2.0
        self.yOffset = ((self.nrows * self.dy) - (maxy - self.miny)) / 2.0

    def __neighbors(self, r, c):
        e = r * self.ncols + (c + 1)
        ne = (r + 1) * self.ncols + (c + 1)
        n = (r + 1) * self.ncols + c
        nw = (r + 1) * self.ncols + (c - 1)
        w = r * self.ncols + (c - 1)
        sw = (r - 1) * self.ncols + (c - 1)
        s = (r - 1) * self.ncols + c
        se = (r - 1) * self.ncols + (c + 1)

        _na = -1
        if (0 == c):
            nw, w, sw = _na, _na, _na
        if (0 == r):
            sw, s, se = _na, _na, _na
        if (self.ncols == c + 1):
            ne, e, se = _na, _na, _na
        if (self.nrows == r + 1):
            nw, n, ne = _na, _na, _na
        return [e, n, w, s], [e, ne, n, nw, w, sw, s, se]

    def grid(self):
        result = []
        x0 = self.minx - self.xOffset
        for c in range(self.ncols):
            x0pp, y0 = x0 + self.dx, self.miny - self.yOffset
            for r in range(self.nrows):
                y0pp = y0 + self.dy
                neighbors4, neighbors8 = self.__neighbors(r, c)
                if self.encode:
                    neighbors4, neighbors8 = (ArrayCoding.encode(neighbors4),
                                              ArrayCoding.encode(neighbors8))
                result.append({
                    'gid': r * self.ncols + c,
                    'neighbors4': neighbors4,
                    'neighbors8': neighbors8,
                    'geometry': box(x0, y0, x0pp, y0pp)
                })
                y0 = y0pp
            x0 = x0pp

        return GeoDataFrame(result, crs=self.gdf.crs)
