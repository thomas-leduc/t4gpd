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
import json
from geopandas import GeoDataFrame
from rasterio.io import DatasetReader
from rasterio.mask import mask
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.raster.AbstractRasterGeoProcess import AbstractRasterGeoProcess


class RTClip(AbstractRasterGeoProcess):
    """
    classdocs
    """

    def __init__(self, raster, roi, debug=False):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use t4gpd.commons.raster.RasterLib instead")
        if not isinstance(roi, GeoDataFrame):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        self.roi = roi

        if not isinstance(raster, DatasetReader):
            raise IllegalArgumentTypeException(raster, "DatasetReader")
        self.raster = raster
        self.debug = debug

    @staticmethod
    def __getFeatures(gdf):
        """
        Function to parse features from GeoDataFrame in such a manner that rasterio expects them
        """
        return [json.loads(gdf.to_json())["features"][0]["geometry"]]

    def run(self):
        out_img, out_transform = mask(
            self.raster, shapes=self.__getFeatures(self.roi), crop=True
        )
        out_meta = self.raster.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_img.shape[1],
                "width": out_img.shape[2],
                "transform": out_transform,
                "crs": self.roi.crs,
            }
        )
        result = self._write_and_load(out_img, out_meta, self.debug, indexes=None)
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        import rasterio
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        roi = STBBox(buildings, buffDist=0).run()
        raster = rasterio.open(
            "/home/tleduc/data/mnt_asc/mnt_nantes_2005_1m/MNT_L93_0354_6690.asc"
        )
        r = RTClip(raster, roi).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(8, 8))
        buildings.boundary.plot(ax=ax, color="red")
        show(r, ax=ax, cmap="Blues_r", alpha=0.8)
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# RTClip.test()
