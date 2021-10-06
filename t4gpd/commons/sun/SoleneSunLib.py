'''
Created on 21 janv. 2021

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
from datetime import datetime, timedelta, timezone

from numpy import arccos, arctan2, cos, pi, sin, tan
from t4gpd.commons.AngleLib import AngleLib

from t4gpd.commons.sun.AbstractSunLib import AbstractSunLib


class SoleneSunLib(AbstractSunLib):
    '''
    classdocs
    '''
    MINS1440 = 1440
    PI_DIV_2 = pi / 2.0
    PI_TIMES_2 = pi * 2.0

    def __fromHourAngleToMinutes(self, hourAngle):
        return int(720.0 + AngleLib.toDegrees(hourAngle) / 0.25)

    @staticmethod
    def __getEquationOfTime(fractionalYear):
        '''
        Based on "General Solar Position Calculations - NOAA Global Monitoring Division"
        https://www.esrl.noaa.gov/gmd/grad/solcalc/solareqns.PDF
        '''
        return 229.18 * (0.000075 + 
                         0.001868 * cos(fractionalYear) - 
                         0.032077 * sin(fractionalYear) - 
                         0.014615 * cos(2 * fractionalYear) - 
                         0.040849 * sin(2 * fractionalYear))

    def __getFractionalYear(self, dt):
        '''
        Based on "General Solar Position Calculations - NOAA Global Monitoring Division"
        https://www.esrl.noaa.gov/gmd/grad/solcalc/solareqns.PDF
        '''
        _dayOfYear = self.getDayOfYear(dt)
        return 2 * pi * (_dayOfYear - 1.0 + (dt.hour - 12.0) / 24.0) / self.nDaysPerYear(dt)

    def getSolarAnglesInDegrees(self, dt):
        _tz = 0 if (dt.utcoffset() is None) else dt.utcoffset().seconds / 3600
        _latInRadians = AngleLib.toRadians(self.lat)

        _fractionalYear = self.__getFractionalYear(dt)
        _eqTime = SoleneSunLib.__getEquationOfTime(_fractionalYear)
        _declination = self.__getSolarDeclinationInRadians(_fractionalYear)

        hour, minute = dt.hour, dt.minute
        # timeOffset = _eqTime + 4 * self.lon - 60 * _tz
        # According to: http://www.jgiesen.de/astro/suncalc/calculations.htm
        timeOffset = _eqTime - 4 * self.lon + 60 * _tz

        # trueSolarTime = hour * 60.0 + minute + second / 60.0 + timeOffset
        # According to: http://www.jgiesen.de/astro/suncalc/calculations.htm
        trueSolarTime = hour * 60.0 + minute + timeOffset
        '''
        Observing the sun from earth, the solar hour angle is an expression of
        time, expressed in angular measurement, usually degrees, from solar noon.
        At solar noon the hour angle is 0.0 degree. The time before solar noon is
        expressed as negative degrees. 24hrs correspond to 360 degrees, 15
        degrees per hour or 0.25 degree per minute.
        '''
        # solarHourAngle = AngleLib.toRadians((trueSolarTime - 12.0 * 60) * 0.25)
        # According to: http://www.jgiesen.de/astro/suncalc/calculations.htm
        solarHourAngle = AngleLib.toRadians((trueSolarTime / 4.0) - 180)

        cosLat, sinLat = cos(_latInRadians), sin(_latInRadians)
        cosDeclination, sinDeclination = [cos(_declination), sin(_declination)]
        cosHourAngle = cos(solarHourAngle)
        cosDeclinationCosHourAngle = cosDeclination * cosHourAngle

        cosSolarZenithAngle = (sinLat * sinDeclination + cosLat * cosDeclinationCosHourAngle)

        solarZenithAngle = arccos(cosSolarZenithAngle)
        alti = SoleneSunLib.PI_DIV_2 - solarZenithAngle

        # According to: https://researchlibrary.agric.wa.gov.au/cgi/viewcontent.cgi?article=1122&context=rmtr
        azim = SoleneSunLib.PI_DIV_2 - arctan2(
            -sin(solarHourAngle), (tan(_declination) * cos(_latInRadians) - sin(_latInRadians) * cos(solarHourAngle))
            )
        if (0 > azim):
            azim += SoleneSunLib.PI_TIMES_2

        return AngleLib.toDegrees(alti), AngleLib.toDegrees(azim)

    def __getSolarDeclinationInRadians(self, fractionalYear):
        '''
        Based on "General Solar Position Calculations - NOAA Global Monitoring Division"
        https://www.esrl.noaa.gov/gmd/grad/solcalc/solareqns.PDF

        Solar Declination by Spencer (1971)
        '''
        return (0.006918 - 
                0.399912 * cos(fractionalYear) + 
                0.070257 * sin(fractionalYear) - 
                0.006758 * cos(2 * fractionalYear) + 
                0.000907 * sin(2 * fractionalYear) - 
                0.002697 * cos(3 * fractionalYear) + 
                0.00148 * sin(3 * fractionalYear))

    def getSolarDeclination(self, dt):
        _fractionalYear = self.__getFractionalYear(dt)
        _declination = self.__getSolarDeclinationInRadians(_fractionalYear)
        return AngleLib.toDegrees(_declination)

    def getSunrise(self, dt):
        _latInRadians = AngleLib.toRadians(self.lat)
        _fractionalYear = self.__getFractionalYear(dt)
        _declination = self.__getSolarDeclinationInRadians(_fractionalYear)
        '''
        _solarHourAngle = arccos(
            cos(AngleLib.toRadians(90.833)) / (cos(_latInRadians) * cos(_declination)) - 
            tan(_latInRadians) * tan(_declination))
        return 720 - 4 * (self.lon + _solarHourAngle) - _eqTime
        '''
        _solarHourAngle = -arccos(-tan(_declination) * tan(_latInRadians))
        _delta = self.__fromHourAngleToMinutes(_solarHourAngle)
        _today = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
        return _today + timedelta(minutes=_delta)

    def getSunset(self, dt):
        _latInRadians = AngleLib.toRadians(self.lat)
        _fractionalYear = self.__getFractionalYear(dt)
        _declination = self.__getSolarDeclinationInRadians(_fractionalYear)
        '''
        _solarHourAngle = arccos(
            cos(AngleLib.toRadians(90.833)) / (cos(_latInRadians) * cos(_declination)) - 
            tan(_latInRadians) * tan(_declination))
        return 720 - 4 * (self.lon + _solarHourAngle) - _eqTime
        '''
        _solarHourAngle = -arccos(-tan(_declination) * tan(_latInRadians))
        _delta = self.MINS1440 - self.__fromHourAngleToMinutes(_solarHourAngle)
        _today = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
        return _today + timedelta(minutes=_delta)
