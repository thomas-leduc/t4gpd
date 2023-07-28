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
from numpy import arange, asarray, cos, exp, pi, sin, stack
from scipy.stats import kurtosis, skew
from shapely import equals, LineString, MultiLineString, Point, Polygon
from shapely.affinity import translate
from shapely.ops import nearest_points
from t4gpd.commons.Entropy import Entropy
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
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
            lambda geom: translate(shootingDirs, xoff=geom.x, yoff=geom.y))
        rays2D = rays2D.explode(index_parts=True)
        rays2D = rays2D.reset_index(names=["__VPT_ID__", "__RAY_ID__"])
        return rays2D

    @staticmethod
    def get25DPanopticRaysGeoDataFrame(sensors, rayLength=100.0, nRays=64, h0=0.0):
        rays25D = RayCasting4Lib.get2DPanopticRaysGeoDataFrame(
            sensors, rayLength, nRays)
        rays25D.geometry = rays25D.apply(lambda row: GeomLib.forceZCoordinateToZ0(
            row.geometry, z0=row.viewpoint.z if row.viewpoint.has_z else h0), axis=1)
        rays25D.viewpoint = rays25D.viewpoint.apply(lambda vp: GeomLib.forceZCoordinateToZ0(
            vp, z0=vp.z if vp.has_z else h0))
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
        # return LineString([sensor, sensor])
        return LineString([])

    @staticmethod
    def multipleRayCast2D(buildings, rays):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, rays):
            raise Exception(
                "Illegal argument: buildings and rays must share shames CRS!")

        rays = overlay(rays, buildings, how="difference")
        rays.geometry = rays.apply(lambda row: RayCasting4Lib.__keepTheAnchoredSegment(
            row.viewpoint, GeomLib.removeZCoordinate(row.geometry)), axis=1)
        rays = rays.loc[rays[~rays.geometry.apply(
            lambda geom: geom.is_empty)].index, :]
        isovRaysField = rays.dissolve(
            by="__VPT_ID__", as_index=False, aggfunc={"viewpoint": "first", "__RAY_ID__": list})
        # isovRaysField.drop(columns=["__VPT_ID__", "__RAY_ID__"], inplace=True)
        isovRaysField.drop(columns=["__VPT_ID__"], inplace=True)
        return isovRaysField

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
    def addIndicesToIsovRaysField2D(isovRaysField, precision=1.0, base=exp(1)):
        isovRaysField["__RAY_LEN__"] = isovRaysField.geometry.apply(
            lambda geom: asarray([ray.length for ray in geom.geoms]))

        isovRaysField = RayCasting4Lib.__add2DIndices(
            isovRaysField, precision, base)

        isovRaysField["__ISOV_GEOM__"] = isovRaysField.geometry.apply(
            lambda mls: Polygon([ls.coords[-1] for ls in mls.geoms]))
        isovRaysField["__ISOV_CENTRE__"] = isovRaysField.__ISOV_GEOM__.apply(
            lambda geom: geom.centroid)

        isovRaysField["vect_drift"] = isovRaysField.apply(
            lambda row: None if row.__ISOV_CENTRE__.is_empty else LineString([
                row.viewpoint.coords[0][0:2], row.__ISOV_CENTRE__.coords[0]]), axis=1)
        isovRaysField["drift"] = isovRaysField.vect_drift.apply(
            lambda v: v.length)

        isovRaysField.drop(
            columns=["__RAY_LEN__", "__ISOV_GEOM__", "__ISOV_CENTRE__"], inplace=True)
        return isovRaysField

    @staticmethod
    def __keepTheLargestSolidAngle(sensor, masks):
        if isinstance(masks, (Point, LineString)):
            _, remotePoint = nearest_points(sensor, masks)
            if equals(sensor, remotePoint):
                return LineString([])
            return LineString([sensor, remotePoint])

        maxSolidAngle, maxMask = -float("inf"), None
        for mask in masks.geoms:
            h, w = mask.coords[0][2], sensor.distance(mask)
            if (0 == w):
                # return LineString([sensor, sensor])
                return LineString([])
            currSolidAngle = h / w
            if (currSolidAngle > maxSolidAngle):
                maxSolidAngle, maxMask = currSolidAngle, mask
        _, remotePoint = nearest_points(sensor, maxMask)

        if equals(sensor, remotePoint):
            return LineString([])
        return LineString([sensor, remotePoint])

    @staticmethod
    def multipleRayCast25D(buildings, rays, elevationFieldName, h0=0.0):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, rays):
            raise Exception(
                "Illegal argument: buildings and rays must share shames CRS!")
        rays.geometry = rays.geometry.apply(lambda geom: GeomLib.forceZCoordinateToZ0(
            geom, z0=geom.coords[0][2] if geom.has_z else h0))

        isovRaysField = overlay(rays, buildings.geometry.to_frame(
        ), how="intersection", keep_geom_type=True)
        isovRaysField = isovRaysField.dissolve(by=["__VPT_ID__", "__RAY_ID__"], as_index=False, aggfunc={
                                               "gid": "first", "viewpoint": "first"})
        isovRaysField.geometry = isovRaysField.apply(lambda row: RayCasting4Lib.__keepTheLargestSolidAngle(
            row.viewpoint, row.geometry), axis=1)

        # left = rays.set_index(["__VPT_ID__", "__RAY_ID__"]).geometry.to_frame()
        # left = rays.set_index(["__VPT_ID__", "__RAY_ID__"])[["viewpoint", "geometry"]]
        left = rays.set_index(["__VPT_ID__", "__RAY_ID__"], drop=False)
        left.drop(columns=["__VPT_ID__"], inplace=True)
        right = isovRaysField.set_index(
            ["__VPT_ID__", "__RAY_ID__"]).geometry.to_frame()
        isovRaysField = left.merge(
            right, how="outer", left_index=True, right_index=True)

        isovRaysField["geometry"] = isovRaysField.apply(
            lambda row: row.geometry_x if row.geometry_y is None else row.geometry_y, axis=1)
        isovRaysField.drop(columns=["geometry_x", "geometry_y"], inplace=True)
        isovRaysField = GeoDataFrame(isovRaysField, crs=buildings.crs)
        isovRaysField = isovRaysField.loc[isovRaysField[~isovRaysField.geometry.apply(
            lambda geom: geom.is_empty)].index, :]
        isovRaysField = isovRaysField.dissolve(by="__VPT_ID__", as_index=False, aggfunc={
                                               "viewpoint": "first", "__RAY_ID__": list})
        isovRaysField.drop(columns=["__VPT_ID__"], inplace=True)

        return isovRaysField

    @staticmethod
    def __add3DIndices(isovRaysField):
        isovRaysField["w_mean"] = isovRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.mean()))
        isovRaysField["w_std"] = isovRaysField.__RAY_LEN__.apply(
            lambda raylens: float(raylens.std()))
        isovRaysField["h_mean"] = isovRaysField.__RAY_ALT__.apply(
            lambda heights: float(heights.mean()))

        isovRaysField["h_over_w"] = isovRaysField.apply(
            lambda row: row.h_mean / (2 * row.w_mean), axis=1)
        isovRaysField["svf"] = isovRaysField.apply(
            lambda row: SVFLib.svf2018(row.__RAY_DELTA_ALT__, row.__RAY_LEN__), axis=1)

        return isovRaysField

    @staticmethod
    def addIndicesToIsovRaysField25D(isovRaysField, precision=1.0, base=exp(1)):
        isovRaysField["__RAY_LEN__"] = isovRaysField.geometry.apply(
            lambda geom: asarray([ray.length for ray in geom.geoms]))
        isovRaysField["__RAY_ALT__"] = isovRaysField.geometry.apply(
            lambda geom: asarray([ray.coords[-1][2] for ray in geom.geoms]))
        isovRaysField["__RAY_DELTA_ALT__"] = isovRaysField.geometry.apply(
            lambda geom: asarray([max(ray.coords[-1][2]-ray.coords[0][2], 0) for ray in geom.geoms]))

        isovRaysField = RayCasting4Lib.__add3DIndices(isovRaysField)

        isovRaysField.drop(
            columns=["__RAY_LEN__", "__RAY_ALT__", "__RAY_DELTA_ALT__"], inplace=True)
        return isovRaysField


"""
buildings = GeoDataFrame([{"gid": x, "geometry": Polygon(
    [(-x, x, h), (x, x, h), (x, x+1, h), (-x, x+1, h)]), "H": h} for x, h in [(4, 4), (8, 8.1), (12, 12.1)]])
sensors = GeoDataFrame([
    {"id": y, "geometry": Point([0, y, 0])} for y in [0, 10, 13.0001]
])
rays = RayCasting4Lib.get25DPanopticRaysGeoDataFrame(
    sensors, rayLength=20.0, nRays=64)

isov = RayCasting4Lib.multipleRayCast25D(
    buildings, rays, elevationFieldName="H")
isov = RayCasting4Lib.addIndicesToIsovRaysField25D(
    isov)

_, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
buildings.plot(ax=ax, color="grey")
sensors.plot(ax=ax, color="green", marker="o")
# rays.plot(ax=ax, color="black", linewidth=0.3)
isov.plot(ax=ax, column="id", linewidth=1.5)
plt.tight_layout()
plt.show()
"""

"""
buildings = GeoDataFrame([{"gid": x, "geometry": Polygon(
    # [(-x, x, h), (x, x, h), (x, x+1, h), (-x, x+1, h)]), "H": h} for x, h in [(4, 4), (8, 8.1), (12, 12.1)]])
    [(-x, x, h), (x, x, h), (x, x+1, h), (-x, x+1, h)]), "H": h} for x, h in [(4, 4)]])
sensors = GeoDataFrame([
    # {"id": y, "geometry": Point([0, y])} for y in [0, 10, 15]
    {"id": y, "geometry": Point([0, y])} for y in [0]
])

nRays, rayLength = 64, 10.0
rays = RayCasting4Lib.get2DPanopticRaysGeoDataFrame(
    sensors, rayLength, nRays)
isovRaysField = RayCasting4Lib.multipleRayCast2D(
    buildings, rays)

_, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
buildings.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.3)
sensors.plot(ax=ax, color="red", marker=".")
sensors.apply(lambda x: ax.annotate(
    text=x["id"], xy=x.geometry.coords[0],
    color="red", size=12, ha="left", va="top"), axis=1)
isovRaysField.plot(ax=ax, color="blue", linewidth=0.3)
plt.axis("off")
plt.tight_layout()
plt.show()
"""
