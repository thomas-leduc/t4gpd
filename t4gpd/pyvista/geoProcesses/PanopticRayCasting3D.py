'''
Created on 21 juil. 2022

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
from numpy import asarray
from shapely.geometry import MultiLineString, MultiPoint, Point
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.RayCasting3DLib import RayCasting3DLib
from t4gpd.pyvista.commons.RayCastingIn3DLib import RayCastingIn3DLib


class PanopticRayCasting3D(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, listOfMasks, maskPkFieldname=None, nrays=1000, method='MonteCarlo', maxRayLen=None,
                 showHitPoints=False, encode=True):
        '''
        Constructor
        '''
        assert isinstance(listOfMasks, (list, tuple)), 'listOfMasks must be a list of GeoDataFrames'
        assert all(isinstance(gdf, GeoDataFrame) for gdf in listOfMasks), 'listOfMasks must be a list of GeoDataFrames'

        if maskPkFieldname is not None:
            assert all((maskPkFieldname in gdf) for gdf in listOfMasks), f'{maskPkFieldname} must be a GeoDataFrame field name!'
        self.maskPkFieldname = maskPkFieldname

        masks = ToUnstructuredGrid(listOfMasks, fieldname=maskPkFieldname).run()
        # self.bounds = masks.bounds

        self.obbTree = RayCastingIn3DLib.prepareVtkOBBTree(masks)

        self.nrays = nrays
        self.method = method
        self.maxRayLen = masks.length if maxRayLen is None else maxRayLen

        if not ('MonteCarlo' == self.method):
            self.shootingDirs = RayCasting3DLib.preparePanopticRays(nrays, method)
            self.shootingDirs *= self.maxRayLen 

        self.showHitPoints = showHitPoints
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

        if ('MonteCarlo' == self.method):
            shootingDirs = RayCasting3DLib.preparePanopticRandomRays(self.nrays)
            shootingDirs *= self.maxRayLen 
        else:
            shootingDirs = self.shootingDirs

        srcPt = asarray(geom.coords[0])
        dstPts = srcPt + shootingDirs
        srcPts = srcPt.reshape(1, -1).repeat(len(dstPts), axis=0)

        rays, hitPoints, hitDists, hitGids = RayCastingIn3DLib.mraycastObbTree(
            self.obbTree, srcPts, dstPts, self.maskPkFieldname)

        # rays = PanopticRayCasting3D.__clipWithBounds(rays, self.bounds)

        if self.maskPkFieldname is None:
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
