'''
Created on 9 juin 2022

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
from geopandas.geodataframe import GeoDataFrame
from numpy import asarray, copy, dot
from numpy.random import shuffle
from shapely.geometry import MultiLineString, MultiPoint, Point
from sklearn.preprocessing import normalize
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.RayCastingIn3DLib import RayCastingIn3DLib


class RayCasting3D(AbstractGeoprocess):
    '''
    classdocs
    '''
    def __init__(self, gdfs, shootingDirs, viewpoints=None, normalFieldname=None,
                 pkFieldname=None, mc=None, maxRayLen=None, showHitPoints=False,
                 encode=False):
        '''
        Constructor
        '''
        assert isinstance(gdfs, (list, tuple)), 'gdfs must be a list of GeoDataFrames'
        assert all(isinstance(gdf, GeoDataFrame) for gdf in gdfs), 'gdfs must be a list of GeoDataFrames'

        self.shootingDirs = asarray(shootingDirs)
        assert 2 == self.shootingDirs.ndim, 'shootingDirs must be a list of 2D/3D vectors'
        self.shootingDirs = normalize(self.shootingDirs, norm='l2', copy=True) 

        assert (viewpoints is None) or isinstance(viewpoints, GeoDataFrame), 'viewpoints must be either None or a GeoDataFrame'
        assert (normalFieldname is None) or (normalFieldname in viewpoints), 'normalFieldname must be either None or a viewpoints field name'
        self.normalFieldname = normalFieldname

        if pkFieldname is not None:
            assert all((pkFieldname in gdf) for gdf in gdfs), f'{pkFieldname} must be a GeoDataFrame field name!'

        self.pkFieldname = pkFieldname
        '''
        https://kitware.github.io/vtk-examples/site/Python/
        https://pyscience.wordpress.com/2014/09/21/ray-casting-with-python-and-vtk-intersecting-linesrays-with-surface-meshes/

        Excerpt from https://www.kitware.com/ray-casting-ray-tracing-with-vtk/

        the vtkOBBTree class, which generates an oriented bounding-box (OBB) 'tree'
        for a given geometry under a vtkPolyData object. Upon generation of this OBB 
        tree, the vtkOBBTree class allows us to perform intersection tests between
        the mesh and the lines of finite length, as well as intersection tests between
        different meshes. It can then return the point coordinates where intersections
        were detected, as well as the polydata cell IDs where the intersections occurred.
        '''
        masks = ToUnstructuredGrid(gdfs, fieldname=pkFieldname).run()
        self.bounds = masks.bounds

        self.obbTree = RayCastingIn3DLib.prepareVtkOBBTree(masks)

        maxRayLen = masks.length if maxRayLen is None else maxRayLen
        self.shootingDirs *= maxRayLen 

        self.showHitPoints = showHitPoints
        assert (mc is None) or (0 <= mc <= 1.0), 'mc parameter must be either None or in the range 0 to 1'
        self.mc = mc
        self.encode = encode

    '''
    @staticmethod
    def __clipWithBounds(rays, bounds):
        _rays = GeoDataFrame(data=[{'geometry': MultiLineString(rays)}])
        _rays = _rays.explode(ignore_index=True)
        _rays = ToUnstructuredGrid([_rays]).run()
        _rays = _rays.clip_box(*bounds)
        _rays = [_rays.cell_points(i) for i in range(_rays.n_cells)]
        return _rays
    '''

    def runWithArgs(self, row):
        geom = row.geometry
        if not isinstance(geom, Point):
            raise IllegalArgumentTypeException(geom, 'GeoDataFrame of Point')

        shootingDirs = copy(self.shootingDirs)
        if self.mc is not None:
            shuffle(shootingDirs)
            shootingDirs = shootingDirs[0:int(self.mc * len(shootingDirs))]

        if self.normalFieldname is not None:
            normalVector = row[self.normalFieldname]
            normalVector = ArrayCoding.decode(normalVector) if isinstance(normalVector, str) else normalVector
            shootingDirs = shootingDirs[ dot(shootingDirs, normalVector) > 0 ]

        srcPt = asarray(geom.coords[0])
        dstPts = srcPt + shootingDirs
        srcPts = srcPt.reshape(1, -1).repeat(len(dstPts), axis=0)

        rays, hitPoints, hitDists, hitGids = RayCastingIn3DLib.mraycastObbTree(
            self.obbTree, srcPts, dstPts, self.pkFieldname)

        # rays = RayCasting3D.__clipWithBounds(rays, self.bounds)

        if self.pkFieldname is None:
            return {
                'geometry': MultiPoint(hitPoints) if (self.showHitPoints) else MultiLineString(rays),
                'n_rays': len(shootingDirs),
                'hitDists': ArrayCoding.encode(hitDists) if self.encode else hitDists,
                'inf_ratio': len([d for d in hitDists if (d == RayCastingIn3DLib.INFINITY)]) / len(hitDists)
                }

        return {
            'geometry': MultiPoint(hitPoints) if (self.showHitPoints) else MultiLineString(rays),
            'n_rays': len(shootingDirs),
            'hitDists': ArrayCoding.encode(hitDists) if self.encode else hitDists,
            'hitGids': ArrayCoding.encode(hitGids) if self.encode else hitGids,
            'inf_ratio': len([d for d in hitDists if (d == RayCastingIn3DLib.INFINITY)]) / len(hitDists)
            }
