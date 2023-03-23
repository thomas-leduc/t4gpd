'''
Created on 8 dec. 2022

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
from datetime import date, datetime, timedelta, timezone

from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunLib import SunLib


class DaylightLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def generate(dt, dtDelta=timedelta(minutes=15), gdf=LatLonLib.NANTES,
                 model='pysolar'):
        sunlib = SunLib(gdf, model)
        sunrise, sunset = sunlib.getSunrise(dt), sunlib.getSunset(dt)
        dts = []
        dt = sunrise + dtDelta
        while dt < sunset:
            dts.append(dt)
            dt += dtDelta
        return dts

"""
dt = date(2020, 12, 21)
dt = datetime(2020, 12, 21)
dts = DaylightLib.generate(dt, dtDelta=timedelta(hours=1))
for dt in dts:
    print(dt)
"""
