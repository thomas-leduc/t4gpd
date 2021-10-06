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
from datetime import datetime, timezone, timedelta
from warnings import warn

from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.PySolarSunLib import PySolarSunLib
from t4gpd.commons.sun.SoleneSunLib import SoleneSunLib

import matplotlib.pyplot as plt


class SunLib(object):
    '''
    classdocs
    '''

    def __init__(self, gdf=LatLonLib.NANTES, model='pysolar'):
        '''
        Constructor
        '''
        if ('pysolar' == model.lower()):
            self.model = PySolarSunLib(gdf)
        elif ('solene' == model.lower()):
            warn('Select SOLENE model')
            self.model = SoleneSunLib(gdf)
        else:
            raise IllegalArgumentTypeException(model, '{"pysolar", "solene"}')

        self.lat, self.lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)

    def getDayLengthInMinutes(self, dt):
        return self.model.getDayLengthInMinutes(dt)

    def getFractionalYear(self, dt):
        return self.model.getFractionalYear(dt)

    def getRadiationDirection(self, dt):
        return self.model.getRadiationDirection(dt)

    def getSolarAnglesInDegrees(self, dt):
        return self.model.getSolarAnglesInDegrees(dt)

    def getSolarAnglesInRadians(self, dt):
        return self.model.getSolarAnglesInRadians(dt)

    def getSolarDeclination(self, dayOfYear):
        return self.model.getSolarDeclination(dayOfYear)

    def getSunrise(self, dt):
        return self.model.getSunrise(dt)

    def getSunset(self, dt):
        return self.model.getSunset(dt)

    def plotDayLengths(self):
        year = datetime.now().year
        daysInYear = range(1, self.model.nDaysPerYear(year) + 1, 10)
        dayLengths = []

        for _dayOfYear in daysInYear:
            _dt = datetime(year, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=_dayOfYear)
            _dayLengthInMin = self.model.getDayLengthInMinutes(_dt)
            dayLengths.append(_dayLengthInMin)

        if (isinstance(self.model, SoleneSunLib)):
            _title = 'Solene model'
        elif (isinstance(self.model, PySolarSunLib)):
            _title = 'PySolar implementation'

        plt.title('%s: days lengths - Year %d\nLatitude: %.1f°, Longitude: %.1f°' % (
            _title, year, self.lat, self.lon))
        plt.xlabel('Day of year')
        plt.ylabel('Day length (min.)')
        plt.grid()
        plt.plot(daysInYear, dayLengths)
        plt.show()      

    def plotSolarDeclination(self):
        _year = datetime.now().year
        _the1stOfJan = datetime(_year, 1, 1, 12, tzinfo=timezone.utc)

        days = range(1, self.model.nDaysPerYear(_year) + 1)

        declinations = [
            self.model.getSolarDeclination(_the1stOfJan + timedelta(days=dayOfYear)) 
            for dayOfYear in days]

        if (isinstance(self.model, SoleneSunLib)):
            plt.title('Solar declination by Solene (Spencer, 1971) - year = %d' % _year)
        elif (isinstance(self.model, PySolarSunLib)):
            plt.title('Solar declination by PySolar - year = %d' % _year)

        plt.xlabel('Day of year')
        plt.ylabel('Solar declination')
        plt.grid()
        plt.plot(days, declinations)
        plt.show()      

    def plotSunAltiAtNoon(self):
        _year = datetime.now().year
        _the1stOfJan = datetime(_year, 1, 1, 12, tzinfo=timezone.utc)

        daysInYear = range(1, self.model.nDaysPerYear(_year) + 1, 10)
        sunAltiAtNoon = []

        for _dayOfYear in daysInYear:
            _dt = _the1stOfJan + timedelta(days=_dayOfYear)
            _alti, _ = self.model.getSolarAnglesInDegrees(_dt)
            sunAltiAtNoon.append(_alti)

        if (isinstance(self.model, SoleneSunLib)):
            _title = 'Solene model'
        elif (isinstance(self.model, PySolarSunLib)):
            _title = 'PySolar implementation'

        plt.title('%s: days lengths - Year %d\nLatitude: %.1f°, Longitude: %.1f°' % (
            _title, _year, self.lat, self.lon))
        plt.xlabel('Day of year')
        plt.ylabel('Solar altitude at noon (in degrees)')
        plt.grid()
        plt.plot(daysInYear, sunAltiAtNoon)
        plt.show()      

    def plotSunriseSunset(self):
        year = datetime.now().year
        daysInYear = range(1, self.model.nDaysPerYear(year) + 1, 10)
        sunrises, sunsets = [], []

        for _dayOfYear in daysInYear:
            _dt = datetime(year, 1, 1, 12, tzinfo=timezone.utc) + timedelta(days=_dayOfYear)

            _sunrise = self.model.getTimeSpentSinceMidnight(
                self.model.getSunrise(_dt))
            _sunset = self.model.getTimeSpentSinceMidnight(
                self.model.getSunset(_dt))

            sunrises.append(_sunrise)
            sunsets.append(_sunset)

        if (isinstance(self.model, SoleneSunLib)):
            _title = 'Solene model'
        elif (isinstance(self.model, PySolarSunLib)):
            _title = 'PySolar implementation'

        plt.title('%s: sunrise/sunset - Year %d\nLatitude: %.1f°, Longitude: %.1f°' % (
            _title, year, self.lat, self.lon))
        plt.xlabel('Day of year')
        plt.ylabel('UTC Time (hr.)')
        plt.grid()
        plt.plot(daysInYear, sunrises, daysInYear, sunsets)
        plt.show()      
