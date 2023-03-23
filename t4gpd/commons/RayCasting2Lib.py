'''
Created on 8 avr. 2022

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
from geopandas.sindex import PyGEOSSTRTreeIndex, SpatialIndex
from numpy import arctan2, cos, pi, sin
from rtree.index import Index 
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import nearest_points
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class RayCasting2Lib(object):
    '''
    classdocs
    '''

    @staticmethod
    def areCovisible(ptA, ptB, masksGdf, maskElevationFieldname, masksSIdx):
        # To avoid: "Inconsistent coordinate dimensionality"
        A = ptA if GeomLib.is3D(ptA) else GeomLib.forceZCoordinateToZ0(ptA, z0=0.0)
        B = ptB if GeomLib.is3D(ptB) else GeomLib.forceZCoordinateToZ0(ptB, z0=0.0)
        # segm = LineString([Point((ptA.x, ptA.y)), Point((ptB.x, ptB.y))])
        segm = LineString([A, B])
        alpha = arctan2(B.z - A.z, segm.length)

        masksIds = masksSIdx.intersection(segm.bounds)
        for maskId in masksIds:
            mask = masksGdf.loc[maskId]
            maskGeom = mask.geometry
            maskElevation = mask[maskElevationFieldname]

            if segm.intersects(maskGeom):
                tmpGeom = maskGeom.intersection(segm)
                gc = tmpGeom.geoms if GeomLib.isMultipart(tmpGeom) else [tmpGeom]
                for geom in gc:
                    for vertex in geom.coords:
                        hitPoint = Point(vertex)
                        _dist = A.distance(hitPoint)
                        _angle = arctan2(maskElevation - A.z, _dist)
                        if (_angle >= alpha):
                            return False, segm
        return True, segm

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
    def outdoorSingleRayCast2D(masksGdf, masksSIdx, viewPoint, shootingDir, rayLength=100.0): 
        # TL. 23.02.2021
        # To avoid: "Inconsistent coordinate dimensionality"
        viewPoint = Point((viewPoint.x, viewPoint.y))
        remotePoint = Point((viewPoint.x + shootingDir[0] * rayLength, viewPoint.y + shootingDir[1] * rayLength))
        ray = LineString([viewPoint, remotePoint])

        anchorId = GeomLib.getAnchoringBuildingId(viewPoint, masksGdf, masksSIdx)

        if anchorId is None:
            # ======================================================================
            # OUTDOOR VIEWPOINT
            hitPoint, hitDist, hitMask = None, rayLength, None

            masksIds = list(masksSIdx.intersection(ray.bounds))
            for maskId in masksIds:
                mask = masksGdf.loc[maskId]
                maskGeom = mask.geometry

                # if (ray.touches(maskGeom) or ray.crosses(maskGeom)):
                if (ray.crosses(maskGeom)):
                    # THE RAY HITS OR CROSSES THE BUILDING
                    _tmp = maskGeom.intersection(ray)
                    _, rp = nearest_points(viewPoint, _tmp)
                    dist = viewPoint.distance(rp)
                    if (dist < hitDist):
                        hitPoint, hitDist, hitMask = rp, dist, mask

            if hitPoint is not None:
                ray = LineString([viewPoint, hitPoint])
            else:
                hitPoint = remotePoint

        else:
            if GeomLib.isAnIndoorPoint(viewPoint, masksGdf):
                # ======================================================================
                # INDOOR VIEWPOINT
                ray, hitPoint, hitDist, hitMask = None, None, 0.0, anchorId

            elif GeomLib.isABorderPoint(viewPoint, masksGdf):
                # ======================================================================
                # VIEWPOINT ON A WALL
                buildingGeom = masksGdf.loc[anchorId].geometry
                _relate = ray.relate(buildingGeom)

                if (_relate in ['1FF00F212', 'F1FF0F212', 'F1FF0F212']):
                    # THE RAY GOES ALONG OR INTO THE "ANCHORING" BUILDING
                    ray, hitPoint, hitDist, hitMask = None, None, 0.0, anchorId

                elif ('FF1F00212' == _relate):
                    # THE RAY MOVES AWAY FROM THE "ANCHORING" BUILDING
                    hitPoint, hitDist, hitMask = None, rayLength, None

                    masksIds = list(masksSIdx.intersection(ray.bounds))
                    masksIds.remove(anchorId)
                    for maskId in masksIds:
                        mask = masksGdf.loc[maskId]
                        maskGeom = mask.geometry

                        if (ray.touches(maskGeom) or ray.crosses(maskGeom)):
                            # THE RAY HITS OR CROSSES THE "NON-ANCHORING" BUILDING
                            _tmp = maskGeom.intersection(ray)
                            _, rp = nearest_points(viewPoint, _tmp)
                            dist = viewPoint.distance(rp)
                            if (dist < hitDist):
                                hitPoint, hitDist, hitMask = rp, dist, mask

                    if hitPoint is not None:
                        ray = LineString([viewPoint, hitPoint])
                    else:
                        hitPoint = remotePoint

                else:
                    raise Exception('Unreachable instruction!')

            else:
                raise Exception('Unreachable instruction!')
        return [ray, hitPoint, hitDist, hitMask]

    @staticmethod
    def outdoorSingleRayCast25D(masksGdf, masksSIdx, viewPoint, shootingDir, rayLength,
                                elevationFieldName, background, h0=0.0):
        # DEFAULT ALTITUDE OF THE VIEWPOINT
        h0 = viewPoint.z if (viewPoint.has_z) else 1.6

        # TL. 23.02.2021
        # To avoid: "Inconsistent coordinate dimensionality"
        viewPoint = Point((viewPoint.x, viewPoint.y, h0))
        remotePoint = Point((viewPoint.x + shootingDir[0] * rayLength, viewPoint.y + shootingDir[1] * rayLength, h0))
        ray = LineString([viewPoint, remotePoint])

        anchorId = GeomLib.getAnchoringBuildingId(viewPoint, masksGdf, masksSIdx)

        if anchorId is None:
            # ======================================================================
            # OUTDOOR VIEWPOINT
            hitPoint, hitDist, hitMask, hitHW = None, rayLength, None, 0.0

            masksIds = list(masksSIdx.intersection(ray.bounds))
            for maskId in masksIds:
                mask = masksGdf.loc[maskId]
                maskGeom = mask.geometry

                # if (ray.touches(maskGeom) or ray.crosses(maskGeom)):
                if (ray.crosses(maskGeom)):
                    # THE RAY HITS OR CROSSES THE BUILDING
                    _tmp = maskGeom.intersection(ray)
                    _, rp = nearest_points(viewPoint, _tmp)
                    height, dist = mask[elevationFieldName], viewPoint.distance(rp)
                    hw = (height - h0) / dist
                    if background and (hitHW < hw):
                        hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw
                    elif (not background) and (dist < hitDist):
                        hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw

            if hitPoint is not None:
                ray = LineString([viewPoint, hitPoint])
            else:
                hitPoint = remotePoint

        else:
            anchor = masksGdf.loc[anchorId]
            if GeomLib.isAnIndoorPoint(viewPoint, masksGdf):
                # ======================================================================
                # INDOOR VIEWPOINT
                ray, hitPoint, hitDist, hitMask, hitHW = None, None, 0.0, anchor, None

            elif GeomLib.isABorderPoint(viewPoint, masksGdf):
                # ======================================================================
                # VIEWPOINT ON A WALL
                buildingGeom = anchor.geometry
                _relate = ray.relate(buildingGeom)

                if (_relate in ['1FF00F212', 'F1FF0F212', 'F1FF0F212', 'F11F00212', '101F00212']):
                    # THE RAY GOES ALONG OR INTO THE "ANCHORING" BUILDING
                    ray, hitPoint, hitDist, hitMask, hitHW = None, None, 0.0, anchor, None

                elif ('FF1F00212' == _relate):
                    # THE RAY MOVES AWAY FROM THE "ANCHORING" BUILDING
                    hitPoint, hitDist, hitMask, hitHW = None, rayLength, None, 0.0

                    masksIds = list(masksSIdx.intersection(ray.bounds))
                    masksIds.remove(anchorId)
                    for maskId in masksIds:
                        mask = masksGdf.loc[maskId]
                        maskGeom = mask.geometry

                        if (ray.touches(maskGeom) or ray.crosses(maskGeom)):
                            # THE RAY HITS OR CROSSES THE "NON-ANCHORING" BUILDING
                            _tmp = maskGeom.intersection(ray)
                            _, rp = nearest_points(viewPoint, _tmp)
                            height, dist = mask[elevationFieldName], viewPoint.distance(rp)
                            hw = (height - h0) / dist
                            if background and (hitHW < hw):
                                hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw
                            elif (not background) and (dist < hitDist):
                                hitPoint, hitDist, hitMask, hitHW = rp, dist, mask, hw

                    if hitPoint is not None:
                        ray = LineString([viewPoint, hitPoint])
                    else:
                        hitPoint = remotePoint

                else:
                    raise Exception('Unreachable instruction!')

            else:
                raise Exception('Unreachable instruction!')
        return [ray, hitPoint, hitDist, hitMask, hitHW]

    @staticmethod
    def outdoorMultipleRayCast2D(masksGdf, masksSIdx, viewPoint, shootingDirs, rayLength=100.0):
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (Index, PyGEOSSTRTreeIndex, SpatialIndex)):
            raise IllegalArgumentTypeException(masksSIdx, 'Index, PyGEOSSTRTreeIndex or SpatialIndex')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')

        rays, hitPoints, hitDists, hitMasks = [[], [], [], []]

        for shootingDir in shootingDirs:
            ray, hitPoint, hitDist, hitMask = RayCasting2Lib.outdoorSingleRayCast2D(
                masksGdf, masksSIdx, viewPoint, shootingDir, rayLength)
            if not ray is None:
                rays.append(ray)
                hitPoints.append(hitPoint)
            hitDists.append(hitDist)
            hitMasks.append(hitMask)

        return [MultiLineString(rays), hitPoints, hitDists, hitMasks]

    @staticmethod
    def outdoorMultipleRayCast25D(masksGdf, masksSIdx, viewPoint, shootingDirs, rayLength,
                                  elevationFieldName, background, h0=0.0):
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        if not isinstance(masksSIdx, (Index, PyGEOSSTRTreeIndex, SpatialIndex)):
            raise IllegalArgumentTypeException(masksSIdx, 'Index, PyGEOSSTRTreeIndex or SpatialIndex')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')
        if elevationFieldName not in masksGdf:
            raise Exception('%s is not a relevant field name!' % (elevationFieldName))

        rays, hitPoints, hitDists, hitMasks, hitHWs = [[], [], [], [], []]

        for shootingDir in shootingDirs:
            ray, hitPoint, hitDist, hitMask, hitHW = RayCasting2Lib.outdoorSingleRayCast25D(
                masksGdf, masksSIdx, viewPoint, shootingDir, rayLength,
                elevationFieldName, background, h0)
            if not ray is None:
                rays.append(ray)
                hitPoints.append(hitPoint)
            hitDists.append(hitDist)
            hitMasks.append(hitMask)
            hitHWs.append(hitHW)

        return [MultiLineString(rays), hitPoints, hitDists, hitMasks, hitHWs]
