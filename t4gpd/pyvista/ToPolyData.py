'''
Created on 5 avr. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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

from numpy import arange, array, ndarray
from pyvista import MultiBlock, MultipleLines, PolyData 
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class ToPolyData(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdfs, fieldname=None):
        '''
        Constructor
        '''
        if not isinstance(gdfs, (list, tuple, ndarray)):
            raise IllegalArgumentTypeException(gdfs, 'list or tuple of GeoDataFrames')
        self.gdfs = gdfs
        self.fieldname = fieldname

    def __fromGeomToPolyData(self, geom):
        # https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf
        if ('Point' == geom.geom_type):
            point = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in geom.coords]
            point = array(point)
            return [ PolyData(point) ]

        elif ('LineString' == geom.geom_type):
            points = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in geom.coords]
            points = array(points)
            return [ MultipleLines(points) ]

        elif ('Polygon' == geom.geom_type):
            if (GeomLib.isConvex(geom) or GeomLib.isHoled(geom)):
                points = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in geom.exterior.coords]
                npoints = len(points)
                faces = [npoints] + arange(npoints).tolist()
                points, faces = array(points), array(faces)
                return [ PolyData(points, faces) ]
            else:
                result = []
                triangles = GeomLib.fromPolygonToListOfTriangles(geom)
                for triangle in triangles:
                    points = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in triangle.exterior.coords]
                    npoints = len(points)
                    faces = [npoints] + arange(npoints).tolist()
                    points, faces = array(points), array(faces)
                    result.append(PolyData(points, faces))
                return result

        raise Exception('Do not handle GeometryCollection!')

    def __fromGeoDataFrameToDictOfPolyDatas(self, gdf, rank):
        gdf = gdf.explode(ignore_index=True)
        # print(gdf.columns)
        result = {}
        for idx, row in gdf.iterrows():
            geom = row.geometry
            polyDatas = self.__fromGeomToPolyData(geom)

            # we can add some attributes to the current PolyData
            if self.fieldname is not None:
                attrValue = row[self.fieldname] if self.fieldname in gdf else float('nan')
                for polyData in polyDatas:
                    polyData.cell_data[self.fieldname] = attrValue

            for i, polyData in enumerate(polyDatas):
                result[f'{rank}_{idx}_{i}'] = polyData
        return result

    def run(self):
        result = {}
        rank = 0
        for rank, gdf in enumerate(self.gdfs):
            result.update(self.__fromGeoDataFrameToDictOfPolyDatas(gdf, rank))
        polyBlocks = MultiBlock(result)
        polyGrid = polyBlocks.combine()
        return polyGrid
