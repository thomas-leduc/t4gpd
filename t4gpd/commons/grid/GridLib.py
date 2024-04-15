'''
Created on 31 mars 2021

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
from geopandas import GeoDataFrame, overlay, sjoin_nearest
from numpy import ceil, gradient, linspace, ndarray, sqrt, zeros
from shapely.geometry import box, LineString, MultiLineString
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
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
                    "gid": r * self.ncols + c,
                    "row": r,
                    "column": c,
                    "neighbors4": neighbors4,
                    "neighbors8": neighbors8,
                    "geometry": box(x0, y0, x0pp, y0pp)
                })
                y0 = y0pp
            x0 = x0pp

        return GeoDataFrame(result, crs=self.gdf.crs)

    @staticmethod
    def getGrid1(gdf, dx, dy=None):
        dy = dx if (dy is None) else dy

        minx, miny, maxx, maxy = gdf.total_bounds
        ncols = int(ceil((maxx - minx) / dx))
        nrows = int(ceil((maxy - miny) / dy))

        xOffset = ((ncols * dx) - (maxx - minx)) / 2.0
        yOffset = ((nrows * dy) - (maxy - miny)) / 2.0

        x0, y0 = minx - xOffset, miny - yOffset

        rows = []
        for c, x in enumerate(linspace(x0, x0 + ncols * dx, ncols, endpoint=False)):
            xpp = x+dx
            for r, y in enumerate(linspace(y0, y0 + nrows * dy, nrows, endpoint=False)):
                ypp = y+dy
                rows.append({
                    "gid": r * ncols + c,
                    "dx": dx,
                    "dy": dy,
                    "geometry": box(x, y, xpp, ypp)
                })
        grid = GeoDataFrame(rows, crs=gdf.crs)
        grid2 = GridLib.getDistanceToNearestContour(gdf, grid)
        return grid2

    @staticmethod
    def __neighbors_4_8(nrows, ncols, r, c):
        e = r * ncols + (c + 1)
        ne = (r + 1) * ncols + (c + 1)
        n = (r + 1) * ncols + c
        nw = (r + 1) * ncols + (c - 1)
        w = r * ncols + (c - 1)
        sw = (r - 1) * ncols + (c - 1)
        s = (r - 1) * ncols + c
        se = (r - 1) * ncols + (c + 1)

        _na = -1
        if (0 == c):
            nw, w, sw = _na, _na, _na
        if (0 == r):
            sw, s, se = _na, _na, _na
        if (ncols == c + 1):
            ne, e, se = _na, _na, _na
        if (nrows == r + 1):
            nw, n, ne = _na, _na, _na
        return [e, n, w, s], [e, ne, n, nw, w, sw, s, se]

    @staticmethod
    def getGrid2(gdf, dx, dy=None, encode=True):
        dy = dx if (dy is None) else dy

        minx, miny, maxx, maxy = gdf.total_bounds
        ncols = int(ceil((maxx - minx) / dx))
        nrows = int(ceil((maxy - miny) / dy))

        xOffset = ((ncols * dx) - (maxx - minx)) / 2.0
        yOffset = ((nrows * dy) - (maxy - miny)) / 2.0

        x0, y0 = minx - xOffset, miny - yOffset

        rows = []
        for c, x in enumerate(linspace(x0, x0 + ncols * dx, ncols, endpoint=False)):
            xpp = x+dx
            for r, y in enumerate(linspace(y0, y0 + nrows * dy, nrows, endpoint=False)):
                ypp = y+dy
                neighbors4, neighbors8 = GridLib.__neighbors_4_8(
                    nrows, ncols, r, c)
                if encode:
                    neighbors4, neighbors8 = (ArrayCoding.encode(neighbors4),
                                              ArrayCoding.encode(neighbors8))
                rows.append({
                    "gid": r * ncols + c,
                    "row": r,
                    "column": c,
                    "neighbors4": neighbors4,
                    "neighbors8": neighbors8,
                    # "dx": dx,
                    # "dy": dy,
                    "geometry": box(x, y, xpp, ypp)
                })
        grid = GeoDataFrame(rows, crs=gdf.crs)
        return grid

    @staticmethod
    def getDistanceToNearestContour(gdf, grid):
        gdf2 = gdf.copy(deep=True)
        gdf2.geometry = gdf2.geometry.apply(
            lambda geom: MultiLineString(GeomLib.toListOfLineStrings(geom)))
        if "dist_to_ctr" in grid:
            grid.drop(columns="dist_to_ctr", inplace=True)
        grid2 = sjoin_nearest(
            grid, gdf2[["geometry"]], how="inner", distance_col="dist_to_ctr", max_distance=None)
        if ("index_right" not in gdf2) and ("index_right" in grid2):
            grid2.drop(columns="index_right", inplace=True)
        grid2.drop_duplicates(
            subset=["gid"], keep="first", ignore_index=True, inplace=True)
        return grid2

    @staticmethod
    def fromGridToNumpyArray(gdf, fieldvalue, rowFieldname="row", colFieldname="column"):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        for fieldname in [fieldvalue, rowFieldname, colFieldname]:
            if not fieldname in gdf:
                raise Exception(f"{fieldname} is not a relevant field name!")

        nrows = 1 + gdf[rowFieldname].max()
        ncols = 1 + gdf[colFieldname].max()
        result = zeros((nrows, ncols))

        for _, row in gdf.iterrows():
            r, c, v = row[rowFieldname], row[colFieldname], row[fieldvalue]
            if not ((r is None) or (c is None) or (v is None)):
                result[r, c] = v
        return result

    @staticmethod
    def fromNumpyArrayToGrid(nparray, gdf, fieldvalue, rowFieldname="row", colFieldname="column"):
        if not isinstance(nparray, ndarray):
            raise IllegalArgumentTypeException(gdf, "NumPy Array")
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        for fieldname in [rowFieldname, colFieldname]:
            if not fieldname in gdf:
                raise Exception(f"{fieldname} is not a relevant field name!")

        result = gdf.copy(deep=True)
        result[fieldvalue] = 0
        for idx, row in result.iterrows():
            r, c = row[rowFieldname], row[colFieldname]
            result.at[idx, fieldvalue] = nparray[r, c]
        return result

    @staticmethod
    def gradient(gdf, fieldvalue, rowFieldname="row", colFieldname="column", magn=1.0, normalize=False):
        nparray = GridLib.fromGridToNumpyArray(
            gdf, fieldvalue, rowFieldname, colFieldname)
        # nparray = nparray.T
        UU, VV = gradient(nparray)

        result = gdf.copy(deep=True)
        result["grad_x"], result["grad_y"] = 0, 0
        for idx, row in result.iterrows():
            r, c = row[rowFieldname], row[colFieldname]
            g = row.geometry.centroid.coords[0][0:2]
            grad_x, grad_y = UU[r, c], VV[r, c]

            if normalize:
                _magn = magn / sqrt(grad_x ** 2 + grad_y ** 2)
            else:
                _magn = magn
            grad_x, grad_y = _magn * grad_x, _magn * grad_y

            result.at[idx, "grad_x"] = grad_x
            result.at[idx, "grad_y"] = grad_y
            result.at[idx, "geometry"] = LineString(
                [g, [g[0] + grad_x, g[1] + grad_y]])
        return result

    @staticmethod
    def divergence(gdf, fieldvalue, rowFieldname="row", colFieldname="column", magn=1.0):
        nparray = GridLib.fromGridToNumpyArray(
            gdf, fieldvalue, rowFieldname, colFieldname)
        # nparray = nparray.T
        UU, VV = gradient(nparray)

        result = gdf.copy(deep=True)
        result["divergence"] = 0
        for idx, row in result.iterrows():
            r, c = row[rowFieldname], row[colFieldname]
            grad_x, grad_y = UU[r, c], VV[r, c]

            result.at[idx, "divergence"] = grad_x + grad_y
        return result

    @staticmethod
    def __overlayWithGrid(gdf, grid, how="difference"):
        _result = grid.loc[:, ["gid", "geometry"]]
        _result.geometry = _result.geometry.apply(lambda geom: geom.centroid)
        _result = overlay(_result, gdf, how)
        _result = set(_result.gid.to_list())
        return _result

    @staticmethod
    def getIndoorOutdoorGrid(gdf, grid):
        grid2 = grid.copy(deep=True)
        gids = GridLib.__overlayWithGrid(gdf, grid2, how="difference")
        grid2["indoor"] = grid2.gid.apply(
            lambda gid: 0 if (gid in gids) else 1)
        return grid2

    @staticmethod
    def getIndoorGrid(gdf, grid):
        grid2 = GridLib.getIndoorOutdoorGrid(gdf, grid)
        grid2 = grid2.loc[grid2[grid2.indoor == 1].index]
        grid2.reset_index(drop=True, inplace=True)
        return grid2

    @staticmethod
    def getOutdoorGrid(gdf, grid):
        grid2 = GridLib.getIndoorOutdoorGrid(gdf, grid)
        grid2 = grid2.loc[grid2[grid2.indoor == 0].index]
        grid2.reset_index(drop=True, inplace=True)
        return grid2

    @staticmethod
    def getSubgrid1(gdf, grid, dx, threshold):
        gid = grid.gid.max()
        rows = []
        for _, row in grid.iterrows():
            if (row.dist_to_ctr > threshold):
                rows.append({
                            "gid": row.gid,
                            "dx": row.dx,
                            "geometry": row.geometry
                            })
            else:
                x0, y0, x1, y1 = row.geometry.bounds
                ncols = int(round((x1 - x0) / dx))
                nrows = int(round((y1 - y0) / dx))
                for x in linspace(x0, x1, ncols, endpoint=False):
                    xpp = x+dx
                    for y in linspace(y0, y1, nrows, endpoint=False):
                        ypp = y+dx
                        gid += 1
                        rows.append({
                            "gid": gid,
                            "dx": dx,
                            "geometry": box(x, y, xpp, ypp)
                        })
        grid2 = GeoDataFrame(rows, crs=gdf.crs)
        grid3 = GridLib.getDistanceToNearestContour(gdf, grid2)
        return grid3
