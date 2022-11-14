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
from pyvista import MultiBlock, UnstructuredGrid
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from vtkmodules.util.vtkConstants import VTK_POLYGON, VTK_POLY_LINE, VTK_TRIANGLE, \
    VTK_VERTEX


class ToUnstructuredGrid(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdfs, fieldname=None):
        '''
        Constructor
        '''
        if not isinstance(gdfs, (list, tuple, ndarray)):
            raise IllegalArgumentTypeException(gdfs, 'list or tuple of GeoDataFrames')
        assert GeoDataFrameLib.shareTheSameCrs(*gdfs), 'gdfs are expected to share the same crs!'
        self.gdfs = gdfs
        self.fieldname = fieldname

    def __fromGeomToUnstructuredGrids(self, geom):
        # https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf
        if ('Point' == geom.geom_type):
            point = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in geom.coords]
            cells = [1, 0]
            cells, celltypes, points = array(cells), array([VTK_VERTEX]), array(point)
            return [ UnstructuredGrid(cells, celltypes, points) ]

        elif ('LineString' == geom.geom_type):
            points = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in geom.coords]
            npoints = len(points)
            cells = [npoints] + arange(npoints).tolist()
            cells, celltypes, points = array(cells), array([VTK_POLY_LINE]), array(points)
            return [ UnstructuredGrid(cells, celltypes, points) ]

        elif ('Polygon' == geom.geom_type):
            if (GeomLib.isConvex(geom) or GeomLib.isHoled(geom)):
                points = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in geom.exterior.coords]
                npoints = len(points)
                cells = [npoints] + arange(npoints).tolist()
                cells, celltypes, points = array(cells), array([VTK_POLYGON]), array(points)
                return [ UnstructuredGrid(cells, celltypes, points) ]
            else:
                result = []
                triangles = GeomLib.fromPolygonToListOfTriangles(geom)
                for triangle in triangles:
                    points = [[xyz[0], xyz[1], 0 if len(xyz) == 2 else xyz[2]] for xyz in triangle.exterior.coords]
                    npoints = len(points)
                    cells = [npoints] + arange(npoints).tolist()
                    cells, celltypes, points = array(cells), array([VTK_TRIANGLE]), array(points)
                    result.append(UnstructuredGrid(cells, celltypes, points))
                return result

        raise Exception('Unreachable instruction!')

    def __fromGeoDataFrameToDictOfUnstructuredGrids(self, gdf, rank):
        gdf = gdf.explode(ignore_index=True)
        # print(gdf.columns)
        result = {}
        for idx, row in gdf.iterrows():
            geom = row.geometry
            partialPolyUgrids = self.__fromGeomToUnstructuredGrids(geom)

            # we can add some attributes to the current UnstructuredGrid
            if self.fieldname is not None:
                attrValue = row[self.fieldname] if self.fieldname in gdf else float('nan')
                for partialPolyUgrid in partialPolyUgrids:
                    partialPolyUgrid.cell_data[self.fieldname] = attrValue

            for i, partialPolyUgrid in enumerate(partialPolyUgrids):
                result[f'{rank}_{idx}_{i}'] = partialPolyUgrid
        return result

    def run(self):
        result = {}
        rank = 0
        for rank, gdf in enumerate(self.gdfs):
            result.update(self.__fromGeoDataFrameToDictOfUnstructuredGrids(gdf, rank))
        polyBlocks = MultiBlock(result)
        polyGrid = polyBlocks.combine()
        return polyGrid
