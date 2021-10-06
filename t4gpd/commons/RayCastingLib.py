'''
Created on 17 juin 2020

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
from numpy import cos, pi, sin

from geopandas.geodataframe import GeoDataFrame
from geopandas.sindex import SpatialIndex
from rtree.index import Index 
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.ops import nearest_points
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class RayCastingLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def preparePanopticRays(nRays=64):
        angularOffset = (2.0 * pi) / nRays
        shootingDirs = [[float(cos(angularOffset * i)), float(sin(angularOffset * i))] for i in range(nRays)]
        return shootingDirs

    @staticmethod
    def singleRayCast2D(masksGdf, masksSIdx, viewPoint, shootingDir, rayLength=100.0):
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (SpatialIndex, Index)):
            raise IllegalArgumentTypeException(masksSIdx, 'SpatialIndex or Index')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')
        
        remotePoint = Point((viewPoint.x + shootingDir[0] * rayLength, viewPoint.y + shootingDir[1] * rayLength))
        ray = LineString([viewPoint, remotePoint])
        
        hitPoint, hitDist, hitMask = [None, rayLength, None]

        masksIds = list(masksSIdx.intersection(ray.bounds))
        for maskId in masksIds:
            mask = masksGdf.loc[maskId]
            maskGeom = mask.geometry
            if ray.crosses(maskGeom):
                _tmp = maskGeom.intersection(ray)
                _, rp = nearest_points(viewPoint, _tmp)
                dist = viewPoint.distance(rp)
                if (dist < hitDist):
                    hitPoint, hitDist, hitMask = rp, dist, mask

        if hitPoint is not None:
            ray = LineString([viewPoint, hitPoint])
        else:
            hitPoint = remotePoint

        return [ray, hitPoint, hitDist, hitMask]

    @staticmethod
    def multipleRayCast2D(masksGdf, masksSIdx, viewPoint, shootingDirs, rayLength=100.0):
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (SpatialIndex, Index)):
            raise IllegalArgumentTypeException(masksSIdx, 'SpatialIndex or Index')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')

        rays, hitPoints, hitDists, hitMasks = [[], [], [], []]
        
        for shootingDir in shootingDirs:
            ray, hitPoint, hitDist, hitMask = RayCastingLib.singleRayCast2D(masksGdf, masksSIdx, viewPoint, shootingDir, rayLength)
            rays.append(ray)
            hitPoints.append(hitPoint)
            hitDists.append(hitDist)
            hitMasks.append(hitMask)

        return [MultiLineString(rays), Polygon(hitPoints), hitDists, hitMasks]
