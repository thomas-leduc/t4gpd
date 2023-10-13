'''
Created on 24 jul. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame, overlay
from numpy import arange, asarray, cos, exp, pi, sin, stack, zeros
from scipy.stats import kurtosis, skew
from shapely import equals, LineString, MultiLineString, Point, Polygon
from shapely.affinity import translate
from shapely.ops import nearest_points
from t4gpd.commons.Entropy import Entropy
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.commons.SVFLib import SVFLib


class RayCasting4Lib(object):
    '''
    classdocs
    '''
    @staticmethod
    def get2DPanopticRaysGeoDataFrame(sensors, rayLength=100.0, nRays=64):
        angles = ((2.0 * pi) / nRays) * arange(nRays)
        shootingDirs = rayLength * stack([cos(angles), sin(angles)], axis=1)
        shootingDirs = MultiLineString(
            [LineString([(0, 0), xy]) for xy in shootingDirs])

        rays2D = sensors.copy(deep=True)
        rays2D["viewpoint"] = rays2D.geometry
        rays2D.geometry = rays2D.geometry.apply(
            lambda geom: geom.centroid)
        rays2D.geometry = rays2D.geometry.apply(
            lambda geom: translate(shootingDirs, xoff=geom.x, yoff=geom.y))
        rays2D = rays2D.explode(index_parts=True)
        rays2D = rays2D.reset_index(names=["__VPT_ID__", "__RAY_ID__"])
        return rays2D

    @staticmethod
    def get25DPanopticRaysGeoDataFrame(sensors, rayLength=100.0, nRays=64, h0=0.0):
        rays25D = RayCasting4Lib.get2DPanopticRaysGeoDataFrame(
            sensors, rayLength, nRays)
        rays25D.geometry = rays25D.apply(
            lambda row: GeomLib.forceZCoordinateToZ0(
                row.geometry, z0=GeomLib3D.centroid(
                    row.viewpoint).z if row.viewpoint.has_z else h0), axis=1)
        rays25D.viewpoint = rays25D.viewpoint.apply(
            lambda vp: GeomLib.forceZCoordinateToZ0(
                vp, z0=GeomLib3D.centroid(vp).z if vp.has_z else h0))
        return rays25D

    @staticmethod
    def __keepTheAnchoredSegment(sensor, segments):
        epsilon = 1e-3
        if isinstance(segments, (Point, LineString)):
            if (epsilon > sensor.distance(segments)):
                return segments
        else:
            for segment in segments.geoms:
                if (epsilon > sensor.distance(segment)):
                    return segment
        return LineString([])

    @staticmethod
    def __buildIsovist(nRays, viewpoint, ray_ids, mls):
        if not GeomLib.isMultipart(mls):
            return Polygon([])

        _ctrPts1 = [ls.coords[-1] for ls in mls.geoms]
        if (nRays == len(_ctrPts1)):
            return Polygon(_ctrPts1)

        viewpoint = viewpoint.coords[0][0:2]
        assert len(ray_ids) == len(_ctrPts1)
        assert ray_ids == sorted(ray_ids)
        _ctrPts2 = []
        for i, ray_id in enumerate(ray_ids):
            if (0 == i):
                if (0 != ray_id):
                    _ctrPts2.append(viewpoint)
                _ctrPts2.append(_ctrPts1[i])
            else:
                if (ray_ids[i-1]+1 < ray_id):
                    _ctrPts2.append(viewpoint)
                _ctrPts2.append(_ctrPts1[i])
        return Polygon(_ctrPts2)

    @staticmethod
    def multipleRayCast2D(buildings, rays, withIndices):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, rays):
            raise Exception(
                "Illegal argument: buildings and rays must share shames CRS!")

        nRays = len(rays)
        rays = overlay(rays, buildings, how="difference")
        rays.geometry = rays.apply(lambda row: RayCasting4Lib.__keepTheAnchoredSegment(
            row.viewpoint, GeomLib.removeZCoordinate(row.geometry)), axis=1)
        rays = rays.loc[rays[~rays.geometry.apply(
            lambda geom: geom.is_empty)].index, :]
        isovRaysField = rays.dissolve(
            by="__VPT_ID__", as_index=False, aggfunc=list)
        isovRaysField.drop(columns=["__VPT_ID__"], inplace=True)
        for fieldname in isovRaysField.columns:
            if fieldname not in ["geometry", "__RAY_ID__"]:
                isovRaysField[fieldname] = isovRaysField[fieldname].apply(
                    lambda t: t[0])

        if (0 < len(isovRaysField)):
            isovRaysField["__ISOV_GEOM__"] = isovRaysField.apply(lambda row: RayCasting4Lib.__buildIsovist(
                nRays, row.viewpoint, row.__RAY_ID__, row.geometry), axis=1)

        if withIndices:
            isovRaysField = RayCasting4Lib.addIndicesToIsovRaysField2D(
                nRays, isovRaysField)

        isovField = isovRaysField.copy(deep=True)
        if (0 < len(isovField)):
            isovField.geometry = isovField.__ISOV_GEOM__

        isovRaysField.drop(
            columns=["__RAY_ID__", "__ISOV_GEOM__"], inplace=True)
        isovField.drop(columns=["__RAY_ID__", "__ISOV_GEOM__"], inplace=True)

        return isovRaysField, isovField

    @staticmethod
    def __from2DRaysToRayLengths(nRays, ray_ids, mls):
        _raylens = asarray(
            [ray.length for ray in GeomLib.toListOfLineStrings(mls)])

        if (nRays == len(_raylens)):
            return _raylens

        raylens = zeros(nRays)
        for i, ray_id in enumerate(ray_ids):
            raylens[ray_id] = _raylens[i]
        return raylens

    @staticmethod
    def __add2DIndices(isovRaysField, precision=1.0, base=exp(1)):
        isovRaysField["w_mean"] = isovRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.mean()))
        isovRaysField["w_std"] = isovRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.std()))
        isovRaysField["w_kurtosis"] = isovRaysField.__RAY_LEN__.apply(
            lambda raylens: float(kurtosis(raylens, fisher=True, bias=True)))
        isovRaysField["w_skew"] = isovRaysField.__RAY_LEN__.apply(
            lambda raylens: float(skew(raylens)))
        isovRaysField["w_entropy"] = isovRaysField.__RAY_LEN__.apply(
            lambda raylens: Entropy.createFromDoubleValuesArray(
                raylens, precision).h(base)
        )
        return isovRaysField

    @staticmethod
    def addIndicesToIsovRaysField2D(nRays, isovRaysField, precision=1.0, base=exp(1)):
        isovRaysField["__RAY_LEN__"] = isovRaysField.apply(
            lambda row: RayCasting4Lib.__from2DRaysToRayLengths(nRays, row.__RAY_ID__, row.geometry), axis=1)

        isovRaysField = RayCasting4Lib.__add2DIndices(
            isovRaysField, precision, base)

        isovRaysField["__ISOV_CENTRE__"] = isovRaysField.__ISOV_GEOM__.apply(
            lambda geom: geom.centroid)

        isovRaysField["vect_drift"] = isovRaysField.apply(
            lambda row: None if row.__ISOV_CENTRE__.is_empty else LineString([
                row.viewpoint.coords[0][0:2], row.__ISOV_CENTRE__.coords[0]]), axis=1)
        isovRaysField["drift"] = isovRaysField.vect_drift.apply(
            lambda v: None if v is None else v.length)

        isovRaysField.drop(
            columns=["__RAY_LEN__", "__ISOV_CENTRE__"], inplace=True)
        return isovRaysField

    @staticmethod
    def __build_LineString(pA, pB):
        if (equals(pA, pB)) or (pA.is_empty) or (pB.is_empty):
            return LineString([])
        if (pA.has_z == pB.has_z):
            return LineString([pA, pB])
        return LineString([(pA.x, pA.y), (pB.x, pB.y)])

    @staticmethod
    def __keepTheLargestSolidAngle(sensor, masks):
        sensor = GeomLib3D.centroid(sensor)
        if isinstance(masks, (Point, LineString)):
            _, remotePoint = nearest_points(sensor, masks)
            # if equals(sensor, remotePoint):
            #     return LineString([])
            # return LineString([sensor, remotePoint])
            return RayCasting4Lib.__build_LineString(sensor, remotePoint)

        maxSolidAngle, maxMask = -float("inf"), None
        for mask in masks.geoms:
            h, w = mask.coords[0][2], sensor.distance(mask)
            if (0 == w):
                return LineString([])
            currSolidAngle = h / w
            if (currSolidAngle > maxSolidAngle):
                maxSolidAngle, maxMask = currSolidAngle, mask
        _, remotePoint = nearest_points(sensor, maxMask)

        # if equals(sensor, remotePoint):
        #     return LineString([])
        # return LineString([sensor, remotePoint])
        return RayCasting4Lib.__build_LineString(sensor, remotePoint)

    @staticmethod
    def __from25DRaysToRayLengths(nRays, rayLength, ray_ids, mls):
        _raylens = asarray(
            [ray.length for ray in GeomLib.toListOfLineStrings(mls)])

        if (nRays == len(_raylens)):
            return _raylens

        # raylens = asarray([rayLength for _ in range(nRays)])
        raylens = zeros(nRays)
        for i, ray_id in enumerate(ray_ids):
            raylens[ray_id] = _raylens[i]
        return raylens

    @staticmethod
    def __from25DRaysToRayAlts(nRays, ray_ids, mls):
        _rayalts = asarray(
            [ray.coords[-1][2] for ray in GeomLib.toListOfLineStrings(mls)])

        if (nRays == len(_rayalts)):
            return _rayalts

        # The altitude of the building adjacent to the viewpoint should be assigned here.
        rayalts = zeros(nRays)
        for i, ray_id in enumerate(ray_ids):
            rayalts[ray_id] = _rayalts[i]
        return rayalts

    @staticmethod
    def __from25DRaysToRayDeltaAlts(nRays, ray_ids, mls):
        _rayDeltaAlts = asarray(
            [max(ray.coords[-1][2]-ray.coords[0][2], 0) for ray in GeomLib.toListOfLineStrings(mls)])

        if (nRays == len(_rayDeltaAlts)):
            return _rayDeltaAlts

        # The altitude of the building adjacent to the viewpoint should be assigned here.
        rayDeltaAlts = zeros(nRays)
        for i, ray_id in enumerate(ray_ids):
            rayDeltaAlts[ray_id] = _rayDeltaAlts[i]
        return rayDeltaAlts

    @staticmethod
    def multipleRayCast25D(buildings, rays, nRays, rayLength, elevationFieldName, withIndices, h0=0.0):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, rays):
            raise Exception(
                "Illegal argument: buildings and rays must share shames CRS!")
        rays.geometry = rays.geometry.apply(lambda geom: GeomLib.forceZCoordinateToZ0(
            geom, z0=geom.coords[0][2] if geom.has_z else h0))

        smapRaysField = overlay(rays, buildings.geometry.to_frame(
        ), how="intersection", keep_geom_type=True)
        smapRaysField = smapRaysField.dissolve(by=["__VPT_ID__", "__RAY_ID__"], as_index=False, aggfunc={
                                               "gid": "first", "viewpoint": "first"})
        smapRaysField.geometry = smapRaysField.apply(lambda row: RayCasting4Lib.__keepTheLargestSolidAngle(
            row.viewpoint, row.geometry), axis=1)
        # smapRaysField.to_csv("/tmp/a.csv", index=False, sep=";")

        left = rays.set_index(["__VPT_ID__", "__RAY_ID__"], drop=False)
        left.drop(columns=["__VPT_ID__"], inplace=True)
        right = smapRaysField.set_index(
            ["__VPT_ID__", "__RAY_ID__"]).geometry.to_frame()
        smapRaysField = left.merge(
            right, how="outer", left_index=True, right_index=True)

        smapRaysField["geometry"] = smapRaysField.apply(
            lambda row: row.geometry_x if row.geometry_y is None else row.geometry_y, axis=1)
        smapRaysField.drop(columns=["geometry_x", "geometry_y"], inplace=True)
        smapRaysField = GeoDataFrame(smapRaysField, crs=buildings.crs)
        smapRaysField = smapRaysField.loc[smapRaysField[~smapRaysField.geometry.apply(
            lambda geom: geom.is_empty)].index, :]
        smapRaysField = smapRaysField.dissolve(
            by="__VPT_ID__", as_index=False, aggfunc=list)
        smapRaysField.drop(columns=["__VPT_ID__"], inplace=True)
        for fieldname in smapRaysField.columns:
            if fieldname not in ["geometry", "__RAY_ID__"]:
                smapRaysField[fieldname] = smapRaysField[fieldname].apply(
                    lambda t: t[0])

        if (0 < len(smapRaysField)):
            smapRaysField["__RAY_LEN__"] = smapRaysField.apply(
                lambda row: RayCasting4Lib.__from25DRaysToRayLengths(nRays, rayLength, row.__RAY_ID__, row.geometry), axis=1)
            smapRaysField["__RAY_ALT__"] = smapRaysField.apply(
                lambda row: RayCasting4Lib.__from25DRaysToRayAlts(nRays, row.__RAY_ID__, row.geometry), axis=1)
            smapRaysField["__RAY_DELTA_ALT__"] = smapRaysField.apply(
                lambda row: RayCasting4Lib.__from25DRaysToRayDeltaAlts(nRays, row.__RAY_ID__, row.geometry), axis=1)

            if withIndices:
                smapRaysField = RayCasting4Lib.addIndicesToSkyMapRaysField25D(
                    nRays, smapRaysField)

        return smapRaysField

    @staticmethod
    def addIndicesToSkyMapRaysField25D(nRays, smapRaysField, precision=1.0, base=exp(1)):
        smapRaysField["w_mean"] = smapRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.mean()))
        smapRaysField["w_std"] = smapRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.std()))
        smapRaysField["h_mean"] = smapRaysField.__RAY_ALT__.apply(
            lambda heights: float(heights.mean()))

        smapRaysField["h_over_w"] = smapRaysField.apply(
            lambda row: row.__RAY_DELTA_ALT__.mean() / (2 * row.w_mean), axis=1)
        smapRaysField["svf"] = smapRaysField.apply(
            lambda row: SVFLib.svf2018(row.__RAY_DELTA_ALT__, row.__RAY_LEN__), axis=1)

        return smapRaysField
