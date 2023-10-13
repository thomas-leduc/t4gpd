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
import rasterio
from numpy import nan, seterr
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.raster.AbstractRasterGeoProcess import AbstractRasterGeoProcess


class RTNdvi(AbstractRasterGeoProcess):
    '''
    classdocs
    '''

    def __init__(self, filename, debug=False):
        '''
        Constructor
        '''
        if not isinstance(filename, str):
            raise IllegalArgumentTypeException(
                filename, "input filename (str)")
        self.filename = filename
        self.debug = debug

    @staticmethod
    def __ndvi(filename):
        '''
        NDVI is a spectral approach used to assess vegetation.

        The density of vegetation (NDVI) at a certain point of the image is equal
        to the difference in the intensities of reflected light in the red and 
        infrared range divided by the sum of these intensities.

        raster (Landsat 8, Collection 2 Level-2):
            Band 1 - Blue
            Band 2 - Green
            Band 3 - Red
            Band 4 - Near Infrared
        '''
        with rasterio.open(filename, mode="r", nodata=0) as raster:
            red = raster.read(3).astype(float)
            nir = raster.read(4).astype(float)

            # Allow NumPy division by zero
            seterr(divide="ignore", invalid="ignore")
            ndvi = (nir - red) / (nir + red)

            # Set pixels whose values are outside the NDVI range (-1, 1) to NaN
            # Likely due to errors in the Landsat imagery
            ndvi[ndvi > 1] = nan
            ndvi[ndvi < -1] = nan

            out_meta = raster.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": raster.height,
                "width": raster.width,
                "transform": raster.transform,
                "crs": raster.crs,
                "count": 1,
                "dtype": ndvi.dtype,
            })

        return out_meta, ndvi

    def run(self):
        out_meta, ndvi = RTNdvi.__ndvi(self.filename)
        result = self._write_and_load(ndvi, out_meta, self.debug)
        return result


"""
src = "/home/tleduc/data/landsat/LC08_01_044_034_LC08_L1GT_044034_20130330_20170310_01_T2_LC08_L1GT_044034_20130330_20170310_01_T2_B1.TIF"
r = RTNdvi(src).run()
print(type(r))
"""
