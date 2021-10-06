'''
Created on 10 avr. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry.linestring import LineString
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class LineStringCuttingLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def __fromLineStringToSegments(line, cuttingDist):
        if not isinstance(line, LineString):
            raise IllegalArgumentTypeException(line, 'LineString')
        if not (2 == len(line.coords)):
            raise IllegalArgumentTypeException(line, '2-point LineString')

        result = []
        coords, lineLen = line.coords, line.length
        if (lineLen <= cuttingDist):
            result.append(line)
        else:
            _d = lineLen / round(lineLen / cuttingDist)
            _prev, _accD = coords[0], _d
            while (_accD < lineLen):
                _curr = line.interpolate(_accD, normalized=False)
                result.append(LineString([_prev, _curr]))
                _prev, _accD = _curr, _accD + _d
            result.append(LineString([_prev, coords[1]]))
        return result

    @staticmethod
    def cuttingIntoSegments(gdf, cuttingDist):
        result = []
        for _, row in gdf.iterrows():
            _geom = row.geometry
            _segms = GeomLib.toListOfBipointsAsLineStrings(_geom)
            for _segm in _segms:
                result += LineStringCuttingLib.__fromLineStringToSegments(_segm, cuttingDist)
        return GeoDataFrame([{'gid': i, 'geometry': g} for i, g in enumerate(result)], crs=gdf.crs)
