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
import os
import rasterio
from numpy.random import default_rng
from os import remove
from os.path import exists
from tempfile import TemporaryDirectory
from t4gpd.commons.GeoProcess import GeoProcess


class AbstractRasterGeoProcess(GeoProcess):
    '''
    classdocs
    '''
    @staticmethod
    def _write_and_load(array, metadata, debug, indexes=1):
        rng = default_rng()

        if debug:
            ofile = f"__temporary__{rng.integers(1e12)}.tif"
            if exists(ofile):
                remove(ofile)
            with rasterio.open(ofile, "w", **metadata) as dst:
                if indexes is None:
                    dst.write(array)
                else:
                    dst.write(array, indexes=1)
            result = rasterio.open(ofile)
        else:
            with TemporaryDirectory() as tmpdir:
                ofile = f"{tmpdir}/temporary.tif"
                with rasterio.open(ofile, "w", **metadata) as dst:
                    if indexes is None:
                        dst.write(array)
                    else:
                        dst.write(array, indexes=indexes)
                result = rasterio.open(ofile)
        return result
