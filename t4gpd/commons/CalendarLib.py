'''
Created on 1 juil. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from datetime import date, datetime, timedelta, timezone

from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class CalendarLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def getEncapsulatingWeek(givenDate=date.today()):
        '''
        Returns the first and last day of the week, i.e. the Monday and Sunday
        that include the given date
        '''
        if not isinstance(givenDate, (date, datetime)):
            raise IllegalArgumentTypeException(givenDate, 'date or datetime')

        _curr = datetime(*givenDate.timetuple()[:3], 12, tzinfo=timezone.utc) 
        _currWeekDay = _curr.weekday()
        _firstDayOfWeek = _curr - timedelta(days=_currWeekDay)
        _lastDayOfWeek = _curr + timedelta(days=6 - _currWeekDay)
        _firstDayOfWeek = date(*_firstDayOfWeek.timetuple()[:3])
        _lastDayOfWeek = date(*_lastDayOfWeek.timetuple()[:3])
        return _firstDayOfWeek, _lastDayOfWeek
