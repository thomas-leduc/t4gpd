'''
Created on 20 janv. 2021

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
from datetime import date, datetime, time, timedelta, timezone 

from numpy import ndarray
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class DatetimeLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def generate(dt, tz=None):
        tz = timezone.utc if (tz is None) else tz

        if ((isinstance(dt, (list, ndarray, tuple))) and (3 == len(dt)) and
            (isinstance(dt[0], datetime)) and (isinstance(dt[1], datetime)) and
            (isinstance(dt[2], timedelta))):
            _dtStart, _dtStop, _dtStep = dt
            # Timezone alignment
            _dtStart = datetime(*_dtStart.timetuple()[:6], tzinfo=tz)
            _dtStop = datetime(*_dtStop.timetuple()[:6], tzinfo=tz)
            _dt = _dtStart

            result = []
            while (_dt <= _dtStop):
                result.append(_dt)
                _dt = _dt + _dtStep
            return { '%s - %s' % (str(_dtStart), str(_dtStop)): result }

        elif isinstance(dt, datetime):
            return { str(dt): [dt.replace(tzinfo=tz)] }

        elif isinstance(dt, date):
            result = []
            _year, _month, _day = dt.timetuple()[:3]
            for _hour in range(4, 20):
                for _minute in range(0, 60, 30):
                    result.append(datetime(_year, _month, _day, _hour, _minute, tzinfo=tz))
            return { str(dt): result }

        elif isinstance(dt, time):
            result = []
            _year = date.today().year
            _tz = tz if (dt.tzinfo is None) else dt.tzinfo
            for _month in range(1, 13):
                for _day in range(1, 22, 10):
                    result.append(datetime(_year, _month, _day, dt.hour,
                                           dt.minute, dt.second,
                                           tzinfo=_tz))
            return { str(dt): result }

        elif isinstance(dt, (list, ndarray, tuple)):
            result = {}
            for _dt in dt:
                result.update(DatetimeLib.generate(_dt, tz))
            return result

        elif isinstance(dt, dict):
            return dt

        raise IllegalArgumentTypeException(dt, '(list of) date, time, datetime, or 3-uple of (datetime, datetime, timedelta)')

    @staticmethod
    def fromDatetimesDictToListOfSunPositions(datetimes, sunModel, tz=None):
        if not isinstance(datetimes, dict):
            datetimes = DatetimeLib.generate(datetimes, tz)

        result = []

        for _lbl, _dts in datetimes.items():
            for _dt in _dts:
                radDir = sunModel.getRadiationDirection(_dt)
                solarAlti, solarAzim = sunModel.getSolarAnglesInRadians(_dt)
                result.append([_dt, radDir, solarAlti, solarAzim])            

        return result
