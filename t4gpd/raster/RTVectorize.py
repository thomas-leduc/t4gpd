'''
Created on 23 aug. 2023

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
from rasterio.features import shapes
from rasterio.io import DatasetReader
from shapely.geometry import shape
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class RTVectorize(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, raster):
        '''
        Constructor
        '''
        if not isinstance(raster, DatasetReader):
            raise IllegalArgumentTypeException(raster, "DatasetReader")
        self.raster = raster

    @staticmethod
    def __vectorize(raster):
        pixels = raster.read(1, masked=True)
        shape_gen = ((shape(s), v)
                     for s, v in shapes(pixels, transform=raster.transform))
        gdf = GeoDataFrame(
            dict(zip(["geometry", "pix_value"], zip(*shape_gen))), crs=raster.crs)
        return gdf

    def run(self):
        return RTVectorize.__vectorize(self.raster)


"""
import matplotlib.pyplot as plt
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STBBox import STBBox
from t4gpd.raster.RTClip import RTClip
from t4gpd.raster.RTLoad import RTLoad
from t4gpd.raster.STRasterize import STRasterize

dtmdir = "/home/tleduc/data/mnt_asc/mnt_nantes_2005_1m"
raster = RTLoad(f"{dtmdir}/MNT_L93_0354_6690.asc").run()

buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
roi = STBBox(buildings, buffDist=0).run()
dtm = RTClip(raster, roi).run()
raster = STRasterize(buildings, dtm, attr="HAUTEUR").run()

# plt.imshow(raster.read(1), cmap="BrBG")
# plt.show()

gdf = RTVectorize(raster).run()
gdf.drop(gdf[gdf.pix_value == 0].index, inplace=True)

fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
buildings.boundary.plot(ax=ax, color="red", linewidth=1)
gdf.plot(ax=ax, column="pix_value", alpha=0.4)
plt.axis("off")
plt.tight_layout()
plt.show()

buildings.to_file("/tmp/0.shp")
gdf.to_file("/tmp/1.shp")
"""
