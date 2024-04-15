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
from numpy import arange, cos, pi, sin, stack
from shapely import MultiLineString
from shapely.affinity import translate
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D


class PanopticRaysLib(object):
    '''
    classdocs
    '''
    """
    NORTH, WEST, SOUTH, EAST = 1, 2, 3, 4
    NE = pi / 4
    NW = (3 * pi) / 4
    SW = (5 * pi) / 4
    SE = (7 * pi) / 4

    @staticmethod
    def __fromRadiansToCompassCode(angle):
        if (PanopticRaysLib.NE <= angle < PanopticRaysLib.NW):
            return PanopticRaysLib.NORTH
        if (PanopticRaysLib.NW <= angle < PanopticRaysLib.SW):
            return PanopticRaysLib.WEST
        if (PanopticRaysLib.SW <= angle < PanopticRaysLib.SE):
            return PanopticRaysLib.SOUTH
        return PanopticRaysLib.EAST

    @staticmethod
    def __fromCompassCodeToOrientation(geometry):
        code = geometry.coords[0][2]
        if (PanopticRaysLib.NORTH == code):
            return "north"
        if (PanopticRaysLib.WEST == code):
            return "west"
        if (PanopticRaysLib.SOUTH == code):
            return "south"
        return "east"

    """
    @staticmethod
    def __get2DMultiLineString(rayLength=100.0, nRays=64):
        angles = ((2.0 * pi) / nRays) * arange(nRays)
        shootingDirs = rayLength * stack([cos(angles), sin(angles)], axis=1)
        return MultiLineString(
            [([(0, 0), xy]) for xy in shootingDirs])
        """
        shootingDirs = hstack([
            rayLength * stack([cos(angles), sin(angles)], axis=1),
            vectorize(PanopticRaysLib.__fromRadiansToCompassCode)(
                angles).reshape(-1, 1)
        ])
        return MultiLineString(
            [([(0, 0, xyz[2]), xyz]) for xyz in shootingDirs])
        """

    @staticmethod
    def get2DGeoDataFrame(sensors, rayLength=100.0, nRays=64):
        shootingDirs = PanopticRaysLib.__get2DMultiLineString(rayLength, nRays)
        rays2D = sensors.copy(deep=True)
        rays2D["viewpoint"] = rays2D.loc[:, "geometry"]
        rays2D.geometry = rays2D.geometry.apply(
            lambda geom: geom.centroid)
        rays2D.geometry = rays2D.geometry.apply(
            lambda geom: translate(shootingDirs, xoff=geom.x, yoff=geom.y))
        rays2D = rays2D.explode(index_parts=True)
        """
        rays2D["compass"] = rays2D.geometry.apply(
            lambda geom: PanopticRaysLib.__fromCompassCodeToOrientation(geom))
        rays2D.geometry = rays2D.geometry.apply(
            lambda geom: GeomLib.removeZCoordinate(geom))
        """
        rays2D = rays2D.reset_index(names=["__VPT_ID__", "__RAY_ID__"])
        return rays2D

    @staticmethod
    def get25DGeoDataFrame(sensors, rayLength=100.0, nRays=64, h0=0.0):
        rays25D = PanopticRaysLib.get2DGeoDataFrame(sensors, rayLength, nRays)
        rays25D.geometry = rays25D.apply(
            lambda row: GeomLib.forceZCoordinateToZ0(
                row.geometry, z0=GeomLib3D.centroid(
                    row.viewpoint).z if row.viewpoint.has_z else h0), axis=1)
        rays25D.viewpoint = rays25D.viewpoint.apply(
            lambda vp: GeomLib.forceZCoordinateToZ0(
                vp, z0=GeomLib3D.centroid(vp).z if vp.has_z else h0))
        return rays25D
