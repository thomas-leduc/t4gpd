"""
Created on 27 sep. 2024

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
from datetime import date, datetime, timedelta
from pymap3d import Ellipsoid
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class SatelliteLib:
    """
    classdocs
    """

    CDDIS_BASE_URL = "https://cddis.nasa.gov/archive/gnss/products"
    GPS_START = date(1980, 1, 6)

    CONSTELLATIONS = {"E": "Galileo", "G": "GPS", "R": "GLONASS"}
    NSAT = 94
    WGS84 = Ellipsoid.from_name("wgs84")

    @staticmethod
    def constellation(satName):
        firstLetter = satName[0]
        return SatelliteLib.CONSTELLATIONS[firstLetter]

    @staticmethod
    def get_satellite_name(i):
        if 0 <= i <= 31:
            return f"G{i+1:02d}"  # GPS
        if 32 <= i <= 57:
            return f"R{i-32+1:02d}"  # GLONASS
        if 58 <= i <= 93:
            return f"E{i-58+1:02d}"  # GALILEO
        raise Exception("Unreachable instruction!")

    @staticmethod
    def get_satellite_names(version):
        if version == 1:
            return [f"sat_{i}" for i in range(SatelliteLib.NSAT)]
        if version == 2:
            return [
                SatelliteLib.get_satellite_name(i) for i in range(SatelliteLib.NSAT)
            ]
        raise Exception("Unknown version!")

    @staticmethod
    def get_gps_week(d):
        delta = d - SatelliteLib.GPS_START
        return delta.days // 7

    @staticmethod
    def get_cddis_sp3_urls(dt_or_year):
        def __get_url(dt):
            gps_week = SatelliteLib.get_gps_week(dt)
            year = dt.year
            doy = dt.timetuple().tm_yday
            hour = 0
            url = f"{SatelliteLib.CDDIS_BASE_URL}/{gps_week}/COD0OPSULT_{year}{doy:03d}{hour:02d}00_02D_05M_ORB.SP3.gz"
            return url

        if isinstance(dt_or_year, int) and (
            SatelliteLib.GPS_START.year <= dt_or_year <= date.today().year
        ):
            # CHARGEMENTS MULTIPLES SUR FIREFOX
            # https://addons.mozilla.org/en-US/firefox/addon/open-multiple-urls/
            gps_weeks0 = SatelliteLib.get_gps_week(date(dt_or_year, 1, 1))
            gps_weeks1 = SatelliteLib.get_gps_week(date(dt_or_year, 12, 31))
            hour = 0

            urls = []
            for gps_week in range(gps_weeks0, gps_weeks1 + 1):
                for days in range(7):
                    dt = SatelliteLib.GPS_START + timedelta(weeks=gps_week, days=days)
                    doy = dt.timetuple().tm_yday
                    if (dt_or_year == dt.year) and (1 == doy % 2):
                        url = f"{SatelliteLib.CDDIS_BASE_URL}/{gps_week}/COD0OPSULT_{dt_or_year}{doy:03d}{hour:02d}00_02D_05M_ORB.SP3.gz"
                        urls.append(url)
            return urls
        elif isinstance(dt_or_year, (date, datetime)):
            return __get_url(dt_or_year)
        raise IllegalArgumentTypeException(dt_or_year, "(year) int, date or datetime")


# print(SatelliteLib.get_cddis_sp3_urls(date.today()))
# r = SatelliteLib.get_cddis_sp3_urls(2024)
# print("\n".join(r))
