'''
Created on 26 aug. 2020

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
from geopandas.geodataframe import GeoDataFrame
from numpy import isnan
from shapely.geometry import MultiPolygon, Polygon
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.ShadowLib import ShadowLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.sun.AbstractHardShadow import AbstractHardShadow


class STHardShadow(AbstractHardShadow):
    '''
    classdocs
    '''

    def __init__(self, occludersGdf, datetimes, occludersElevationFieldname='HAUTEUR',
                 altitudeOfShadowPlane=0, aggregate=False, tz=None, model='pysolar'):
        '''
        Constructor
        '''
        if not isinstance(occludersGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(occludersGdf, 'GeoDataFrame')
        self.gdf = occludersGdf
        self.crs = occludersGdf.crs

        if occludersElevationFieldname not in occludersGdf:
            raise Exception('%s is not a relevant field name!' % (occludersElevationFieldname))
        self.occludersElevationFieldname = occludersElevationFieldname

        self.altitudeOfShadowPlane = altitudeOfShadowPlane
        self.aggregate = aggregate
        sunModel = SunLib(gdf=occludersGdf, model=model)

        self.sunPositions = DatetimeLib.fromDatetimesDictToListOfSunPositions(
            datetimes, sunModel, tz)

    def _auxiliary(self, row, radDir, solarAlti, solarAzim):
        occluderGeom = row.geometry
        occluderElevation = row[self.occludersElevationFieldname]

        if (occluderElevation is None) or (isnan(occluderElevation)):
            return occluderGeom

        if isinstance(occluderGeom, Polygon):
            _shadow = ShadowLib.projectBuildingOntoShadowPlane(
                occluderGeom, occluderElevation, radDir, self.altitudeOfShadowPlane)
            if _shadow is not None:
                return _shadow

        elif isinstance(occluderGeom, MultiPolygon):
            _shadows = []
            for g in occluderGeom.geoms:
                _shadow = ShadowLib.projectBuildingOntoShadowPlane(
                    g, occluderElevation, radDir, self.altitudeOfShadowPlane)
                if _shadow is not None:
                    _shadows.append(_shadow)
            return None if (0 == len(_shadows)) else MultiPolygon(_shadows)
