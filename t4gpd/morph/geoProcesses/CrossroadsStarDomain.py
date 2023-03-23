'''
Created on 10 juin 2021

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
from geopandas import GeoDataFrame
from geopandas import clip
from shapely.geometry import box, MultiPolygon
from shapely.ops import unary_union
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.KernelLib import KernelLib
from t4gpd.commons.RayCasting3Lib import RayCasting3Lib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class CrossroadsStarDomain(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, buildings, nRays=64, maxRayLength=100, debug=False):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame')
        self.buildings = buildings
        # CLEAN GEOMETRIES
        self.buildings.geometry = self.buildings.geometry.apply(lambda g: g.buffer(0))
        # self.buildingsIdx = buildings.sindex

        # self.shootingDirs = RayCastingLib.preparePanopticRays(nRays)
        self.shootingDirs = RayCasting3Lib.preparePanopticRays(nRays)
        self.maxRayLength = maxRayLength
        self.debug = debug

    def __assessKernel(self, geom, r):
        if (self.minRayLength >= r):
            _kernel = _open_spaces = geom.buffer(self.minRayLength)
            if self.debug:
                self.debugList.append(_open_spaces)
                self.debugRayLens.append(round(self.minRayLength, 1))
            return _kernel
        
        _open_spaces = geom.buffer(r)

        _buildings = clip(self.buildings, box(*_open_spaces.bounds))
        if (0 == len(_buildings)):
            return _open_spaces
        _buildings = GeoDataFrame([{'geometry': unary_union(_buildings.geometry)}],
                                  crs=self.buildings.crs)
        _buildings = _buildings.explode(ignore_index=True)
        _buildings = _buildings[ ~_buildings.geometry.isna() ].copy(deep=True)
        _buildings.geometry = _buildings.geometry.apply(lambda g: g.convex_hull)
        _buildings = unary_union(_buildings.geometry)

        _open_spaces = _open_spaces.difference(_buildings)
        _kernel, flag = KernelLib.getKernel(_open_spaces)

        if self.debug:
            self.debugList.append(_open_spaces)
            self.debugRayLens.append(round(r, 1))

        if (flag and (geom.within(_kernel))):
            return _kernel

        return None

    def __assessKernelByDichotomy(self, geom, r1, r2):
        if (r2 - r1 < 1.0):
            if (0 < r1):
                return self.__assessKernel(geom, r1)
            return None

        r12 = (r1 + r2) / 2.0
        _kernel = self.__assessKernel(geom, r12)
        if (_kernel is None):
            return self.__assessKernelByDichotomy(geom, r1, r12)
        else:
            return self.__assessKernelByDichotomy(geom, r12, r2)

    def runWithArgs(self, row):
        geom = row.geometry.centroid

        if self.debug:
            self.debugList = []
            self.debugRayLens = []

        buffDist = 40.0
        # self.minRayLength, _, _ = GeomLib.getNearestFeature(
        #     self.buildings, self.buildingsIdx, geom, buffDist)
        self.minRayLength, _, _ = GeomLib.getNearestFeature3(
            self.buildings, geom, buffDist)

        # _, _, hitDists, _ = RayCastingLib.multipleRayCast2D(
        #     self.buildings, self.buildingsIdx, geom, self.shootingDirs, self.maxRayLength)
        _, _, hitDists = RayCasting3Lib.outdoorMultipleRayCast2D(
            self.buildings, geom, self.shootingDirs, self.maxRayLength)
        self.maxRayLength = max(hitDists)

        kernel = None
        if (0 < self.minRayLength):
            kernel = self.__assessKernelByDichotomy(geom, 0, self.maxRayLength)
        if kernel is None:
            kernel = geom

        if self.debug:
            return {
                'geometry': MultiPolygon(self.debugList),
                'RayLens': ArrayCoding.encode(self.debugRayLens)
                }

        return {
            'geometry': kernel,
            'MinLenRad': self.minRayLength,
            'MaxLenRad': self.maxRayLength,
            'kern_drift': geom.distance(kernel.centroid)
            }
