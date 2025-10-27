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
import rasterio
from geopandas import GeoDataFrame
from numpy import float32
from rasterio import features
from rasterio.io import DatasetReader
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.raster.AbstractRasterGeoProcess import AbstractRasterGeoProcess


class STRasterize(AbstractRasterGeoProcess):
    """
    classdocs
    """

    def __init__(self, gdf, raster, attr=None, debug=False):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use t4gpd.commons.raster.RasterLib instead")
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        self.gdf = gdf

        if not ((attr is None) or (attr in gdf)):
            raise IllegalArgumentTypeException(
                attr, "must be either None or a valid field name"
            )
        self.attr = attr

        if not isinstance(raster, DatasetReader):
            raise IllegalArgumentTypeException(raster, "DatasetReader")
        self.raster = raster
        self.debug = debug

    def run(self):
        if self.attr is None:
            geoms = self.gdf.geometry.to_list()
            rasterized = features.rasterize(
                geoms,
                out_shape=self.raster.shape,
                transform=self.raster.transform,
                all_touched=False,
                fill=0,  # background value
                default_value=1,
                # merge_alg=MergeAlg.replace,
                dtype=float32,
            )

        else:
            pairs = (
                (geom, value)
                for geom, value in zip(self.gdf.geometry, self.gdf[self.attr])
            )

            rasterized = features.rasterize(
                pairs,
                out_shape=self.raster.shape,
                transform=self.raster.transform,
                all_touched=False,
                fill=0,  # background value
                # merge_alg=MergeAlg.replace,
                dtype=float32,
            )

        out_meta = self.raster.meta.copy()
        out_meta.update(
            {
                "driver": "GTiff",
                "height": self.raster.height,
                "width": self.raster.width,
                "transform": self.raster.transform,
                "crs": self.raster.crs,
                "count": 1,
                "dtype": rasterio.float32,
            }
        )

        result = self._write_and_load(rasterized, out_meta, self.debug)
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox
        from t4gpd.raster.RTClip import RTClip

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        roi = STBBox(buildings, buffDist=0).run()
        raster1 = rasterio.open(
            "/home/tleduc/data/mnt_asc/mnt_nantes_2005_1m/MNT_L93_0354_6690.asc"
        )
        raster2 = RTClip(raster1, roi).run()
        raster3 = STRasterize(buildings, raster2, attr="HAUTEUR").run()
        # raster3 = STRasterize(buildings, raster2, attr=None).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(1.4 * 8.26, 1.0 * 8.26))
        buildings.boundary.plot(ax=ax, color="red")
        show(raster3, ax=ax, cmap="Blues_r", alpha=0.8)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# STRasterize.test()
