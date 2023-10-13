'''
Created on 5 oct. 2023

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
from rasterio.io import DatasetReader
from rasterio.transform import Affine, AffineTransformer
from shapely import Point
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class RTFromRasterToGeoDataFrameOfPoints(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, raster, oFieldname="value"):
        '''
        Constructor
        '''
        if not isinstance(raster, DatasetReader):
            raise IllegalArgumentTypeException(raster, "DatasetReader")
        self.raster = raster
        self.oFieldname = oFieldname

    @staticmethod
    def __vectorize(raster, fieldname):
        transform, crs = raster.transform, raster.crs
        transformer = AffineTransformer(Affine(*transform))
        pixels = raster.read(1, masked=True)
        nrows, ncols = pixels.shape

        rows = []
        for nr in range(nrows):
            for nc in range(ncols):
                rows.append({
                    "geometry": Point(transformer.xy(nr, nc)),
                    fieldname: pixels[nr, nc]
                })
        return GeoDataFrame(rows, crs=crs)

    def run(self):
        return RTFromRasterToGeoDataFrameOfPoints.__vectorize(self.raster, self.oFieldname)

"""
from numpy import zeros
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STBBox import STBBox
from t4gpd.raster.RTFromArrayToRaster import RTFromArrayToRaster
from t4gpd.raster.RTToFile import RTToFile
from t4gpd.raster.STRasterize import STRasterize

buildings = GeoDataFrameDemos.regularGridOfPlots(2, 2)
buildings["HAUTEUR"] = 1 + buildings.gid
buildings.to_file("/tmp/buildings.shp")
roi = STBBox(buildings, buffDist=0).run()

dtm = zeros([10, 10])
dtm = RTFromArrayToRaster(dtm, roi).run()
RTToFile(dtm, "/tmp/dtm.tif").run()

dsm = STRasterize(buildings, dtm, attr="HAUTEUR").run()
RTToFile(dsm, "/tmp/dsm.tif").run()

gdf = RTFromRasterToGeoDataFrameOfPoints(dsm).run()
gdf.to_file("/tmp/points.shp")
"""
