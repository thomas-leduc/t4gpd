'''
Created on 27 mai 2021

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
from datetime import date, datetime, timezone

from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class DateRangeLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def preprocess(date0, date1=None, period='hourly', tz=None):
        tz = timezone.utc if (tz is None) else tz

        if not isinstance(date0, date):
            raise IllegalArgumentTypeException(date0, 'date')
        date0 = datetime(*date0.timetuple()[:3], 0, tzinfo=tz)

        if not (date1 is None or isinstance(date1, date)):
            raise IllegalArgumentTypeException(date1, 'date')
        if date1 is None:
            date1 = datetime(*date0.timetuple()[:3], 23, tzinfo=tz)
        else:
            date1 = datetime(*date1.timetuple()[:3], 23, tzinfo=tz)

        if (date0 > date1):
            raise Exception(f'Nonsense: date0={date0} > date1={date1}')

        if not period in ('hourly', 'daily', 'weekly', 'monthly'):
            raise Exception("Illegal argument: period must be chosen in {'hourly', 'daily', 'weekly', 'monthly'}!")

        if 'hourly' == period:
            keyFilter = lambda dt: ((dt - date0).total_seconds() / 3600)
            fieldname = 'hour'
        elif 'daily' == period:
            keyFilter = lambda dt: dt.timetuple().tm_yday
            fieldname = 'day'
        elif 'weekly' == period:
            keyFilter = lambda dt: dt.isocalendar()[1]
            fieldname = 'week'
        elif 'monthly' == period:
            keyFilter = lambda dt: dt.month
            fieldname = 'month'

        return date0, date1, keyFilter, fieldname
