'''
Created on 5 juin 2022

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
from geopandas import GeoDataFrame
from numpy import asarray, cos, ndarray, pi, sin
from numpy.linalg import norm
from pyvista.core.pointset import UnstructuredGrid
from shapely.geometry import LineString, Point
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from vtkmodules.vtkCommonCore import vtkIdList, vtkPoints
from vtkmodules.vtkFiltersGeneral import vtkOBBTree


class RayCastingIn3DLib(object):
    '''
    classdocs
    '''
    INFINITY = float('inf')

    @staticmethod
    def areCovisibleObbTree(obbTree, srcPt, dstPt, epsilon=1e-6):
        assert isinstance(obbTree, vtkOBBTree), 'obbTree must be a vtkOBBTree!'
        _points = vtkPoints()
        _cellIds = vtkIdList()
        code = obbTree.IntersectWithLine(srcPt, dstPt, _points, None)
        
        if (0 == code):
            # NO POINTS HIT
            return True
        else:
            pointData = _points.GetData()
            noPoints = pointData.GetNumberOfTuples()
            if (2 == noPoints):
                _distSrc = norm(asarray(pointData.GetTuple3(0)) - asarray(srcPt))
                _distDst = norm(asarray(pointData.GetTuple3(1)) - asarray(dstPt))
                if (_distSrc < epsilon) and (_distDst < epsilon):
                    return True
            elif (1 == noPoints):
                _distSrc = norm(asarray(pointData.GetTuple3(0)) - asarray(srcPt))
                _distDst = norm(asarray(pointData.GetTuple3(0)) - asarray(dstPt))
                if (_distSrc < epsilon) or (_distDst < epsilon):
                    return True
        return False

    @staticmethod
    def mraycastObbTree(obbTree, srcPts, dstPts, pkFieldname=None):
        '''
        Excerpt from https://www.kitware.com/ray-casting-ray-tracing-with-vtk/

        the vtkOBBTree class, which generates an oriented bounding-box (OBB) 'tree'
        for a given geometry under a vtkPolyData object. Upon generation of this OBB 
        tree, the vtkOBBTree class allows us to perform intersection tests between
        the mesh and the lines of finite length, as well as intersection tests between
        different meshes. It can then return the point coordinates where intersections
        were detected, as well as the polydata cell IDs where the intersections occurred.
        '''
        assert isinstance(obbTree, vtkOBBTree), 'obbTree must be a vtkOBBTree!'
        assert len(srcPts) == len(dstPts), 'The number of origin points must be equal to the number of target points!'

        rays, hitPoints, hitDists, hitGids = [], [], [], []
        for i, srcPt in enumerate(srcPts):
            dstPt = dstPts[i]
            _points = vtkPoints()
            _cellIds = vtkIdList()
            code = obbTree.IntersectWithLine(srcPt, dstPt, _points, _cellIds)
            if (0 == code):
                # NO POINTS HIT
                ray, hitPoint, hitDist, hitGid = [srcPt, dstPt], dstPt, RayCastingIn3DLib.INFINITY, None
            else:
                pointData = _points.GetData()
                noPoints = pointData.GetNumberOfTuples()
                hitDist = RayCastingIn3DLib.INFINITY
                hitGid = None
                for idx in range(noPoints):
                    _tup = pointData.GetTuple3(idx)
                    _dist = norm(asarray(_tup) - asarray(srcPt))
                    if (_dist < hitDist):
                        ray, hitPoint, hitDist = [srcPt, _tup], _tup, _dist
                        if (0 < idx):
                            print('Surprise in RayCastingIn3DLib.raycast(...)!')
                        if pkFieldname is not None:
                            hitGid = _cellIds.GetId(idx)

            rays.append(ray)
            hitPoints.append(hitPoint)
            hitDists.append(hitDist)
            hitGids.append(hitGid)
        return rays, hitPoints, hitDists, hitGids

    @staticmethod
    def mraycast(unstructuredGrid, srcPts, dstPts, pkFieldname=None):
        obbTree = RayCastingIn3DLib.prepareVtkOBBTree(unstructuredGrid)
        return RayCastingIn3DLib.mraycastObbTree(obbTree, srcPts, dstPts, pkFieldname)

    @staticmethod
    def mraycast2D(unstructuredGrid, viewpoint, nRays=36):
        if isinstance(viewpoint, Point):
            viewpoint = viewpoint.coords[0]

        angularOffset, raylen = (2.0 * pi) / nRays, unstructuredGrid.length
        srcPts = [viewpoint] * nRays
        dstPts = [[
            viewpoint[0] + raylen * cos(angularOffset * i),
            viewpoint[1] + raylen * sin(angularOffset * i),
            0 if (2 == len(viewpoint)) else viewpoint[2],
            ] for i in range(nRays)]
        return RayCastingIn3DLib.mraycast(unstructuredGrid, srcPts, dstPts)

    @staticmethod
    def mraycast2DToGeoDataFrame(masks, viewpoint, nRays=36, crs='epsg:2154'):
        if isinstance(masks, (list, tuple, ndarray)):
            uGrid = ToUnstructuredGrid(masks).run()
        elif isinstance(masks, UnstructuredGrid):
            uGrid = masks
        else:
            raise IllegalArgumentTypeException(masks, 'UnstructuredGrid')
        rays, hitPoints, hitDists, hitGids = RayCastingIn3DLib.mraycast2D(uGrid, viewpoint, nRays)
        rows = []
        for ray, hitPoint, hitDist in zip(rays, hitPoints, hitDists):
            rows.append({
                'geometry': LineString(ray),
                'hitPoint': Point(hitPoint),
                'hitDist': hitDist
                })
        return GeoDataFrame(rows, crs=crs)

    @staticmethod
    def prepareVtkOBBTree(*args):
        '''
        Excerpt from https://www.kitware.com/ray-casting-ray-tracing-with-vtk/

        the vtkOBBTree class, which generates an oriented bounding-box (OBB) 'tree'
        for a given geometry under a vtkPolyData object. Upon generation of this OBB 
        tree, the vtkOBBTree class allows us to perform intersection tests between
        the mesh and the lines of finite length, as well as intersection tests between
        different meshes. It can then return the point coordinates where intersections
        were detected, as well as the polydata cell IDs where the intersections occurred.
        '''
        if all([isinstance(args[i], GeoDataFrame) for i in range(len(args))]):
            uGrid = ToUnstructuredGrid(args).run()
        elif (1 == len(args)) and isinstance(args[0], UnstructuredGrid):
            uGrid = args[0]
        else:
            raise IllegalArgumentTypeException(args, 'single UnstructuredGrid or list of GeoDataFrame')

        obbTree = vtkOBBTree()
        obbTree.SetDataSet(uGrid.extract_geometry())
        obbTree.BuildLocator()

        return obbTree
