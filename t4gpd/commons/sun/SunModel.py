"""
Created on 6 dec. 2024

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

from datetime import datetime
from numpy import cos, deg2rad, sin
from pandas import DatetimeIndex, Series, concat, to_datetime
from pandas.core.arrays.datetimes import DatetimeArray
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib


class SunModel(object):
    """
    classdocs
    """

    class Pvlib(object):
        def __init__(self, gdf, altitude):
            from pvlib.location import Location

            lat, lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)
            self.location = Location(lat, lon, altitude)

        def clearsky_irradiances(self, dts, model="ineichen"):
            return self.location.get_clearsky(dts, model)

        def positions(self, dts):
            return self.location.get_solarposition(dts)

        def positions_clearsky_irradiances(self, dts, model="ineichen"):
            positions = self.location.get_solarposition(dts)
            irradiances = self.location.get_clearsky(dts, model)
            result = concat([positions, irradiances], axis=1)
            # result.reset_index(names="timestamp", inplace=True)
            return result

    class CircularEarthOrbit(object):
        def __init__(self, gdf, altitude):
            self.lat, _ = LatLonLib.fromGeoDataFrameToLatLon(gdf)

        @staticmethod
        def __solar_declination(day_of_year):
            # http://www.heliodon.net/downloads/Beckers_2010_Helio_007_fr.pdf
            # Spencer formula
            from numpy import cos, pi, sin

            g = ((2 * pi) * (day_of_year - 1)) / 365
            return (
                0.006918
                + -0.399912 * cos(g)
                + 0.070257 * sin(g)
                - 0.006758 * cos(2 * g)
                + 0.000907 * sin(2 * g)
                - 0.002697 * cos(3 * g)
                + 0.00148 * sin(3 * g)
            )

        @staticmethod
        def __hour_angle(dt):
            # Observing the sun from earth, the solar hour angle
            # is an expression of time, expressed in angular
            # measurement, usually degrees, from solar noon. At
            # solar noon the hour angle is 0.0 degree. The time
            # before solar noon is expressed as negative degrees.
            # 24hrs correspond to 360 degrees, 15 degrees per hour.
            from numpy import deg2rad

            return deg2rad(((dt.hour + (dt.minute / 60)) - 12) * 15)

        @staticmethod
        def __solar_angles(latitude, declination, hour_angle):
            from numpy import arcsin, arctan2, cos, deg2rad, pi, rad2deg, sin
            from t4gpd.commons.AngleLib import AngleLib

            latitude = deg2rad(latitude)

            # ELEVATION
            elevation = arcsin(
                sin(latitude) * sin(declination)
                + cos(latitude) * cos(declination) * cos(hour_angle)
            )

            # AZIMUTH
            azimuth = arctan2(
                (-cos(declination) * sin(hour_angle)) / cos(elevation),
                (sin(elevation) * sin(latitude) - sin(declination))
                / (cos(elevation) * cos(latitude)),
            )
            azimuth = AngleLib.southCCW2northCW(azimuth, degree=False)

            return rad2deg([elevation, azimuth])

        def clearsky_irradiances(self, dts):
            from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut

            df = self.positions(dts)

            raise NotImplementedError("Must be implemented!")

        def positions(self, dts):
            from pandas import DataFrame

            df = DataFrame({"elevation": dts, "azimuth": dts}, index=dts)
            df = DataFrame(
                columns=[
                    "day_of_year",
                    "declination",
                    "hour_angle",
                    "elev_azim",
                    "elevation",
                    "azimuth",
                ],
                index=dts,
            )
            df = df.assign(
                day_of_year=df.index.day_of_year,
                declination=lambda row: self.__solar_declination(row.day_of_year),
                hour_angle=lambda row: self.__hour_angle(row.index),
            )
            df.elev_azim = df.apply(
                lambda row: self.__solar_angles(
                    self.lat, row.declination, row.hour_angle
                ),
                axis=1,
            )
            df.elevation = df.elev_azim.apply(lambda ea: ea[0])
            df.azimuth = df.elev_azim.apply(lambda ea: ea[1])
            df.drop(columns=["elev_azim"], inplace=True)
            return df

        def positions_clearsky_irradiances(self, dts):
            return self.clearsky_irradiances(dts)

    def __init__(self, gdf=LatLonLib.NANTES, altitude=0, model="pvlib"):
        """
        Constructor
        """
        model_class = SunModel.model_switch(model)
        self.model = model_class(gdf, altitude)
        self.lat, self.lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        self.altitude = altitude

    @staticmethod
    def __to_DatetimeIndex(dts):
        if isinstance(dts, (list, DatetimeArray, Series)):
            dts = DatetimeIndex(to_datetime(dts))
        if not isinstance(dts, DatetimeIndex):
            raise IllegalArgumentTypeException(dts, "pandas.DatetimeIndex")
        return dts

    @staticmethod
    def is_a_leap_year(year):
        if isinstance(year, datetime):
            year = year.year
        return (0 == year % 400) if (0 == year % 100) else (0 == year % 4)

    @staticmethod
    def model_switch(modelName):
        modelName = modelName.lower()
        if "pvlib" == modelName:
            return SunModel.Pvlib
        elif "circular" == modelName:
            return SunModel.CircularEarthOrbit
        raise IllegalArgumentTypeException(modelName, "model as 'pvlib' or 'circular'")

    @staticmethod
    def ndays_per_year(year):
        if isinstance(year, datetime):
            year = year.year
        return 366 if (SunModel.is_a_leap_year(year)) else 365

    def sun_rise_set(self, dts, tz="UTC"):
        from pandas import DataFrame
        from suntimes.suntimes import SunTimes

        dts = SunModel.__to_DatetimeIndex(dts)
        st = SunTimes(self.lon, self.lat, altitude=self.altitude)
        df = DataFrame({"sunrise": dts, "sunset": dts}, index=dts)
        df.sunrise = df.sunrise.apply(lambda dt: st.riseutc(dt))
        df.sunrise = df.sunrise.dt.tz_localize("UTC")
        df.sunset = df.sunset.apply(lambda dt: st.setutc(dt))
        df.sunset = df.sunset.dt.tz_localize("UTC")
        if "UTC" != tz:
            df.sunrise = df.sunrise.dt.tz_convert(tz)
            df.sunset = df.sunset.dt.tz_convert(tz)
        df = df.assign(daylength=df.sunset - df.sunrise)
        # df.daylength = df.daylength.apply(lambda v: v.seconds//60)
        return df

    def clearsky_irradiances(self, dts):
        dts = SunModel.__to_DatetimeIndex(dts)
        return self.model.clearsky_irradiances(dts)

    def positions(self, dts):
        dts = SunModel.__to_DatetimeIndex(dts)
        return self.model.positions(dts)

    def __get_sun_beam_direction(self, df):
        def __to_sun_beam_direction(row):
            x = row.cos_elevation * row.cos_azimuth
            y = row.cos_elevation * row.sin_azimuth
            z = row.sin_elevation
            return x, y, z

        df["azimuth_rad"] = deg2rad(AngleLib.northCW2eastCCW(df.azimuth, degree=True))
        df["cos_azimuth"] = cos(df.azimuth_rad)
        df["sin_azimuth"] = sin(df.azimuth_rad)
        df["elevation_rad"] = deg2rad(df.elevation)
        df["cos_elevation"] = cos(df.elevation_rad)
        df["sin_elevation"] = sin(df.elevation_rad)
        df["sun_beam_direction"] = df.apply(
            lambda row: __to_sun_beam_direction(row),
            axis=1,
        )
        df.drop(
            columns=[
                "azimuth_rad",
                "cos_azimuth",
                "sin_azimuth",
                "elevation_rad",
                "cos_elevation",
                "sin_elevation",
            ],
            inplace=True,
        )
        return df

    def positions_and_sun_beam_direction(self, dts):
        result = self.__get_sun_beam_direction(self.positions(dts))
        return result

    def positions_clearsky_irradiances(self, dts):
        dts = SunModel.__to_DatetimeIndex(dts)
        return self.model.positions_clearsky_irradiances(dts)

    def positions_clearsky_irradiances_and_sun_beam_direction(self, dts):
        result = self.__get_sun_beam_direction(self.positions_clearsky_irradiances(dts))
        return result


"""
from pandas import Timestamp, date_range

tz = "Europe/Paris"
tz = "UTC"
dt0 = Timestamp("2024-06-21 08:00", tz=tz)
dt1 = Timestamp("2024-06-21 18:00", tz=tz)
dts = date_range(dt0, dt1, freq="1h")

# dt0 = Timestamp("2024-03-21 08:00", tz=tz)
# dt1 = Timestamp("2024-09-21 08:00", tz=tz)
# dts = date_range(dt0, dt1, freq="1ME")

# model = "pvlib"
# df = SunModel(model=model).sun_rise_set(dts, tz=tz)

model = "pvlib"
df1 = SunModel(model=model).positions(dts)

model = "circular"
df2 = SunModel(model=model).positions(dts)

print(
    concat([df1[["elevation", "azimuth"]], df2[["elevation", "azimuth"]]], axis=1)
)

model = "pvlib"
df3 = SunModel(model=model).positions_clearsky_irradiances(dts)
"""
