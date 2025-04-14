'''
Created on 10 nov. 2023

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
from geopandas import overlay
from numpy import asarray, exp, zeros
from scipy.stats import kurtosis, skew
from shapely import LineString, Point, Polygon
from t4gpd.commons.Entropy import Entropy
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.raycasting.PanopticRaysLib import PanopticRaysLib


class RayCasting2DLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def get2DPanopticRaysGeoDataFrame(sensors, rayLength=100.0, nRays=64):
        return PanopticRaysLib.get2DGeoDataFrame(sensors, rayLength, nRays)

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

        viewpoint = viewpoint.centroid.coords[0][0:2]
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
    def multipleRayCast2D(buildings, rays, withIndices, threshold=1e-3):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, rays):
            raise Exception(
                "Illegal argument: buildings and rays are expected to share the same crs!")

        nRays = len(rays)
        rays = overlay(rays, buildings, how="difference", keep_geom_type=False)
        rays.geometry = rays.apply(lambda row: RayCasting2DLib.__keepTheAnchoredSegment(
            row.viewpoint, GeomLib.removeZCoordinate(row.geometry)), axis=1)
        rays = rays.loc[rays[~rays.geometry.apply(
            lambda geom: geom.is_empty)].index, :]
        # debug 10.11.2023
        rays = rays.loc[rays[rays.geometry.apply(
            lambda geom: geom.length > threshold)].index, :]
        isovRaysField = rays.dissolve(
            by="__VPT_ID__", as_index=False, aggfunc=list)
        isovRaysField.set_index("__VPT_ID__", drop=True, inplace=True)
        isovRaysField.index.name = None
        # isovRaysField.drop(columns=["__VPT_ID__"], inplace=True)
        for fieldname in isovRaysField.columns:
            if fieldname not in ["geometry", "__RAY_ID__"]:
                isovRaysField[fieldname] = isovRaysField[fieldname].apply(
                    lambda t: t[0])

        if (0 < len(isovRaysField)):
            isovRaysField["__ISOV_GEOM__"] = isovRaysField.apply(lambda row: RayCasting2DLib.__buildIsovist(
                nRays, row.viewpoint, row.__RAY_ID__, row.geometry), axis=1)

        if withIndices:
            isovRaysField = RayCasting2DLib.__addIndicesToIsovRaysField2D(
                nRays, isovRaysField)

        isovField = isovRaysField.copy(deep=True)

        # debug 20.08.2024
        isovField = isovField.set_geometry("__ISOV_GEOM__", crs=buildings.crs)
        isovField.drop(columns=["__RAY_ID__", "geometry"], inplace=True)
        isovField.rename_geometry("geometry", inplace=True)

        isovRaysField.drop(
            columns=["__RAY_ID__", "__ISOV_GEOM__"], inplace=True)

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
    def __addIndicesToIsovRaysField2D(nRays, isovRaysField, precision=1.0, base=exp(1)):
        isovRaysField["__RAY_LEN__"] = isovRaysField.apply(
            lambda row: RayCasting2DLib.__from2DRaysToRayLengths(nRays, row.__RAY_ID__, row.geometry), axis=1)

        isovRaysField = RayCasting2DLib.__add2DIndices(
            isovRaysField, precision, base)

        isovRaysField["__ISOV_CENTRE__"] = isovRaysField.__ISOV_GEOM__.apply(
            lambda geom: geom.centroid)

        isovRaysField["vect_drift"] = isovRaysField.apply(
            lambda row: None if row.__ISOV_CENTRE__.is_empty else LineString([
                row.viewpoint.centroid.coords[0][0:2], row.__ISOV_CENTRE__.coords[0]]), axis=1)
        isovRaysField["drift"] = isovRaysField.vect_drift.apply(
            lambda v: None if v is None else v.length)

        isovRaysField.drop(
            columns=["__RAY_LEN__", "__ISOV_CENTRE__"], inplace=True)
        return isovRaysField
