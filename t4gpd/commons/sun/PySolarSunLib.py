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
from datetime import timezone
import warnings

from pysolar import solar
from suntimes.suntimes import SunTimes
from t4gpd.commons.sun.AbstractSunLib import AbstractSunLib

warnings.filterwarnings('ignore', message="I don't know about leap seconds after 2020")


class PySolarSunLib(AbstractSunLib):
    '''
    classdocs
    '''

    def __azimToTrigonometric(self, solarAzimuthAngle):
        return (360 - (solarAzimuthAngle - 90)) % 360

    def getNativeSolarAnglesInDegrees(self, dt):
        alti = solar.get_altitude(self.lat, self.lon, dt)
        azim = solar.get_azimuth(self.lat, self.lon, dt)
        return alti, azim

    def getSolarAnglesInDegrees(self, dt):
        alti, azim = self.getNativeSolarAnglesInDegrees(dt)
        azim = self.__azimToTrigonometric(azim)
        return alti, azim

    def getSolarDeclination(self, dt):
        _dayOfYear = self.getDayOfYear(dt)
        return solar.get_declination(_dayOfYear)

    def getSunrise(self, dt):
        return SunTimes(self.lon, self.lat, altitude=0).riseutc(dt).replace(tzinfo=timezone.utc)

    def getSunset(self, dt):
        return SunTimes(self.lon, self.lat, altitude=0).setutc(dt).replace(tzinfo=timezone.utc)
