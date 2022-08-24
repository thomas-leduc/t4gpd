'''
Created on 28 avr. 2022

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
from datetime import datetime, timezone

from geopandas import GeoDataFrame
from numpy import cos, max, sin, tan
from shapely.geometry import Point
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.SunLib import SunLib

from t4gpd.commons.RayCasting3Lib import RayCasting3Lib


class SunBeamLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def isHitBySunBeam(position, dt, masks, maskElevationFieldname='HAUTEUR', model='pysolar'):
        if not isinstance(position, Point):
            raise IllegalArgumentTypeException(position, 'Point')
        if not isinstance(dt, datetime):
            raise IllegalArgumentTypeException(dt, 'datetime')
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if not isinstance(masks, GeoDataFrame):
            raise IllegalArgumentTypeException(masks, 'GeoDataFrame')
        masksSIdx = masks.sindex
        if maskElevationFieldname not in masks:
            raise Exception('%s is not a relevant field name!' % (maskElevationFieldname))

        ptA = position if GeomLib.is3D(position) else GeomLib.forceZCoordinateToZ0(position, z0=0.0)
        maxElevation = max(masks[maskElevationFieldname])
        sunModel = SunLib(masks, model)
        alti, azim = sunModel.getSolarAnglesInRadians(dt)
        R = (maxElevation - ptA.z) / tan(alti)
        ptB = Point([ptA.x + R * cos(azim), ptA.y + R * sin(azim), ptA.z + R * sin(alti)])

        # return RayCasting2Lib.areCovisible(ptA, ptB, masks, maskElevationFieldname, masksSIdx)
        return RayCasting3Lib.areCovisibleIn3D(ptA, ptB, masks, maskElevationFieldname, masksSIdx)
