'''
Created on 2 mai 2022

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
from numpy import cos, pi, sin, sqrt
from shapely.geometry import LineString, MultiLineString, Point
from shapely.ops import nearest_points
from shapely.prepared import prep
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class RayCasting3Lib(object):
    '''
    classdocs
    '''
    SQRT3DIV2 = sqrt(3) / 2
    DIVSQRT2 = 1 / sqrt(2)
    BASES = {
        12: [
            (1, 0), (SQRT3DIV2, 0.5), (0.5, SQRT3DIV2),
            (0, 1), (-0.5, SQRT3DIV2), (-SQRT3DIV2, 0.5),
            (-1, 0), (-SQRT3DIV2, -0.5), (-0.5, -SQRT3DIV2),
            (0, -1), (0.5, -SQRT3DIV2), (SQRT3DIV2, -0.5)
            ],
        8: [
            (1, 0), (DIVSQRT2, DIVSQRT2),
            (0, 1), (-DIVSQRT2, DIVSQRT2),
            (-1, 0), (-DIVSQRT2, -DIVSQRT2),
            (0, -1), (DIVSQRT2, -DIVSQRT2)
            ],
        6: [ (1, 0), (0.5, SQRT3DIV2), (-0.5, SQRT3DIV2), (-1, 0), (-0.5, -SQRT3DIV2), (0.5, -SQRT3DIV2) ],
        4: [ (1, 0), (0, 1), (-1, 0), (0, -1) ],
        3: [ (1, 0), (-0.5, SQRT3DIV2), (-0.5, -SQRT3DIV2) ],
        2: [ (1, 0), (-1, 0) ]
        }

    @staticmethod
    def areCovisibleIn2D(ptA, ptB, masks):
        # To avoid: "Inconsistent coordinate dimensionality"
        A = Point([ptA.x, ptA.y])
        B = Point([ptB.x, ptB.y])
        segm = LineString([A, B])

        psegm = prep(segm)
        hits = filter(psegm.intersects, masks.geometry)
        for maskGeom in hits:
            _geom = segm.intersection(maskGeom)
            _geom = _geom.geoms if GeomLib.isMultipart(_geom) else [_geom]
            for _g in _geom:
                if (not A.equals(_g)) and (not B.equals(_g)):
                    return False
        return True

    @staticmethod
    def areCovisibleIn3D(ptA, ptB, masks, maskElevationFieldname, masksSIdx=None):
        # if RayCasting3Lib.areCovisibleIn2D(ptA, ptB, masks):
        #     return True

        if masksSIdx is None:
            masksSIdx = masks.sindex

        # To avoid: "Inconsistent coordinate dimensionality"
        A = ptA if GeomLib.is3D(ptA) else GeomLib.forceZCoordinateToZ0(ptA, z0=0.0)
        B = ptB if GeomLib.is3D(ptB) else GeomLib.forceZCoordinateToZ0(ptB, z0=0.0)

        # SEGM [AB] MUST BE IN 2D (REGARDING INTERSECTION WITH 3D POLYGONS)
        segm2d = LineString([Point([A.x, A.y]), Point([B.x, B.y])])
        # alpha = arctan2(B.z - A.z, segm.length)
        alpha = (B.z - A.z) / segm2d.length

        # SELECTION OF A SUBSET OF MASKS
        collectionOfGeoms = []
        masksIds = masksSIdx.intersection(segm2d.bounds)
        for maskId in masksIds:
            row = masks.loc[maskId]
            collectionOfGeoms.append(
                GeomLib.forceZCoordinateToZ0(row.geometry, z0=row[maskElevationFieldname])
                )

        psegm = prep(segm2d)
        hits = filter(psegm.intersects, collectionOfGeoms)
        for maskGeom in hits:
            geom = segm2d.intersection(maskGeom)
            geom = geom.geoms if GeomLib.isMultipart(geom) else [geom]
            for g in geom:
                for c in g.coords:
                    p = Point(c)
                    if (not p.equals(A)):
                        beta = (p.z - A.z) / LineString([A, p]).length
                        if (beta >= alpha):
                            return False, segm2d
        return True, segm2d

    @staticmethod
    def __preparePanopticRays(n, i, angularOffset):
        for D in [12, 8, 6, 4, 3, 2]:
            if (0 == n % D):
                N = n // D
                if (0 == i % N):
                    # print(f'accel {D} pour {i}/{n}')
                    return RayCasting3Lib.BASES[D][i // N]
        return [float(cos(angularOffset * i)), float(sin(angularOffset * i))]

    @staticmethod
    def preparePanopticRays(nRays=64):
        angularOffset = (2.0 * pi) / nRays
        shootingDirs = [RayCasting3Lib.__preparePanopticRays(nRays, i, angularOffset) for i in range(nRays)]
        return shootingDirs

    @staticmethod
    def prepareOrientedRays(masks, viewPoint):
        _, nearestPoint, _ = GeomLib.getNearestFeature3(masks, viewPoint, buffDist=40.0)
        u = GeomLib.unitVector([viewPoint.x, viewPoint.y], [nearestPoint.x, nearestPoint.y])
        return [u, [-u[0], -u[1]]]

    @staticmethod
    def outdoorSingleRayCast2D(masks, viewPoint, shootingDir, rayLength=100.0):
        isAnInsidePoint = lambda point, polygon: ('0FFFFF212' == point.relate(polygon))

        # To avoid: "Inconsistent coordinate dimensionality"
        viewPoint = Point((viewPoint.x, viewPoint.y))
        remotePoint = Point((viewPoint.x + shootingDir[0] * rayLength, viewPoint.y + shootingDir[1] * rayLength))
        ray = LineString([viewPoint, remotePoint])

        hitPoint, hitDist = remotePoint, rayLength

        pray = prep(ray)
        hits = filter(pray.intersects, masks.geometry)
        for maskGeom in hits:
            # THE RAY STARTS FROM, HITS OR CROSSES THE BUILDING

            if (isAnInsidePoint(viewPoint, maskGeom)):
                # INDOOR VIEWPOINT
                return None, None, None

            _geom = ray.intersection(maskGeom)
            _geom = _geom.geoms if GeomLib.isMultipart(_geom) else [_geom]
            for _g in _geom:
                if (not viewPoint.equals(_g)) and (not _g.is_empty):
                    _, rp = nearest_points(viewPoint, _g)
                    _dist = viewPoint.distance(rp)
                    if (0.0 == _dist):
                        return LineString([viewPoint, viewPoint]), viewPoint, 0.0
                    elif (_dist < hitDist):
                        # To avoid: "Inconsistent coordinate dimensionality"
                        hitPoint, hitDist = Point((rp.x, rp.y)), _dist

        return LineString([viewPoint, hitPoint]), hitPoint, hitDist

    @staticmethod
    def outdoorMultipleRayCast2D(masks, viewPoint, shootingDirs, rayLength=100.0):
        if not isinstance(masks, GeoDataFrame):
            raise IllegalArgumentTypeException(masks, 'GeoDataFrame')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')

        rays, hitPoints, hitDists = [], [], []
        for shootingDir in shootingDirs:
            ray, hitPoint, hitDist = RayCasting3Lib.outdoorSingleRayCast2D(
                masks, viewPoint, shootingDir, rayLength)
            if not ray is None:
                rays.append(ray)
                hitPoints.append(hitPoint)
                hitDists.append(hitDist)

        return MultiLineString(rays), hitPoints, hitDists

    @staticmethod
    def outdoorSingleRayCast25D(masks, viewPoint, shootingDir, rayLength,
                                elevationFieldName, background, h0=0.0):
        # DEFAULT ALTITUDE OF THE VIEWPOINT
        if not viewPoint.has_z:
            viewPoint = Point([viewPoint.x, viewPoint.y, h0])

        remotePoint = Point((viewPoint.x + shootingDir[0] * rayLength, viewPoint.y + shootingDir[1] * rayLength, h0))
        ray = LineString([viewPoint, remotePoint])
        pray = prep(ray)

        anchorId = GeomLib.getAnchoringBuildingId3(viewPoint, masks)

        if anchorId is None:
            # ======================================================================
            # OUTDOOR VIEWPOINT
            hitPoint, hitDist, hitMask, hitHW = None, rayLength, None, 0.0

            # _masks = masks[pray.intersects(masks.geometry)].copy(deep=True)
            _masks = masks.loc[ masks.geometry.apply(lambda g: pray.intersects(g))]
            for _, mask in _masks.iterrows():
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
                if not hitPoint.has_z:
                    hitPoint = Point([hitPoint.x, hitPoint.y, h0])
                ray = LineString([viewPoint, hitPoint])
            else:
                hitPoint = remotePoint

        else:
            anchor = masks.loc[anchorId]
            if GeomLib.isAnIndoorPoint(viewPoint, masks):
                # ======================================================================
                # INDOOR VIEWPOINT
                ray, hitPoint, hitDist, hitMask, hitHW = None, None, 0.0, anchor, None

            elif GeomLib.isABorderPoint(viewPoint, masks):
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

                    # _masks = masks[pray.intersects(masks.geometry)].copy(deep=True)
                    _masks = masks.loc[ masks.geometry.apply(lambda g: pray.intersects(g))].copy(deep=True)
                    _masks.drop(index=anchorId, inplace=True)
                    for _, mask in _masks.iterrows():
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
                        if not hitPoint.has_z:
                            hitPoint = Point([hitPoint.x, hitPoint.y, h0])
                        ray = LineString([viewPoint, hitPoint])
                    else:
                        hitPoint = remotePoint

                else:
                    raise Exception('Unreachable instruction!')

            else:
                raise Exception('Unreachable instruction!')
        return [ray, hitPoint, hitDist, hitMask, hitHW]

    @staticmethod
    def outdoorMultipleRayCast25D(masks, viewPoint, shootingDirs, rayLength,
                                  elevationFieldName, background, h0=0.0):
        if not isinstance(masks, GeoDataFrame):
            raise IllegalArgumentTypeException(masks, 'GeoDataFrame')
        if not isinstance(viewPoint, Point):
            raise IllegalArgumentTypeException(viewPoint, 'Point')
        if elevationFieldName not in masks:
            raise Exception('%s is not a relevant field name!' % (elevationFieldName))

        # DEFAULT ALTITUDE OF THE VIEWPOINT
        if not viewPoint.has_z:
            viewPoint = Point([viewPoint.x, viewPoint.y, h0])

        rays, hitPoints, hitDists, hitMasks, hitHWs = [[], [], [], [], []]

        for shootingDir in shootingDirs:
            ray, hitPoint, hitDist, hitMask, hitHW = RayCasting3Lib.outdoorSingleRayCast25D(
                masks, viewPoint, shootingDir, rayLength, elevationFieldName, background, h0)
            if not ray is None:
                rays.append(ray)
                hitPoints.append(hitPoint)
            hitDists.append(hitDist)
            hitMasks.append(hitMask)
            hitHWs.append(hitHW)

        return MultiLineString(rays), hitPoints, hitDists, hitMasks, hitHWs
