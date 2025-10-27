"""
Created on 23 aug. 2024

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
"""

from pandas import DatetimeIndex, to_datetime
from geopandas import GeoDataFrame
from pvlib.location import Location
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib


class STPvlibIrradiances(GeoProcess):
    """
    classdocs
    """

    def __init__(self, gdf, dts, altitude=0, model="ineichen"):
        """
        Constructor
        """
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        self.dts = to_datetime(dts) if not isinstance(dts, DatetimeIndex) else dts
        lat, lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        self.location = Location(lat, lon, altitude)

        self.model = model

    def run(self):
        df = self.location.get_clearsky(self.dts, model=self.model)
        # df = df.assign(timestamp=df.index)
        df.reset_index(names="timestamp", inplace=True)
        return df

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from datetime import date, timezone
        from locale import LC_ALL, setlocale
        from pandas import date_range
        from t4gpd.commons.sun.SunLib import SunLib

        sunModel = SunLib(LatLonLib.NANTES, model="pysolar")
        day = date(2023, 6, 21)
        sunrise, sunset = sunModel.getSunrise(day), sunModel.getSunset(day)
        dts = date_range(
            start=sunrise,
            end=sunset,
            freq=f"60min",
            inclusive="neither",
            tz=timezone.utc,
        )

        # dt = datetime(*sunrise.timetuple()[:-3], tzinfo=timezone.utc)
        # dts = []
        # while (dt + timedelta(minutes=60) < sunset):
        #     dt += timedelta(minutes=60)
        #     dts.append(dt)

        df = STPvlibIrradiances(LatLonLib.NANTES, dts).run()
        df = df.assign(time=df.timestamp.apply(lambda dt: dt.time()))

        # PLOTTING
        fig, ax = plt.subplots(figsize=(8.26, 8.26))
        setlocale(LC_ALL, "en_US.utf8")
        ax.set_title(f"Irradiation, {day.strftime('%B %d')}", fontsize=20)
        ax1 = df.plot("time", "dni", ax=ax, grid=True, label="DNI")
        df.plot("time", "dhi", ax=ax, grid=True, label="DHI")
        df.plot("time", "ghi", ax=ax, grid=True, label="GHI")
        ax1.set_xlabel("Timestamp (UTC)", fontdict={"fontsize": 16})
        ax1.set_ylabel("[W.m$^{-2}$]", fontdict={"fontsize": 16})
        fig.tight_layout()
        plt.show()

        return df


# STPvlibIrradiances.test()
