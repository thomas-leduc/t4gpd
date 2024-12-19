'''
Created on 31 aug. 2020

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
from shapely.wkt import loads
from t4gpd.commons.GeoProcess import GeoProcess


class CSVWKTReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputFile, geomFieldName='the_geom:GEOMETRY', fieldSep=';',
                 srcEpsgCode='EPSG:4326', dstEpsgCode=None, decimalSep='.'):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.geomFieldName = geomFieldName
        self.fieldSep = fieldSep
        self.crs = srcEpsgCode
        self.dstEpsgCode = dstEpsgCode
        self.decimalSep = decimalSep

    def run(self):
        df = read_csv(self.inputFile, sep=self.fieldSep,
                      decimal=self.decimalSep)
        df.rename(columns={fieldname: fieldname.strip()
                  for fieldname in df.columns}, inplace=True)
        df.rename(columns={self.geomFieldName: "geometry"}, inplace=True)
        df.geometry = df.geometry.apply(lambda v: loads(v))
        gdf = GeoDataFrame(df, crs=self.crs)
        if not self.dstEpsgCode is None:
            return gdf.to_crs(self.dstEpsgCode)
        return gdf
