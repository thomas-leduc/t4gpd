'''
Created on 6 dec. 2024

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
from pandas import concat
from pytz import timezone
from pandas import Timestamp, date_range
from datetime import datetime, timedelta

from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.PySolarSunLib import PySolarSunLib
from t4gpd.commons.sun.SoleneSunLib import SoleneSunLib

import matplotlib.pyplot as plt


class SunModel(object):
    '''
    classdocs
    '''
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
            return (0.006918 +
                    -0.399912 * cos(g) + 0.070257 * sin(g)
                    - 0.006758 * cos(2 * g) + 0.000907 * sin(2 * g)
                    - 0.002697 * cos(3 * g) + 0.00148 * sin(3 * g))

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
                (sin(elevation) * sin(latitude) - sin(declination)) /
                (cos(elevation) * cos(latitude))
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
                columns=["day_of_year", "declination",
                         "hour_angle", "elev_azim", "elevation", "azimuth"],
                index=dts)
            df = df.assign(
                day_of_year=df.index.day_of_year,
                declination=lambda row: self.__solar_declination(
                    row.day_of_year),
                hour_angle=lambda row: self.__hour_angle(
                    row.index),
            )
            df.elev_azim = df.apply(lambda row: self.__solar_angles(
                self.lat, row.declination, row.hour_angle), axis=1)
            df.elevation = df.elev_azim.apply(lambda ea: ea[0])
            df.azimuth = df.elev_azim.apply(lambda ea: ea[1])
            df.drop(columns=["elev_azim"], inplace=True)
            return df

        def positions_clearsky_irradiances(self, dts):
            return self.clearsky_irradiances(dts)

    def __init__(self, gdf=LatLonLib.NANTES, altitude=0, model="pvlib"):
        '''
        Constructor
        '''
        model_class = SunModel.model_switch(model)
        self.model = model_class(gdf, altitude)
        self.lat, self.lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        self.altitude = altitude

    @ staticmethod
    def __check_DatetimeIndex(dts):
        from pandas import DatetimeIndex
        if not isinstance(dts, DatetimeIndex):
            raise IllegalArgumentTypeException(
                dts, "pandas.DatetimeIndex")

    @ staticmethod
    def model_switch(modelName):
        modelName = modelName.lower()
        if ("pvlib" == modelName):
            return SunModel.Pvlib
        elif ("circular" == modelName):
            return SunModel.CircularEarthOrbit
        raise IllegalArgumentTypeException(
            modelName, "model as 'pvlib' or 'circular'")

    def sun_rise_set(self, dts, tz="UTC"):
        from pandas import DataFrame
        from suntimes.suntimes import SunTimes

        SunModel.__check_DatetimeIndex(dts)
        st = SunTimes(self.lon, self.lat, altitude=self.altitude)
        df = DataFrame({"sunrise": dts, "sunset": dts}, index=dts)
        df.sunrise = df.sunrise.apply(lambda dt: st.riseutc(dt))
        df.sunrise = df.sunrise.dt.tz_localize("UTC")
        df.sunset = df.sunset.apply(lambda dt: st.setutc(dt))
        df.sunset = df.sunset.dt.tz_localize("UTC")
        if ("UTC" != tz):
            df.sunrise = df.sunrise.dt.tz_convert(tz)
            df.sunset = df.sunset.dt.tz_convert(tz)
        df = df.assign(daylength=df.sunset-df.sunrise)
        # df.daylength = df.daylength.apply(lambda v: v.seconds//60)
        return df

    def clearsky_irradiances(self, dts):
        SunModel.__check_DatetimeIndex(dts)
        return self.model.clearsky_irradiances(dts)

    def positions(self, dts):
        SunModel.__check_DatetimeIndex(dts)
        return self.model.positions(dts)

    def positions_clearsky_irradiances(self, dts):
        SunModel.__check_DatetimeIndex(dts)
        return self.model.positions_clearsky_irradiances(dts)

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

    @staticmethod
    def polarPlot(models=["circular", "pvlib"], year=2023):
        from numpy import deg2rad
        from pandas import DatetimeIndex, Timestamp

        solstices_equinox = DatetimeIndex([
            Timestamp(f"{year}-03-21"),
            Timestamp(f"{year}-06-21"),
            Timestamp(f"{year}-12-21"),
        ])

        ncols = len(models)
        fig, axes = plt.subplots(figsize=(1.2*8.26, 0.5*8.26),
                                 nrows=1, ncols=ncols, squeeze=False,
                                 subplot_kw={"projection": "polar"})
        for nc, model in enumerate(models):
            sun_model = SunModel(model=model)
            sun_rise_set = sun_model.sun_rise_set(solstices_equinox, tz="UTC")

            ax = axes[0, nc]
            # NORTH IS ON TOP
            ax.set_theta_zero_location("N")
            # CLOCKWISE
            ax.set_theta_direction(-1)
            # LABEL POSITIONS
            # ax.set_rlabel_position(0)
            ax.set_title(model)
            ax.set_ylim(0, 90)

            for month, color in [(3, "green"), (6, "red"), (12, "blue")]:
                day = Timestamp(f"{year}-{month}-21")
                sunrise = sun_rise_set.loc[day, "sunrise"]
                sunset = sun_rise_set.loc[day, "sunset"]
                dts = date_range(sunrise, sunset, freq="10min")
                df = sun_model.positions(dts)
                ax.plot(deg2rad(df.azimuth), 90-df.elevation, color=color)

            for hour in range(6, 19, 2):
                start = Timestamp(f"{year}-01-01 {hour:02d}:00")
                end = Timestamp(f"{year}-12-31 {hour:02d}:00")
                dts = date_range(start, end, freq="5    D")
                df = sun_model.positions(dts)
                ax.plot(deg2rad(df.azimuth), 90-df.elevation, color="brown",
                        linewidth=0.75, linestyle="solid")

            ax.set_rgrids(
                range(0, 90, 10),
                labels=[f"{a}°" for a in range(90, 0, -10)])
            ax.set_thetagrids(
                range(0, 360, 15),
                labels=[f"{a}°" for a in range(0, 360, 15)])
        plt.show()
        plt.close(fig)

    def plotDayLengths(self):
        year = datetime.now().year
        daysInYear = range(1, self.model.nDaysPerYear(year) + 1, 10)
        dayLengths = []

        for _dayOfYear in daysInYear:
            _dt = datetime(year, 1, 1, 12, tzinfo=timezone.utc) + \
                timedelta(days=_dayOfYear)
            _dayLengthInMin = self.model.getDayLengthInMinutes(_dt)
            dayLengths.append(_dayLengthInMin)

        if (isinstance(self.model, SoleneSunLib)):
            _title = "Solene model"
        elif (isinstance(self.model, PySolarSunLib)):
            _title = "PySolar implementation"

        plt.title("%s: days lengths - Year %d\nLatitude: %.1f$^o$, Longitude: %.1f$^o$" % (
            _title, year, self.lat, self.lon))
        plt.xlabel("Day of year")
        plt.ylabel("Day length (min.)")
        plt.grid()
        plt.plot(daysInYear, dayLengths)
        plt.show()

    def plotSolarDeclination(self):
        _year = datetime.now().year
        _the1stOfJan = datetime(_year, 1, 1, 12, tzinfo=timezone.utc)

        days = range(1, self.model.nDaysPerYear(_year) + 1)

        declinations = [
            self.model.getSolarDeclination(
                _the1stOfJan + timedelta(days=dayOfYear))
            for dayOfYear in days]

        if (isinstance(self.model, SoleneSunLib)):
            plt.title(
                "Solar declination by Solene (Spencer, 1971) - year = %d" % _year)
        elif (isinstance(self.model, PySolarSunLib)):
            plt.title("Solar declination by PySolar - year = %d" % _year)

        plt.xlabel("Day of year")
        plt.ylabel("Solar declination")
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
            _title = "Solene model"
        elif (isinstance(self.model, PySolarSunLib)):
            _title = "PySolar implementation"

        plt.title("%s: days lengths - Year %d\nLatitude: %.1f$^o$, Longitude: %.1f$^o$" % (
            _title, _year, self.lat, self.lon))
        plt.xlabel("Day of year")
        plt.ylabel("Solar altitude at noon (in degrees)")
        plt.grid()
        plt.plot(daysInYear, sunAltiAtNoon)
        plt.show()

    def plotSunriseSunset(self):
        year = datetime.now().year
        daysInYear = range(1, self.model.nDaysPerYear(year) + 1, 10)
        sunrises, sunsets = [], []

        for _dayOfYear in daysInYear:
            _dt = datetime(year, 1, 1, 12, tzinfo=timezone.utc) + \
                timedelta(days=_dayOfYear)

            _sunrise = self.model.getTimeSpentSinceMidnight(
                self.model.getSunrise(_dt))
            _sunset = self.model.getTimeSpentSinceMidnight(
                self.model.getSunset(_dt))

            sunrises.append(_sunrise)
            sunsets.append(_sunset)

        if (isinstance(self.model, SoleneSunLib)):
            _title = "Solene model"
        elif (isinstance(self.model, PySolarSunLib)):
            _title = "PySolar implementation"

        plt.title("%s: sunrise/sunset - Year %d\nLatitude: %.1f$^o$, Longitude: %.1f$^o$" % (
            _title, year, self.lat, self.lon))
        plt.xlabel("Day of year")
        plt.ylabel("UTC Time (hr.)")
        plt.grid()
        plt.plot(daysInYear, sunrises, daysInYear, sunsets)
        plt.show()

    def plotSolarPanorama(self):
        year = datetime.now().year
        _, basemap = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))

        if (isinstance(self.model, SoleneSunLib)):
            _title = "Solene model"
        elif (isinstance(self.model, PySolarSunLib)):
            _title = "PySolar implementation"
        plt.title("%s: solar panorama - year %d\nLatitude: %.1f$^o$, Longitude: %.1f$^o$" % (
            _title, year, self.lat, self.lon))
        plt.xlabel("Azim. [$^0$]")
        plt.ylabel("Alti. [$^0$]")

        altis, azims = {}, {}
        hrsAltis, hrsAzims = {}, {}

        for hour in range(0, 24):
            hrsAltis[hour], hrsAzims[hour] = [], []

        for month in range(6, 13, 3):
            altis[month], azims[month] = [], []
            t0 = datetime(year, month, 21, tzinfo=timezone.utc)
            _sunrise = self.model.getSunrise(t0)
            _sunset = self.model.getSunset(t0)

            for hour in range(0, 24):
                for minute in range(0, 60, 10):
                    _dt = t0 + timedelta(hours=hour) + \
                        timedelta(minutes=minute)
                    if True or (_sunrise < _dt < _sunset):
                        _alti, _azim = self.model.getNativeSolarAnglesInDegrees(
                            _dt)
                        if (0 <= _alti):
                            altis[month].append(_alti)
                            azims[month].append(_azim)
                        if (0 == minute):
                            hrsAltis[hour].append(_alti)
                            hrsAzims[hour].append(_azim)

            basemap.plot(azims[month], altis[month],
                         label=_dt.strftime("%b %d"))

        for hour in range(5, 20, 1):
            if (0 == (hour % 2)):
                basemap.plot(hrsAzims[hour], hrsAltis[hour], "k-.")
                basemap.text((3 * hrsAzims[hour][0] + hrsAzims[hour][-1]) / 4,
                             (3 * hrsAltis[hour][0] + hrsAltis[hour][-1]) / 4,
                             f"{hour}:00", fontsize=9).set_color("black")

        for lbl, azim in [("East", 90), ("South", 180), ("West", 270)]:
            basemap.axvline(x=azim, linestyle=":", color="black", linewidth=1)
            basemap.text(azim, 70, lbl, fontsize=9).set_color("black")
        basemap.set_ylim(0, 90)

        basemap.legend()
        plt.show()


"""
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

SunModel.polarPlot()
"""
