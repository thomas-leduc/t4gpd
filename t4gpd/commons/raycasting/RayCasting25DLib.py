'''
Created on 10 nov. 2023

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from geopandas import GeoDataFrame, overlay, sjoin_nearest
from numpy import asarray, full, median, min, nan, zeros
from shapely import LineString, Point
from shapely.ops import nearest_points
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.commons.SVFLib import SVFLib
from t4gpd.commons.raycasting.PanopticRaysLib import PanopticRaysLib


class RayCasting25DLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def get25DPanopticRaysGeoDataFrame(sensors, rayLength=100.0, nRays=64, h0=0.0):
        return PanopticRaysLib.get25DGeoDataFrame(sensors, rayLength, nRays, h0)

    @staticmethod
    def __build_LineString(pA, pB, threshold):
        if ((pA.is_empty) or (pB.is_empty) or (pA.distance(pB) <= threshold)):
            return LineString([])
        return LineString([pA, pB])

    @staticmethod
    def __keepTheLargestSolidAngle(sensor, rays, threshold):
        sensor = GeomLib3D.centroid(sensor)
        if isinstance(rays, (Point, LineString)):
            _, remotePoint = nearest_points(sensor, rays)
            # Debug 10.11.2023: nearest_points returns 2D points
            remotePoint = GeomLib.forceZCoordinateToZ0(
                remotePoint, z0=rays.coords[0][2])
            return RayCasting25DLib.__build_LineString(sensor, remotePoint, threshold)

        maxSolidAngle, maxMask = -float("inf"), None
        for mask in rays.geoms:
            h, w = mask.coords[0][2], sensor.distance(mask)
            if (0 == w):
                return LineString([])
            currSolidAngle = h / w
            if (currSolidAngle > maxSolidAngle):
                maxSolidAngle, maxMask = currSolidAngle, mask
        _, remotePoint = nearest_points(sensor, maxMask)
        # Debug 10.11.2023: nearest_points returns 2D points
        remotePoint = GeomLib.forceZCoordinateToZ0(
            remotePoint, z0=maxMask.coords[0][2])

        return RayCasting25DLib.__build_LineString(sensor, remotePoint, threshold)

    @staticmethod
    def __from25DRaysToRayLengths(gid, nRays, ray_ids, mls):
        try:
            _raylens = asarray(
                [ray.length for ray in GeomLib.toListOfLineStrings(mls)])

            if (nRays == len(_raylens)):
                return _raylens

            raylens = zeros(nRays)
            for i, ray_id in enumerate(ray_ids):
                raylens[ray_id] = _raylens[i]
            return raylens
        except Exception as e:
            print(f"__from25DRaysToRayLengths[{gid}]: {e}")
            return full(nRays, nan)

    @staticmethod
    def __from25DRaysToRayAlts(gid, nRays, ray_ids, mls, default_height):
        try:
            _rayalts = asarray(
                [ray.coords[-1][2] for ray in GeomLib.toListOfLineStrings(mls)])

            if (nRays == len(_rayalts)):
                return _rayalts

            # The altitude of the building adjacent to the viewpoint should be assigned here.
            # rayalts = zeros(nRays)
            rayalts = full(nRays, default_height)
            for i, ray_id in enumerate(ray_ids):
                rayalts[ray_id] = _rayalts[i]
            return rayalts
        except Exception as e:
            print(f"__from25DRaysToRayAlts[{gid}]: {e}")
            return full(nRays, nan)

    @staticmethod
    def __from25DRaysToRayDeltaAlts(gid, nRays, ray_ids, mls, default_height):
        try:
            _rays = GeomLib.toListOfLineStrings(mls)
            _rayDeltaAlts = asarray(
                [max(ray.coords[-1][2]-ray.coords[0][2], 0) for ray in _rays])

            if (nRays == len(_rayDeltaAlts)):
                return _rayDeltaAlts

            # The altitude of the building adjacent to the viewpoint should be assigned here.
            # rayDeltaAlts = zeros(nRays)
            alt0 = min([ray.coords[0][2] for ray in _rays], initial=0)
            rayDeltaAlts = full(nRays, default_height-alt0)
            for i, ray_id in enumerate(ray_ids):
                rayDeltaAlts[ray_id] = _rayDeltaAlts[i]
            return rayDeltaAlts
        except Exception as e:
            print(f"__from25DRaysToRayDeltaAlts[{gid}]: {e}")
            return full(nRays, nan)

    @staticmethod
    def multipleRayCast25D(viewpoints, buildings, rays, nRays, elevationFieldName,
                           withIndices, h0=0.0, threshold=1e-9):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, rays):
            raise Exception(
                "Illegal argument: buildings and rays are expected to share the same crs!")
        # rays.to_csv("/tmp/1.csv", index=False) # DEBUG

        rays.geometry = rays.geometry.apply(lambda geom: GeomLib.forceZCoordinateToZ0(
            geom, z0=geom.coords[0][2] if geom.has_z else h0))

        smapRaysField = overlay(rays, buildings[["geometry", elevationFieldName]],
                                how="intersection", keep_geom_type=True)

        if (0 == len(smapRaysField)):
            smapRaysField = rays.set_index("__VPT_ID__", drop=True).set_index(
                "__RAY_ID__", append=True, drop=False)
            smapRaysField["__HAUTEUR_VP__"] = None
        else:
            # Debug 25.03.2024
            smapRaysField.geometry = smapRaysField.apply(
                lambda row: GeomLib.forceZCoordinateToZ0(
                    row.geometry, row[elevationFieldName]),
                axis=1)
            # smapRaysField.to_csv("/tmp/2.csv") # DEBUG

            # Debug 06.05.2024
            # smapRaysField = smapRaysField.dissolve(
            #     by=["__VPT_ID__", "__RAY_ID__"], as_index=False, aggfunc={
            #     "gid": "first", "viewpoint": "first"})
            smapRaysField = smapRaysField.dissolve(
                by=["__VPT_ID__", "__RAY_ID__"], as_index=False, aggfunc="first")
            # smapRaysField.to_csv("/tmp/3.csv") # DEBUG
            smapRaysField.geometry = smapRaysField.apply(lambda row: RayCasting25DLib.__keepTheLargestSolidAngle(
                row.viewpoint, row.geometry, threshold), axis=1)
            # smapRaysField.to_csv("/tmp/31.csv") # DEBUG

            left = rays.set_index(["__VPT_ID__", "__RAY_ID__"], drop=False)
            left.drop(columns=["__VPT_ID__"], inplace=True)
            # left.to_csv("/tmp/32.csv") # DEBUG
            right = smapRaysField.set_index(
                ["__VPT_ID__", "__RAY_ID__"]).geometry.to_frame()
            # right.to_csv("/tmp/33.csv") # DEBUG
            smapRaysField = left.merge(
                right, how="left", left_index=True, right_index=True)
            # smapRaysField.to_csv("/tmp/34.csv") # DEBUG

            smapRaysField["geometry"] = smapRaysField.apply(
                lambda row: row.geometry_x if row.geometry_y is None else row.geometry_y, axis=1)
            smapRaysField.drop(
                columns=["geometry_x", "geometry_y"], inplace=True)
            # Debug 20.08.2024
            smapRaysField = GeoDataFrame(smapRaysField).set_crs(
                buildings.crs, allow_override=True)

            # Retrieve the heights of buildings near problematic sensors
            # Debug 25.03.2024
            indices1 = smapRaysField[smapRaysField.geometry.apply(
                lambda geom: geom.is_empty)].index
            ids1 = smapRaysField.loc[indices1, "gid"].unique()
            smapRaysField.drop(index=indices1, inplace=True)

            viewpoints2 = viewpoints.loc[viewpoints.gid.isin(ids1), [
                "gid", "geometry"]]
            viewpoints2 = sjoin_nearest(
                viewpoints2, buildings[["geometry", elevationFieldName]])
            viewpoints2 = viewpoints2[["gid", elevationFieldName]].groupby(
                by="gid").agg("mean").to_dict("index")
            viewpoints2 = {
                key: viewpoints2[key][elevationFieldName] for key in viewpoints2.keys()}
            # FROM: ...apply(lambda row: ... if ... else None)
            # TO: ...apply(lambda row: ... if ... else h0)
            # Debug 30.04.2024
            smapRaysField["__HAUTEUR_VP__"] = smapRaysField.apply(
                lambda row: viewpoints2[row.gid] if row.gid in viewpoints2 else h0,
                axis=1)
        # smapRaysField.to_csv("/tmp/4.csv") # DEBUG

        # Debug 06.05.2024
        # smapRaysField = smapRaysField.dissolve(
        #     by="__VPT_ID__", as_index=False, aggfunc={
        #         "__RAY_ID__": list, "gid": "first", "viewpoint": "first", "__HAUTEUR_VP__": "first"})
        aggfunc = dict({"__RAY_ID__": list})
        for f in smapRaysField.columns:
            if f not in ["__VPT_ID__", "__RAY_ID__", "geometry"]:
                aggfunc[f] = "first"
        smapRaysField = smapRaysField.dissolve(
            by="__VPT_ID__", as_index=False, aggfunc=aggfunc)
        # smapRaysField.drop(columns=["__VPT_ID__"], inplace=True)
        # smapRaysField.to_csv("/tmp/5.csv") # DEBUG

        if (0 < len(smapRaysField)):
            smapRaysField["__RAY_LEN__"] = smapRaysField.apply(
                lambda row: RayCasting25DLib.__from25DRaysToRayLengths(row.__VPT_ID__, nRays, row.__RAY_ID__, row.geometry), axis=1)
            smapRaysField["__RAY_ALT__"] = smapRaysField.apply(
                lambda row: RayCasting25DLib.__from25DRaysToRayAlts(row.__VPT_ID__, nRays, row.__RAY_ID__, row.geometry, row.__HAUTEUR_VP__), axis=1)
            smapRaysField["__RAY_DELTA_ALT__"] = smapRaysField.apply(
                lambda row: RayCasting25DLib.__from25DRaysToRayDeltaAlts(row.__VPT_ID__, nRays, row.__RAY_ID__, row.geometry, row.__HAUTEUR_VP__), axis=1)

            if withIndices:
                smapRaysField = RayCasting25DLib.__addIndicesToSkyMapRaysField25D(
                    smapRaysField)

        smapRaysField.drop(columns=["__VPT_ID__"], inplace=True)
        # smapRaysField.to_csv("/tmp/6.csv") # DEBUG

        return smapRaysField

    @staticmethod
    def __addIndicesToSkyMapRaysField25D(smapRaysField):
        smapRaysField["w_mean"] = smapRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.mean()))
        smapRaysField["w_median"] = smapRaysField.__RAY_LEN__.apply(
            lambda raylens: float(median(raylens)))
        smapRaysField["w_min"] = smapRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.min()))
        smapRaysField["w_std"] = smapRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.std()))
        smapRaysField["h_mean"] = smapRaysField.__RAY_ALT__.apply(
            lambda heights: float(heights.mean()))

        smapRaysField["h_over_w"] = smapRaysField.apply(
            lambda row: row.__RAY_DELTA_ALT__.mean() / (2 * row.w_mean), axis=1)
        smapRaysField["svf"] = smapRaysField.apply(
            lambda row: SVFLib.svf2018(row.__RAY_DELTA_ALT__, row.__RAY_LEN__), axis=1)

        return smapRaysField
