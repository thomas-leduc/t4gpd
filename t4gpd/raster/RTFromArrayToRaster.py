"""
Created on 22 aug. 2023

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
from numpy import dtype, ndarray
from rasterio.io import DatasetReader
from rasterio.transform import Affine
from t4gpd.commons.ArrayLib import ArrayLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.raster.AbstractRasterGeoProcess import AbstractRasterGeoProcess


class RTFromArrayToRaster(AbstractRasterGeoProcess):
    """
    classdocs
    """

    def __init__(self, array, rasterOrRoi, ndv=-9999, debug=False):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use t4gpd.commons.raster.RasterLib instead")
        if not isinstance(array, (list, ndarray, tuple)):
            raise IllegalArgumentTypeException(array, "list, numpy ndarray, or tuple")
        self.array = ArrayLib.cast_compact_dtype(array)
        if 1 == self.array.ndim:
            self.array = self.array.reshape(1, -1)
        if 2 != self.array.ndim:
            raise IllegalArgumentTypeException(
                array, "*1D* or *2D* list, numpy ndarray, or tuple"
            )

        if not isinstance(rasterOrRoi, (DatasetReader, GeoDataFrame)):
            raise IllegalArgumentTypeException(
                rasterOrRoi, "DatasetReader or GeoDataFrame"
            )
        self.rasterOrRoi = rasterOrRoi
        self.ndv = ndv
        self.debug = debug

    def __get_type(arr):
        # Le format float16 n'est pas officiellement supporté dans la spécification TIFF
        from numpy import issubdtype, floating

        if issubdtype(arr.dtype, floating):
            return dtype("float")
        return arr.dtype

    def __extract_metadata_from_DatasetReader(self, raster):
        if self.array.shape[0] != raster.height:
            raise Exception(
                f"array.shape[0] ({self.array.shape[0]}) <> raster.height ({raster.height})!"
            )
        if self.array.shape[1] != raster.width:
            raise Exception(
                f"array.shape[1] ({self.array.shape[1]}) <> raster.width ({raster.width})!"
            )

        out_meta = raster.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": raster.height,
                "width": raster.width,
                "transform": raster.transform,
                "crs": raster.crs,
                "count": 1,
                "dtype": RTFromArrayToRaster.__get_type(self.array),
                "nodata": self.ndv,
            }
        )
        return out_meta

    def __extract_metadata_from_GeoDataFrame(self, roi):
        minx, miny, maxx, maxy = roi.total_bounds
        nrows, ncols = self.array.shape

        xres = (maxx - minx) / ncols
        yres = (maxy - miny) / nrows

        transform = Affine.translation(minx, maxy) * Affine.scale(xres, -yres)

        out_meta = {
            "driver": "GTiff",
            "height": nrows,
            "width": ncols,
            "transform": transform,
            "crs": roi.crs,
            "count": 1,
            "dtype": RTFromArrayToRaster.__get_type(self.array),
            "nodata": self.ndv,
            # "blockxsize": 1,
            # "blockysize": 1,
            # "compress": "lzw",
        }
        return out_meta

    def run(self):
        if isinstance(self.rasterOrRoi, DatasetReader):
            out_meta = self.__extract_metadata_from_DatasetReader(self.rasterOrRoi)

        elif isinstance(self.rasterOrRoi, GeoDataFrame):
            out_meta = self.__extract_metadata_from_GeoDataFrame(self.rasterOrRoi)

        #         print(f"""\theight / nrows = {out_meta['height']}
        # \twidth / ncols  = {out_meta['width']}
        # \tminx           = {out_meta['transform'][2]}
        # \tmaxy           = {out_meta['transform'][5]}
        # \txres           = {out_meta['transform'][0]}
        # \tyres           = {out_meta['transform'][4]}
        # \tndv            = {out_meta['nodata']}
        # """)
        result = self._write_and_load(self.array, out_meta, self.debug)
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from numpy import arange, flip
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        array = flip(arange(1, 26).reshape(5, -1), axis=0)
        raster = RTFromArrayToRaster(array, buildings, ndv=0, debug=False).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(1.4 * 8.26, 1.0 * 8.26))
        buildings.boundary.plot(ax=ax, color="green")
        show(raster, ax=ax, cmap="Blues_r", alpha=0.8)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# RTFromArrayToRaster.test()
