"""
Created on 29 nov. 2023

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

import warnings
from geopandas import GeoDataFrame
from numpy import full
from t4gpd.commons.TypeLib import TypeLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.raster.AbstractRasterGeoProcess import AbstractRasterGeoProcess
from t4gpd.raster.RTFromArrayToRaster import RTFromArrayToRaster


class STFromGridToRaster(AbstractRasterGeoProcess):
    """
    classdocs
    """

    def __init__(
        self,
        grid,
        fieldname,
        rowFieldname="row",
        columnFieldname="column",
        roi=None,
        ndv=-1,
        debug=False,
    ):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use t4gpd.commons.raster.RasterLib instead")

        if not isinstance(grid, GeoDataFrame):
            raise IllegalArgumentTypeException(grid, "GeoDataFrame")
        self.grid = grid

        for field in [fieldname, rowFieldname, columnFieldname]:
            if field not in grid:
                raise IllegalArgumentTypeException(
                    field, "must be a valid grid field name"
                )
        self.fieldname = fieldname
        self.rowFieldname = rowFieldname
        self.columnFieldname = columnFieldname
        self.roi = roi
        self.ndv = ndv
        self.debug = debug

    def __get_nrows_ncols(self):
        # if self.roi is None:
        nrows = 1 + self.grid[self.rowFieldname].max()
        ncols = 1 + self.grid[self.columnFieldname].max()
        return nrows, ncols

    def __as_array(self, nrows, ncols):
        arr = full([nrows, ncols], self.ndv, dtype=type(self.ndv))

        if not TypeLib.are_both_floating_or_integer(
            self.ndv, self.grid[self.fieldname]
        ):
            warnings.warn(
                "The numerical types of the NDV and the series of values are not identical"
            )

        for _, row in self.grid.iterrows():
            nr = row[self.rowFieldname]
            nc = row[self.columnFieldname]
            value = row[self.fieldname]
            arr[(nrows - 1) - nr, nc] = value

        return arr

    def run(self):
        nrows, ncols = self.__get_nrows_ncols()
        arr = self.__as_array(nrows, ncols)
        # print(arr.shape)
        # return arr

        roi = self.grid if self.roi is None else self.roi
        raster = RTFromArrayToRaster(arr, roi, self.ndv, self.debug).run()
        return raster

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STGrid import STGrid

        my_cmap = ListedColormap(["blue", "green"])

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        # buildings = GeoDataFrameDemos.singleBuildingInNantes()

        grid = STGrid(
            buildings,
            dx=5,
            dy=5,
            indoor="both",
            intoPoint=True,
            encode=True,
            withDist=False,
        ).run()

        ndv = 0
        # grid.loc[len(grid), ["row", "column", "indoor"]] = int(grid.row.max() + 6), int(grid.column.max()), ndv
        grid.row = grid.row.astype(int)
        grid.column = grid.column.astype(int)

        raster = STFromGridToRaster(
            grid,
            "indoor",
            rowFieldname="row",
            columnFieldname="column",
            ndv=ndv,
            debug=False,
        ).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        buildings.boundary.plot(ax=ax, color="red")
        show(raster, ax=ax, cmap=my_cmap, alpha=0.8)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# STFromGridToRaster.test()
