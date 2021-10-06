'''
Created on 17 aug. 2020

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
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class ObjReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputFile, crs='EPSG:2154'):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.crs = crs

    def __extract_v_vt_vn(self, tmp):
        # Extract vertex index/vextex texture coord. index/vertex normal index
        # f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3 ...
        tmp = tmp.strip().split('/')
        if 1 == len(tmp):
            return tmp[0], None, None
        elif 2 == len(tmp):
            return tmp[0], tmp[1], None
        elif 3 == len(tmp):
            return tmp
        raise IllegalArgumentTypeException(tmp, 'v1/vt1/vn1')

    def __read(self):
        rows_of_faces, rows_of_lines = [], []
        
        with open(self.inputFile, 'r') as f:
            # objectName, groupName, materialName = None, None, None
            vtxId, vertices = 1, dict()

            for line in f:
                line = line.strip()
                tmp = line.split()
                if 0 < len(tmp):
                    if 'o' == tmp[0]:
                        # objectName = tmp[1]
                        pass

                    elif 'g' == tmp[0]:
                        # groupName = tmp[1]
                        pass

                    elif 'usemtl' == tmp[0]:
                        # materialName = tmp[1]
                        pass

                    elif 'v' == tmp[0]:
                        vertices[vtxId] = (float(tmp[1]), float(tmp[2]), float(tmp[3]))
                        vtxId += 1

                    elif 'l' == tmp[0]:  # POLYLINE ELEMENTS
                        _vertices = [vertices[int(i)] for i in tmp[1:]]
                        _polyline = LineString(_vertices)
                        _row = {'geometry': _polyline}
                        rows_of_lines.append(_row)

                    elif 'f' == tmp[0]:  # POLYGONAL ELEMENTS
                        _trios = [self.__extract_v_vt_vn(x) for x in tmp[1:]]
                        _vertices = [vertices[int(i)] for i, _, _ in _trios]
                        _polygon = Polygon(_vertices)
                        _row = {'geometry': _polygon}
                        rows_of_faces.append(_row)

        return rows_of_faces, rows_of_lines

    def run(self):
        rows_of_faces, rows_of_lines = self.__read()

        if 0 == len(rows_of_faces) + len(rows_of_lines):
            return None
        elif 0 == len(rows_of_faces):
            return GeoDataFrame(rows_of_lines, crs=self.crs)
        elif 0 == len(rows_of_lines):
            return GeoDataFrame(rows_of_faces, crs=self.crs)
        return GeoDataFrame(rows_of_faces, crs=self.crs), GeoDataFrame(rows_of_lines, crs=self.crs)
