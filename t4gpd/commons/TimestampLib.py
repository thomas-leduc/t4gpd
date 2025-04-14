"""
Created on 14 Apr. 2025

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

from pandas import Series, Timedelta, Timestamp, concat, date_range
from t4gpd.commons.sun.SunModel import SunModel


class TimestampLib(object):
    """
    classdocs
    """

    @staticmethod
    def from_d0_to_d1_using_freq(trios, tz="UTC"):
        result = []
        for dt0, dt1, freq in trios:
            if (dt0 is None) and (dt1 is None):
                continue

            inclusive = "both"
            if dt0 is None:
                dt1 = Timestamp(dt1)
                dt0 = dt1.normalize()
            elif dt1 is None:
                dt0 = Timestamp(dt0)
                dt1 = dt0.normalize() + Timedelta(days=1)
                inclusive = "left"
            else:
                dt0 = Timestamp(dt0)
                dt1 = Timestamp(dt1)

            _dts = date_range(
                start=dt0,
                end=dt1,
                freq=freq,
                inclusive=inclusive,
                tz=tz,
            )
            result.append(Series(_dts))
        result = concat(result, ignore_index=True)
        return result

    @staticmethod
    def from_daystart_to_dayoff(dts, freq="1h", tz="UTC"):
        """
        Generate a list of timestamps from the start to the end of the day
        :param dts: list of datetime objects
        :param freq: frequency of the Timestamps
        :param tz: timezone of the output Timestamps
        :return: list of Timestamps
        """
        result = []
        for dt in dts:
            _dts = date_range(
                start=dt.normalize(),
                end=dt.normalize() + Timedelta(days=1),
                freq=freq,
                inclusive="left",
                tz=tz,
            )
            result.append(Series(_dts))
        result = concat(result, ignore_index=True)
        return result

    @staticmethod
    def from_sunrise_to_sunset(gdf, dts, freq="1h", tz="UTC"):
        sunModel = SunModel(gdf, altitude=0, model="pvlib")
        sun_rise_set = sunModel.sun_rise_set(dts, tz=tz)
        result = []
        for day, row in sun_rise_set.iterrows():
            sunrise, sunset = row["sunrise"], row["sunset"]
            _dts = date_range(
                start=sunrise.ceil(freq), end=sunset, freq=freq, inclusive="both", tz=tz
            )
            result.append(Series(_dts))
        result = concat(result, ignore_index=True)
        return result
