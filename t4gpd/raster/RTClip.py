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
from geopandas import read_file
import json
from geopandas import GeoDataFrame
from rasterio.io import DatasetReader
from rasterio.mask import mask
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.raster.AbstractRasterGeoProcess import AbstractRasterGeoProcess


class RTClip(AbstractRasterGeoProcess):
    '''
    classdocs
    '''

    def __init__(self, raster, roi, debug=False):
        '''
        Constructor
        '''
        if not isinstance(roi, GeoDataFrame):
            raise IllegalArgumentTypeException(roi, "GeoDataFrame")
        self.roi = roi

        if not isinstance(raster, DatasetReader):
            raise IllegalArgumentTypeException(raster, "DatasetReader")
        self.raster = raster
        self.debug = debug

    @staticmethod
    def __getFeatures(gdf):
        '''
        Function to parse features from GeoDataFrame in such a manner that rasterio expects them
        '''
        return [json.loads(gdf.to_json())["features"][0]["geometry"]]

    def run(self):
        out_img, out_transform = mask(
            self.raster, shapes=self.__getFeatures(self.roi), crop=True)
        out_meta = self.raster.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_img.shape[1],
            "width": out_img.shape[2],
            "transform": out_transform,
            "crs": self.roi.crs
        })
        result = self._write_and_load(out_img, out_meta, self.debug, indexes=None)
        return result


"""
roi = read_file("/home/tleduc/prj/uenv_aau_msc_course/tps/data/roi.shp")
raster = rasterio.open("/home/tleduc/data/mnt_asc/mnt_nantes_2005_1m/MNT_L93_0354_6690.asc")
r = RTClip(raster, roi).run()
print(type(r))
"""
