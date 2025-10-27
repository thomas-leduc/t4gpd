"""
Created on 7 avr. 2021

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
from numpy import ceil, floor, sqrt
from shapely import Polygon
from shapely.affinity import translate
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.grid.AbstractGridLib import AbstractGridLib


class HexagonalTilingLib(AbstractGridLib):
    """
    classdocs
    """

    __slots__ = ("gdf", "dx", "dy", "minx", "miny", "ncols", "nrows")

    def __init__(self, gdf, dx, dy=None, encode=True):
        """
        Constructor
        """
        super().__init__(gdf, dx, dy, encode)

        # dx: hexagon diameter on x-axis
        self.dx = dx / 2.0
        # dy: hexagon diameter on y-axis
        self.dy = (sqrt(3.0) * self.dx / 2.0) if (dy is None) else dy / 2.0

        self.minx, self.miny, maxx, maxy = gdf.total_bounds
        self.ncols = int(ceil((maxx - self.minx) / (1.5 * self.dx))) + 1
        self.nrows = int(floor((maxy - self.miny) / (2 * self.dy))) + 1

    def __neighbors6(self, r, c):
        _gid = r * self.ncols + c
        if 0 == c % 2:
            nw, ne = _gid - 1, _gid + 1
            sw, se = nw - self.ncols, ne - self.ncols
        else:
            sw, se = _gid - 1, _gid + 1
            nw, ne = sw + self.ncols, se + self.ncols

        n = _gid + self.ncols
        s = _gid - self.ncols

        _na = -1
        if 0 == c:
            nw, sw = _na, _na
        if 0 == r:
            sw, s, se = _na, _na, _na
        if self.ncols == c + 1:
            ne, se = _na, _na
        if self.nrows == r + 1:
            if 0 == c % 2:
                n = _na
            else:
                nw, n, ne = _na, _na, _na

        return [ne, n, nw, sw, s, se]

    def grid(self):
        _hexagon = Polygon(
            [
                (self.dx, 0),
                (self.dx / 2, self.dy),
                (-self.dx / 2, self.dy),
                (-self.dx, 0),
                (-self.dx / 2, -self.dy),
                (self.dx / 2, -self.dy),
            ]
        )

        result = []
        for c in range(self.ncols):
            for r in range(self.nrows):
                neighbors6 = self.__neighbors6(r, c)
                if self.encode:
                    neighbors6 = ArrayCoding.encode(neighbors6)

                _xoff = self.minx + c * (1.5 * self.dx)

                if 0 == c % 2:
                    _yoff = self.miny + r * (2 * self.dy)
                else:
                    _yoff = self.miny + r * (2 * self.dy) + self.dy

                result.append(
                    {
                        "gid": r * self.ncols + c,
                        "neighbors6": neighbors6,
                        "geometry": translate(_hexagon, xoff=_xoff, yoff=_yoff),
                    }
                )

        return GeoDataFrame(result, crs=self.gdf.crs)
