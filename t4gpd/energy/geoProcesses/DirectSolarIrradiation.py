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
from datetime import date, datetime, timedelta

from geopandas import GeoDataFrame
from numpy import dot
from shapely.geometry import Point
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess

from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.sun.SunBeamLib import SunBeamLib


class DirectSolarIrradiation(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, masksGdf, sensorsNormalFieldname, maskElevationFieldname,
                 dtStart, dtStop, dtDelta=timedelta(hours=1), model='pysolar'):
        '''
        Constructor
        '''
        if not isinstance(sensorsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'GeoDataFrame')

        if sensorsNormalFieldname not in sensorsGdf:
            raise Exception(f'{sensorsNormalFieldname} is not a relevant field name!')
        self.sensorsNormalFieldname = sensorsNormalFieldname

        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        self.masksGdf = masksGdf
        self.masksSIdx = masksGdf.sindex

        if maskElevationFieldname not in masksGdf:
            raise Exception(f'{maskElevationFieldname} is not a relevant field name!')
        self.maskElevationFieldname = maskElevationFieldname

        if not GeoDataFrameLib.shareTheSameCrs(sensorsGdf, masksGdf):
            raise Exception(f'The sensors & masks GeoDataFrame must share same CRS!')

        if not isinstance(dtStart, (date, datetime)):
            raise IllegalArgumentTypeException(dtStart, 'date or datetime')
        self.dt0 = dtStart

        if not isinstance(dtStop, (date, datetime)):
            raise IllegalArgumentTypeException(dtStop, 'date or datetime')
        self.dt1 = dtStop

        if not isinstance(dtDelta, timedelta):
            raise IllegalArgumentTypeException(dtDelta, 'timedelta')
        self.ddt = dtDelta

        self.model = model

        magnWh = dtDelta.total_seconds() / 3600
        datetimes = DatetimeLib.range(dtStart, dtStop, dtDelta)
        sunModel = SunLib(masksGdf, model)
        self.sunBeamsAndDni = DirectSolarIrradiation.__fromListOfDatetimesToListOfSunBeamsAndDNI(
            datetimes, magnWh, sunModel)

    @staticmethod
    def __fromListOfDatetimesToListOfSunBeamsAndDNI(datetimes, magnWh, sunModel, skyType=PerrinDeBrichambaut.STANDARD_SKY):
        result = []
        for dt in datetimes:
            radDir = sunModel.getRadiationDirection(dt)
            solarAlti, _ = sunModel.getSolarAnglesInRadians(dt)
            dni = PerrinDeBrichambaut.directNormalIrradiance(solarAlti, skyType) if (0.0 < solarAlti) else 0.0
            result.append([dt, radDir, dni * magnWh])
        return result

    def runWithArgs(self, row):
        geom = row.geometry
        if not isinstance(geom, Point):
            raise IllegalArgumentTypeException(geom, 'Point')
        normal = row[self.sensorsNormalFieldname]
        if isinstance(normal, str):
            normal = ArrayCoding.decode(normal)

        wh = 0
        for dt, radDir, dni in self.sunBeamsAndDni:
            if (0.0 < dni):
                dotProd = dot(normal, radDir)
                if (0 < dotProd):
                    hitBySunBeam, _ = SunBeamLib.isHitBySunBeam(geom, dt, self.masksGdf, self.maskElevationFieldname, self.model)
                    if hitBySunBeam:
                        wh += dni * dotProd
        return { 'direct_irradiation': wh }
