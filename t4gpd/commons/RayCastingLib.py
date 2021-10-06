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
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import nearest_points, linemerge
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class RayCastingLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def prepareOrientedRays(masksGdf, masksSIdx, viewPoint):
        _, nearestPoint, _ = GeomLib.getNearestFeature(
            masksGdf, masksSIdx, viewPoint, buffDist=40.0)
        u = GeomLib.unitVector([viewPoint.x, viewPoint.y], [nearestPoint.x, nearestPoint.y])
        return [u, [-u[0], -u[1]]]

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

        # TL. 23.02.2021
        # To avoid: "Inconsistent coordinate dimensionality"
        viewPoint = Point((viewPoint.x, viewPoint.y))
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
    def singleRayCast25D(masksGdf, masksSIdx, viewPoint, shootingDir, rayLength,
                         elevationFieldName, background):
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (SpatialIndex, Index)):
            raise IllegalArgumentTypeException(masksSIdx, 'SpatialIndex or Index')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')
        if elevationFieldName not in masksGdf:
            raise Exception('%s is not a relevant field name!' % (elevationFieldName))

        # TL. 23.02.2021
        # To avoid: "Inconsistent coordinate dimensionality"
        viewPoint = Point((viewPoint.x, viewPoint.y))
        remotePoint = Point((viewPoint.x + shootingDir[0] * rayLength, viewPoint.y + shootingDir[1] * rayLength))
        ray = LineString([viewPoint, remotePoint])

        hitPoint, hitDist, hitMask, hitHW = [None, rayLength, None, 0]

        masksIds = list(masksSIdx.intersection(ray.bounds))
        for maskId in masksIds:
            mask = masksGdf.loc[maskId]
            maskGeom = mask.geometry
            if ray.crosses(maskGeom):
                _tmp = maskGeom.intersection(ray)
                _, rp = nearest_points(viewPoint, _tmp)
                height, dist = mask[elevationFieldName], viewPoint.distance(rp)
                hw = height / dist
                if background and (hitHW < hw):
                    hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw
                elif (not background) and (dist < hitDist):
                    hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw

        if hitPoint is not None:
            ray = LineString([viewPoint, hitPoint])
        else:
            hitPoint = remotePoint

        return [ray, hitPoint, hitDist, hitMask, hitHW]

    @staticmethod
    def singleRayCastOnTopOfRoof(masksGdf, masksSIdx, viewPoint, shootingDir, rayLength,
                                 h0, elevationFieldName, background):
        
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (SpatialIndex, Index)):
            raise IllegalArgumentTypeException(masksSIdx, 'SpatialIndex or Index')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')
        if elevationFieldName not in masksGdf:
            raise Exception('%s is not a relevant field name!' % (elevationFieldName))

        # TL. 23.02.2021
        # To avoid: "Inconsistent coordinate dimensionality"
        viewPoint = Point((viewPoint.x, viewPoint.y))
        remotePoint = Point((viewPoint.x + shootingDir[0] * rayLength, viewPoint.y + shootingDir[1] * rayLength))
        ray = LineString([viewPoint, remotePoint])

        hitPoint, hitDist, hitMask, hitHW = [None, rayLength, None, 0]

        masksIds = list(masksSIdx.intersection(ray.bounds))
        for maskId in masksIds:
            mask = masksGdf.loc[maskId]
            maskGeom = mask.geometry
            if ray.crosses(maskGeom):
                _tmp = maskGeom.intersection(ray)
                _, rp = nearest_points(viewPoint, _tmp)
                height, dist = mask[elevationFieldName], viewPoint.distance(rp)
                hw = (height - h0) / dist
                if background and (hitHW < hw):
                    hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw
                elif (not background) and (dist < hitDist) and (0 < hw):
                    hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw

        if hitPoint is not None:
            ray = LineString([viewPoint, hitPoint])
        else:
            hitPoint = remotePoint

        return [ray, hitPoint, hitDist, hitMask, hitHW]

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

        return [MultiLineString(rays), hitPoints, hitDists, hitMasks]

    @staticmethod
    def multipleRayCast25D(masksGdf, masksSIdx, viewPoint, shootingDirs, rayLength,
                           elevationFieldName, background):
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (SpatialIndex, Index)):
            raise IllegalArgumentTypeException(masksSIdx, 'SpatialIndex or Index')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')
        if elevationFieldName not in masksGdf:
            raise Exception('%s is not a relevant field name!' % (elevationFieldName))

        rays, hitPoints, hitDists, hitMasks, hitHWs = [[], [], [], [], []]

        for shootingDir in shootingDirs:
            ray, hitPoint, hitDist, hitMask, hitHW = RayCastingLib.singleRayCast25D(
                masksGdf, masksSIdx, viewPoint, shootingDir, rayLength,
                elevationFieldName, background)
            rays.append(ray)
            hitPoints.append(hitPoint)
            hitDists.append(hitDist)
            hitMasks.append(hitMask)
            hitHWs.append(hitHW)

        return [MultiLineString(rays), hitPoints, hitDists, hitMasks, hitHWs]

    @staticmethod
    def multipleRayCastOnTopOfRoof(masksGdf, masksSIdx, viewPoint, shootingDirs,
                                   rayLength, enclosingFeatures, elevationFieldName,
                                   background):
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (SpatialIndex, Index)):
            raise IllegalArgumentTypeException(masksSIdx, 'SpatialIndex or Index')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')
        if elevationFieldName not in masksGdf:
            raise Exception('%s is not a relevant field name!' % (elevationFieldName))

        rays, hitPoints, hitDists, hitMasks, hitHWs = [[], [], [], [], []]
        h0 = min([f[elevationFieldName] for f in enclosingFeatures])

        for shootingDir in shootingDirs:
            ray, hitPoint, hitDist, hitMask, hitHW = RayCastingLib.singleRayCastOnTopOfRoof(
                masksGdf, masksSIdx, viewPoint, shootingDir, rayLength, h0,
                elevationFieldName, background)
            rays.append(ray)
            hitPoints.append(hitPoint)
            hitDists.append(hitDist)
            hitMasks.append(hitMask)
            hitHWs.append(hitHW)

        return [MultiLineString(rays), hitPoints, hitDists, hitMasks, hitHWs]

    @staticmethod
    def assessStreetWidth(masksGdf, masksSIdx, viewPoint, rayLength=100.0):
        if GeomLib.isAnIndoorPoint(viewPoint, masksGdf, masksSIdx):
            return None, -1, [-1, -1]

        _shootingDirs = RayCastingLib.prepareOrientedRays(
            masksGdf, masksSIdx, viewPoint)
        rays, _, hitDists, _ = RayCastingLib.multipleRayCast2D(
            masksGdf, masksSIdx, viewPoint, _shootingDirs, rayLength)
        return linemerge(rays), sum(hitDists), hitDists
