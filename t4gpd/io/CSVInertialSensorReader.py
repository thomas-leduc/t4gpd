'''
Created on 3 juil. 2020

@author: tleduc

Copyright 2020 Thomas Leduc

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
from numpy import cos, sin

from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.CSVLib import CSVLib
from t4gpd.commons.GeoProcess import GeoProcess


class CSVInertialSensorReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputFile, xFieldName='X', yFieldName='Y', zFieldName='Z',
                 distFieldName='Distance', azimFieldName='degree',
                 lon0FieldName='longitude', lat0FieldName='latitude',
                 fieldSep=',', srcEpsgCode='EPSG:4326', dstEpsgCode='EPSG:2154',
                 cartesian=True, decimalSep='.'):
        '''
        Constructor
        '''
        self.inputFile = inputFile

        if ((xFieldName is None) or (yFieldName is None) or
            (distFieldName is None) or (azimFieldName is None)):
            raise Exception('')

        self.xFieldName = xFieldName
        self.yFieldName = yFieldName
        self.zFieldName = zFieldName
        self.distFieldName = distFieldName
        self.azimFieldName = azimFieldName

        self.cartesian = cartesian
        self.lon0FieldName = lon0FieldName
        self.lat0FieldName = lat0FieldName
        self.fieldSep = fieldSep
        self.crs = srcEpsgCode
        self.dstEpsgCode = dstEpsgCode
        self.decimalSep = decimalSep

    @staticmethod
    def __transform(pt, srcEpsgCode, dstEpsgCode):
        '''
        import pyproj
        from shapely.ops import transform
        srcCrs = pyproj.CRS(srcEpsgCode)
        dstCrs = pyproj.CRS(dstEpsgCode)
        project = pyproj.Transformer.from_crs(srcCrs, dstCrs, always_xy=True).transform
        return transform(project, pt)
        '''
        inputGdf = GeoDataFrame([{'geometry':pt}], crs=srcEpsgCode)
        outputGdf = inputGdf.to_crs(dstEpsgCode)
        return outputGdf.geometry[0]

    def run(self):
        _rows = CSVLib.read(self.inputFile, self.fieldSep, self.decimalSep)

        p0 = Point(0, 0)
        if ((self.lon0FieldName is not None) and (self.lat0FieldName is not None)):
            p0 = Point(_rows[0][self.lon0FieldName], _rows[0][self.lat0FieldName])
            p0 = CSVInertialSensorReader.__transform(p0, self.crs, self.dstEpsgCode)

        rows = []
        if self.cartesian:
            for row in _rows:
                if self.zFieldName is None:
                    row['geometry'] = Point(row[self.yFieldName] + p0.x,
                                            row[self.xFieldName] + p0.y)
                else:
                    row['geometry'] = Point(row[self.yFieldName] + p0.x,
                                            row[self.xFieldName] + p0.y,
                                            row[self.zFieldName])
                rows.append(row)
                result = GeoDataFrame(rows, crs=self.dstEpsgCode)
                # result = result.rotate(_rows[0]['degree'], origin=p0, use_radians=False)

        else:
            for i, row in enumerate(_rows):
                r = row[self.distFieldName]
                azim = AngleLib.toRadians(row[self.azimFieldName])
                if (0 < i):
                    r = r - _rows[i - 1][self.distFieldName]
                row['geometry'] = p0 = Point(r * sin(azim) + p0.x, r * cos(azim) + p0.y)
                rows.append(row)
                result = GeoDataFrame(rows, crs=self.dstEpsgCode)

        return result
