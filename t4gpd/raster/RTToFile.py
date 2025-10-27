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
from rasterio.io import DatasetReader
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils


class RTToFile(GeoProcess):
    """
    classdocs
    """

    def __init__(self, raster, ofilename):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use t4gpd.commons.raster.RasterLib instead")
        if not isinstance(raster, DatasetReader):
            raise IllegalArgumentTypeException(raster, "DatasetReader")
        self.raster = raster

        if not isinstance(ofilename, str):
            raise IllegalArgumentTypeException(ofilename, "output filename (str)")
        self.ofilename = ofilename

    def run(self):
        with rasterio.open(self.ofilename, "w", **self.raster.meta) as dst:
            if 1 == self.raster.count:
                dst.write(self.raster.read(1), indexes=1)
            else:
                # write each band individually
                for band in range(self.raster.count):
                    # write data, band # (starting from 1)
                    dst.write(self.raster.read(band + 1), band + 1)

        return self.raster

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from rasterio.plot import show
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox
        from t4gpd.raster.RTClip import RTClip
        from t4gpd.raster.STRasterize import STRasterize

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        roi = STBBox(buildings, buffDist=0).run()
        raster1 = rasterio.open(
            "/home/tleduc/data/mnt_asc/mnt_nantes_2005_1m/MNT_L93_0354_6690.asc"
        )
        raster2 = RTClip(raster1, roi).run()
        raster3 = STRasterize(buildings, raster2, attr="HAUTEUR").run()
        # raster3 = STRasterize(buildings, raster2, attr=None).run()

        raster = RTToFile(raster3, "/tmp/raster3.tif").run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(1.4 * 8.26, 1.0 * 8.26))
        buildings.boundary.plot(ax=ax, color="red")
        show(raster, ax=ax, cmap="Blues_r", alpha=0.8)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# RTToFile.test()
