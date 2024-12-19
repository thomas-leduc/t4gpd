'''
Created on 22 aug. 2023

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
from geopandas import GeoDataFrame
from numpy import asarray, dtype, ndarray
from rasterio.io import DatasetReader
from rasterio.transform import Affine
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.raster.AbstractRasterGeoProcess import AbstractRasterGeoProcess


class RTFromArrayToRaster(AbstractRasterGeoProcess):
    '''
    classdocs
    '''

    def __init__(self, array, rasterOrRoi, ndv=-9999, debug=False):
        '''
        Constructor
        '''
        if not isinstance(array, (list, ndarray, tuple)):
            raise IllegalArgumentTypeException(
                array, "list, numpy ndarray, or tuple")
        self.array = RTFromArrayToRaster.__asarray(array)
        if (1 == self.array.ndim):
            self.array = self.array.reshape(1, -1)
        if (2 != self.array.ndim):
            raise IllegalArgumentTypeException(
                array, "*1D* or *2D* list, numpy ndarray, or tuple")

        if not isinstance(rasterOrRoi, (DatasetReader, GeoDataFrame)):
            raise IllegalArgumentTypeException(
                rasterOrRoi, "DatasetReader or GeoDataFrame")
        self.rasterOrRoi = rasterOrRoi
        self.ndv = ndv
        self.debug = debug

    @staticmethod
    def __asarray(array):
        array = asarray(array)
        if (array.dtype == dtype(float)):
            return array.astype("float32")
        elif (array.dtype == dtype(int)):
            # Conversion to uint16, int16, int32, etc. is automatic
            return array.astype("uint8")
        raise IllegalArgumentTypeException(array, "Array of int or float values")

    def __extract_metadata_from_DatasetReader(self, raster):
        if (self.array.shape[0] != raster.height):
            raise Exception(
                f"array.shape[0] ({self.array.shape[0]}) <> raster.height ({raster.height})!")
        if (self.array.shape[1] != raster.width):
            raise Exception(
                f"array.shape[1] ({self.array.shape[1]}) <> raster.width ({raster.width})!")

        out_meta = raster.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": raster.height,
            "width": raster.width,
            "transform": raster.transform,
            "crs": raster.crs,
            "count": 1,
            "dtype": self.array.dtype,
            "nodata": self.ndv
        })
        return out_meta

    def __extract_metadata_from_GeoDataFrame(self, roi):
        minx, miny, maxx, maxy = roi.total_bounds
        nrows, ncols = self.array.shape

        xres = (maxx-minx) / ncols
        yres = (maxy-miny) / nrows

        transform = Affine.translation(minx, maxy) * Affine.scale(xres, -yres)

        out_meta = {
            "driver": "GTiff",
            "height": nrows,
            "width": ncols,
            "transform": transform,
            "crs": roi.crs,
            "count": 1,
            "dtype": self.array.dtype,
            "nodata": self.ndv,
            # "blockxsize": 1,
            # "blockysize": 1,
            # "compress": "lzw",
        }
        return out_meta

    def run(self):
        if isinstance(self.rasterOrRoi, DatasetReader):
            out_meta = self.__extract_metadata_from_DatasetReader(
                self.rasterOrRoi)

        elif isinstance(self.rasterOrRoi, GeoDataFrame):
            out_meta = self.__extract_metadata_from_GeoDataFrame(
                self.rasterOrRoi)

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


"""
import contextily as ctx
import matplotlib.pyplot as plt
from t4gpd.raster.RTToFile import RTToFile
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STBBox import STBBox
from numpy import arange

buildings = GeoDataFrameDemos.districtGraslinInNantesBuildings()
roi = STBBox(buildings, buffDist=0).run()

buildings.to_file("/tmp/buildings.shp")
roi.to_file("/tmp/roi.shp")

array = arange(20).reshape(4, -1).astype(float)
array = arange(20).reshape(2, -1).astype(float)
raster1 = RTFromArrayToRaster(array, roi).run()
RTToFile(raster1, "/tmp/raster1.tif").run()

fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
buildings.boundary.plot(ax=ax, color="red", hatch=".")
ctx.add_basemap(ax, crs=buildings.crs, source="/tmp/raster1.tif")
ax.axis("off")
plt.tight_layout()
plt.show()
"""

"""
from geopandas import read_file
from t4gpd.raster.RTClip import RTClip
from t4gpd.raster.RTLoad import RTLoad
from t4gpd.raster.RTToFile import RTToFile
from t4gpd.raster.STRasterize import STRasterize

srcdir = "/home/tleduc/prj/uenv_aau_msc_course/tps"
dtmdir = "/home/tleduc/data/mnt_asc/mnt_nantes_2005_1m";
raster = RTLoad(f"{dtmdir}/MNT_L93_0354_6690.asc").run()

#~ CROP RASTER FILE
roi = read_file(f"{srcdir}/data/roi.shp")
dtm = RTClip(raster, roi).run()
RTToFile(dtm, f"{srcdir}/data/dtm.tif").run()

#~ BUILDINGS LAYER RASTERIZING
buildings = read_file(f"{srcdir}/data/buildings.shp")
_dsm1 = STRasterize(buildings, dtm, attr="HAUTEUR").run()
RTToFile(_dsm1, f"{srcdir}/data/_dsm1.tif").run()

#~ STATUE LAYER RASTERIZING
statue = read_file(f"{srcdir}/data/statue.shp")
_dsm2 = STRasterize(statue, dtm, attr="HAUTEUR").run()
RTToFile(_dsm2, f"{srcdir}/data/_dsm2.tif").run()

#~ DSM1 + DSM2 => DSM12
dsm12 = _dsm1.read(1) + _dsm2.read(1)
dsm12 = RTFromArrayToRaster(dsm12, roi).run()
RTToFile(dsm12, f"{srcdir}/data/dsm12.tif").run()
"""

"""
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from numpy import arange, flip
from shapely import box
from t4gpd.morph.STGrid import STGrid
from t4gpd.raster.RTToFile import RTToFile

roi = GeoDataFrame([{"geometry": box(0, 0, 50, 50)}])
grid = STGrid(roi, dx=10, dy=None, indoor=None, intoPoint=False,
              encode=False, withDist=False).run()

array = flip(arange(25).reshape(5,-1), axis=0)
raster = RTFromArrayToRaster(array, roi, ndv=0, debug=False).run()

# MAPPING - OK WITH QGIS
roi.to_file("/tmp/roi.shp")
grid.to_file("/tmp/grid.shp")
RTToFile(raster, "/tmp/raster.tif").run()

# MAPPING - BUG WITH IMSHOW
fig, ax = plt.subplots(figsize=(1.4 * 8.26, 1.0 * 8.26))
roi.boundary.plot(ax=ax, color="green")
grid.plot(ax=ax, column="gid", cmap="magma", legend=True)
ax.imshow(raster.read(1), cmap="magma")
ax.axis("off")
fig.tight_layout()
plt.show()
plt.close(fig)
"""
