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
from datetime import datetime, timedelta

from numpy import cos, round, sin
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.LatLonLib import LatLonLib


class AbstractSunLib(object):
    '''
    classdocs
    '''

    def __init__(self, gdf=LatLonLib.NANTES):
        self.lat, self.lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)

    def __fromSolarAnglesToRadiationDirection(self, alti, azim):
        cosAlt = cos(alti)
        x = cosAlt * cos(azim)
        y = cosAlt * sin(azim)
        z = sin(alti)
        return x, y, z

    def getDayLengthInMinutes(self, dt):
        _sunrise = self.getSunrise(dt)
        _sunset = self.getSunset(dt)
        return (_sunset - _sunrise).seconds // 60

    def getDayOfYear(self, dt):
        return dt.timetuple().tm_yday

    def getMinutesSpentSinceMidnight(self, dt):
        _midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(round((dt - _midnight) / timedelta(minutes=1)))

    def getTimeSpentSinceMidnight(self, dt):
        _midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return ((dt - _midnight) / timedelta(hours=1))

    def getRadiationDirection(self, dt):
        alti, azim = self.getSolarAnglesInRadians(dt)
        return self.__fromSolarAnglesToRadiationDirection(alti, azim)

    def getSolarAnglesInDegrees(self, dt):
        raise NotImplementedError('getSolarAnglesInDegrees(...) must be overridden!')

    def getSolarAnglesInRadians(self, dt):
        alti, azim = self.getSolarAnglesInDegrees(dt)
        return AngleLib.toRadians(alti), AngleLib.toRadians(azim)

    def getSolarDeclination(self, dayOfYear):
        raise NotImplementedError('getSolarDeclination(...) must be overridden!')

    def isALeapYear(self, year):
        if isinstance(year, datetime):
            year = year.year
        return (0 == year % 400) if (0 == year % 100) else (0 == year % 4)

    def nDaysPerYear(self, year):
        if isinstance(year, datetime):
            year = year.year
        return 366 if (self.isALeapYear(year)) else 365
