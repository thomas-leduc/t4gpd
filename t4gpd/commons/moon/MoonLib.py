'''
Created on 10 mar. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from ephem import (localtime, next_first_quarter_moon, next_full_moon, next_last_quarter_moon, next_new_moon,
                   previous_first_quarter_moon, previous_full_moon, previous_last_quarter_moon, previous_new_moon)
from pandas import DataFrame


class MoonLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def moon_phases_calendar(year):
        # Inner function
        def _add(year, moons, dt, fct1, fct2, label):
            for fct in [fct1, fct2]:
                t = localtime(fct(dt))
                if (year == t.year):
                    moons[t.date()] = label

        # 1st step
        moons = {}
        dt0 = datetime(year, 1, 1, 12)
        for day_of_year in range(0, 366, 7):
            dt = dt0 + timedelta(days=day_of_year)
            _add(year, moons, dt, next_first_quarter_moon,
                 previous_first_quarter_moon, "first_quarter")
            _add(year, moons, dt, next_full_moon, previous_full_moon, "full")
            _add(year, moons, dt, next_last_quarter_moon,
                 previous_last_quarter_moon, "last_quarter")
            _add(year, moons, dt, next_new_moon, previous_new_moon, "new")

        # 2nd step
        rows = []
        for day in sorted(moons.keys()):
            rows.append({
                "timestamp": day,
                "day_of_year": day.timetuple().tm_yday,
                "moon_phasis": moons[day],
            })
        df = DataFrame(rows)
        return df


# df = MoonLib.moon_phases_calendar(2023)
