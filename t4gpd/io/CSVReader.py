'''
Created on 3 juil. 2020

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from pandas import read_csv
from shapely import Point
from t4gpd.commons.GeoProcess import GeoProcess


class CSVReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputFile, xFieldName="longitude", yFieldName="latitude",
                 fieldSep=",", srcEpsgCode="epsg:4326", dstEpsgCode=None, decimalSep="."):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.xFieldName = xFieldName
        self.yFieldName = yFieldName
        self.fieldSep = fieldSep
        self.crs = srcEpsgCode
        self.dstEpsgCode = dstEpsgCode
        self.decimalSep = decimalSep

    def run(self):
        df = read_csv(self.inputFile, sep=self.fieldSep,
                      decimal=self.decimalSep)
        df["geometry"] = df.apply(
            lambda row: Point(row[self.xFieldName], row[self.yFieldName]), axis=1)
        gdf = GeoDataFrame(df, crs=self.crs, geometry="geometry")
        if not self.dstEpsgCode is None:
            gdf = gdf.to_crs(self.dstEpsgCode)
        return gdf
