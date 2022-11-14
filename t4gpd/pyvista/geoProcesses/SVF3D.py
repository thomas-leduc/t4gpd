'''
Created on 22 Aug. 2022

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
from numpy import asarray, dot, ones, where
from shapely.geometry import MultiLineString, Point
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.RayCasting3DLib import RayCasting3DLib
from t4gpd.pyvista.commons.RayCastingIn3DLib import RayCastingIn3DLib


class SVF3D(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, listOfMasks, nrays=1000, method='MonteCarlo'):
        '''
        Constructor
        '''
        assert isinstance(listOfMasks, (list, tuple)), 'listOfMasks must be a list of GeoDataFrames'
        assert all(isinstance(gdf, GeoDataFrame) for gdf in listOfMasks), 'listOfMasks must be a list of GeoDataFrames'
        masks = ToUnstructuredGrid(listOfMasks).run()
        self.maxRayLen = masks.length

        self.obbTree = RayCastingIn3DLib.prepareVtkOBBTree(masks)

        self.nrays = nrays
        self.main_direction = asarray([0, 0, 1])
        self.method = method

        self.shootingDirs, self.weights = None, None
        if not ('MonteCarlo' == self.method):
            # rays = RayCasting3DLib.preparePanopticRays(2 * nrays, method)
            # self.shootingDirs = self.maxRayLen * self.__selectUpwardFacingRays(rays)
            rays, weights = RayCasting3DLib.preparePanopticRaysAndWeights(2 * nrays, method)
            rays, weights = self.__selectUpwardFacingRaysAndWeights(rays, weights)
            self.shootingDirs = self.maxRayLen * rays
            self.weights = 2 * weights

    # def __selectUpwardFacingRays(self, rays):
    #     dotProducts = dot(rays, self.main_direction)
    #     indices = where(dotProducts >= 0)[0]
    #     return rays[indices,:]

    def __selectUpwardFacingRaysAndWeights(self, rays, weights):
        dotProducts = dot(rays, self.main_direction)
        indices = where(dotProducts >= 0)[0]
        return rays[indices,:], weights[indices]

    def runWithArgs(self, row):
        geom = row.geometry
        if not isinstance(geom, Point):
            raise IllegalArgumentTypeException(geom, 'GeoDataFrame of Point')

        if ('MonteCarlo' == self.method):
            rays = RayCasting3DLib.prepareOrientedRandomRays(
                self.nrays, self.main_direction, openness=90, method='MonteCarlo')
            shootingDirs = self.maxRayLen * rays
            weights = ones(shape=len(shootingDirs)) / len(shootingDirs)
        else:
            shootingDirs, weights = self.shootingDirs, self.weights

        srcPt = asarray(geom.coords[0])
        dstPts = srcPt + shootingDirs
        srcPts = srcPt.reshape(1, -1).repeat(len(dstPts), axis=0)

        rays, _, hitDists, _ = RayCastingIn3DLib.mraycastObbTree(self.obbTree, srcPts, dstPts)

        svf = 0
        for i, d in enumerate(hitDists):
            if (d == RayCastingIn3DLib.INFINITY):
                svf += weights[i]

        return {
            # 'geometry': MultiLineString(rays),
            'svf_old': len([d for d in hitDists if (d == RayCastingIn3DLib.INFINITY)]) / len(hitDists),
            'svf': svf
            }
