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
from geopandas import GeoDataFrame
from shapely.prepared import prep
from t4gpd.commons.grid.AbstractGridLib import AbstractGridLib
from t4gpd.commons.grid.GridLib import GridLib


class DichotomizedGrid(AbstractGridLib):
    """
    classdocs
    """
    __slots__ = ("gdf", "niter", "dx", "dy")

    def __init__(self, gdf, niter=5, encode=True):
        """
        Constructor
        """
        super().__init__(gdf, None, None, encode)
        self.gdf = self.gdf.explode(ignore_index=True).reset_index(drop=True)
        self.niter = niter
        minx, miny, maxx, maxy = self.gdf.total_bounds
        self.dx = maxx - minx
        self.dy = maxy - miny

    def __rapidIntersects(self, left, right):
        gid, result = 0, []
        for _, leftRow in left.iterrows():
            leftGeom = leftRow.geometry
            pLeftGeom = prep(leftGeom)
            rightGeoms = filter(pLeftGeom.intersects, right.geometry)
            for rightGeom in rightGeoms:
                if leftGeom.intersects(rightGeom):
                    _row = dict(leftRow)
                    _row["local_id"] = gid
                    result.append(_row)
                    gid += 1
                    break
        return GeoDataFrame(result, crs=self.gdf.crs)

    def grid(self):
        result, nrows, grid = dict(), 1, self.gdf

        for i in range(self.niter):
            grid = GridLib(grid, self.dx, self.dy, self.encode).grid()
            grid = self.__rapidIntersects(grid, self.gdf)
            result[i] = {"nrows": nrows, "dx": self.dx, "dy": self.dy, "grid": grid}

            self.dx, self.dy, nrows = self.dx / 2.0, self.dy / 2.0, 2 * nrows

        return result
