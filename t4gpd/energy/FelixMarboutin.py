'''
Created on 21 sep. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
from datetime import datetime, timedelta, timezone
from locale import LC_ALL, setlocale
from numpy import asarray, sqrt
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.energy.DirectSolarIrradianceLib import DirectSolarIrradianceLib


class FelixMarboutin(GeoProcess):
    '''
    classdocs

    Irradiance is understood as instantaneous density of solar radiation incident on a given
    surface, typically expressed in W/m2.

    Irradiation is the sum of irradiance over a time period (e.g. 1 hour, day, month, etc.)
    expressed in J/m2. However, in daily routine Wh/m2 are more commonly used.
    '''
    R = sqrt(2)/2
    NORMALS = {
        "Roof": {"normalvector": (0, 0, 1), "linestyle": "dashdot", "linewidth": 2.25, "color": "black"},
        "Ground": {"normalvector": (0, 0, -1), "linestyle": "solid", "linewidth": 2.25, "color": "black"},
        "N": {"normalvector": (0, 1, 0), "linestyle": "solid", "linewidth": 2.25, "color": "blue"},
        "S": {"normalvector": (0, -1, 0), "linestyle": "solid", "linewidth": 2.25, "color": "red"},
        "E": {"normalvector": (1, 0, 0), "linestyle": "dotted", "linewidth": 2.75, "color": "darkorange"},
        "W": {"normalvector": (-1, 0, 0), "linestyle": "dashed", "linewidth": 2.75, "color": "brown"},
        "NE": {"normalvector": (R, R, 0), "linestyle": "dashed", "linewidth": 2.25, "color": "blue"},
        "NW": {"normalvector": (-R, R, 0), "linestyle": "dashed", "linewidth": 2.25, "color": "red"},
        "SW": {"normalvector": (-R, -R, 0), "linestyle": "dotted", "linewidth": 2.25, "color": "darkorange"},
        "SE": {"normalvector": (R, -R, 0), "linestyle": "dotted", "linewidth": 2.25, "color": "brown"},
    }
    YEAR = datetime.today().year
    DMJ = [
        datetime(YEAR, 12, 21, tzinfo=timezone.utc),
        datetime(YEAR, 3, 21, tzinfo=timezone.utc),
        datetime(YEAR, 6, 21, tzinfo=timezone.utc),
    ]
    MINUTES = range(0, 60, 15)

    def __init__(self, position=LatLonLib.NANTES,
                 normals=["Roof", "N", "S", "E", "W"],
                 stepInDays=10,
                 model="pysolar"):
        '''
        Constructor
        '''
        if ("epsg:4326" != position.crs):
            raise IllegalArgumentTypeException(
                position, "Must be a WGS84 GeoDataFrame")
        self.position = position
        self.lat, _ = LatLonLib.fromGeoDataFrameToLatLon(position)
        self.sunModel = SunLib(position, model=model)

        if not (set(normals) <= set(FelixMarboutin.NORMALS.keys())):
            raise IllegalArgumentTypeException(
                normals, f"Must be contained in {FelixMarboutin.NORMALS.keys()}")
        self.normals = normals
        self.stepInDays = stepInDays

    def __timeSinceMidnight(dt):
        midnight = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
        return (dt - midnight).seconds / 3600

    def __dailyIrradiances(self, dt0, sunrise, sunset, normal):
        X, Y = [], []
        for hour in range(int(sunrise), int(sunset)+1):
            for minutes in FelixMarboutin.MINUTES:
                dt = dt0 + timedelta(hours=hour, minutes=minutes)
                di = DirectSolarIrradianceLib.noMaskDI(
                    normal, dt, gdf=self.position)
                X.append(hour + minutes/60)
                Y.append(di)
        return X, Y

    def daily(self, dts=DMJ, ofile=None):
        sunrise = min([FelixMarboutin.__timeSinceMidnight(
            self.sunModel.getSunrise(dt)) for dt in dts])
        sunset = max([FelixMarboutin.__timeSinceMidnight(
            self.sunModel.getSunset(dt)) for dt in dts])

        ncols = len(dts)
        fig, axes = plt.subplots(ncols=ncols, figsize=(
            ncols * 8.26, 8.26), squeeze=False)
        fig.suptitle(
            f"Direct Solar Irradiance, lat. {self.lat:+.1f}°N", size=20)

        for nfig, dt0 in enumerate(dts):
            ax = axes[0, nfig]

            for normal in self.normals:
                _normal = FelixMarboutin.NORMALS[normal]
                X, Y = self.__dailyIrradiances(
                    dt0, sunrise, sunset, _normal["normalvector"])
                totalIrr = sum(Y) / (len(FelixMarboutin.MINUTES) * 1e3)
                ax.plot(X, Y, label=f"{normal}: {totalIrr:.1f} kWh/m$^2$",
                        linestyle=_normal["linestyle"],
                        linewidth=_normal["linewidth"],
                        color=_normal["color"])

            setlocale(LC_ALL, "en_US.utf8")
            ax.set_title(f"{dt0.strftime('%b %d')}", fontsize=18)
            ax.set_xlabel("Hour (UTC)", fontsize=14)
            ax.legend(loc="upper left", framealpha=0.5, ncol=2, fontsize=14)
            ax.set_ylim([0, 1000])
            ax.xaxis.set_major_locator(tck.MultipleLocator(base=2))
            ax.tick_params(axis="x", labelsize=14)
            ax.tick_params(axis="y", labelsize=14)
            if (0 == nfig):
                ax.set_ylabel(
                    "Instantaneous irradiance [W.m$^{-2}$]", fontsize=14)

        if ofile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    def __annualIrradiances(self, sunrise, sunset, normal):
        X, Y = range(0, 365, self.stepInDays), []

        dt0 = datetime(FelixMarboutin.YEAR, 1, 1, tzinfo=timezone.utc)
        for yday in X:
            irr = 0
            for hour in range(int(sunrise), int(sunset)+1):
                dt = dt0 + timedelta(days=yday, hours=hour)
                irr += DirectSolarIrradianceLib.noMaskDI(
                    normal, dt, gdf=self.position)
            Y.append(irr)
        return X, Y

    def annual(self, ofile=None):
        w_solstice = datetime(FelixMarboutin.YEAR, 12, 21)
        s_solstice = datetime(FelixMarboutin.YEAR, 6, 21)

        sunrise = min([FelixMarboutin.__timeSinceMidnight(
            self.sunModel.getSunrise(dt)) for dt in [w_solstice, s_solstice]])
        sunset = max([FelixMarboutin.__timeSinceMidnight(
            self.sunModel.getSunset(dt)) for dt in [w_solstice, s_solstice]])

        fig, ax = plt.subplots(figsize=(8.26, 0.55*8.26))

        for normal in self.normals:
            _normal = FelixMarboutin.NORMALS[normal]
            X, Y = self.__annualIrradiances(
                sunrise, sunset, _normal["normalvector"])
            Y = 1e-3 * asarray(Y)

            totalIrr = self.stepInDays * sum(Y) * 1e-3
            ax.plot(X, Y, label=f"{normal}: {totalIrr:.2f} MWh/m$^2$",
                    linestyle=_normal["linestyle"],
                    linewidth=_normal["linewidth"],
                    color=_normal["color"])
            ax.legend(loc="upper left", framealpha=0.5, ncol=2, fontsize=14)

        fig.suptitle(
            f"Direct Solar Irradiation, lat. {self.lat:+.1f}°N", size=20)
        ax.set_xlabel("Day of year", fontsize=14)
        ax.set_ylabel("Daily irradiation [kWh/m$^2$]", fontsize=14)
        ax.tick_params(axis="x", labelsize=14)
        ax.tick_params(axis="y", labelsize=14)

        for month, label in [(3, "Spring equinox"), (6, "Summer solstice"), (9, "Autumn equinox")]:
            x0 = datetime(FelixMarboutin.YEAR, month, 21, 12,
                          tzinfo=timezone.utc).timetuple().tm_yday
            ax.axvline(x=x0, linestyle="dotted", color="blue", linewidth=1)
            ax.text(x0, 2.5, label, rotation=90,
                    color="blue", va="center", fontsize=14)

        if ofile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)


"""
fm = FelixMarboutin()
fm.daily()
fm.annual()

FelixMarboutin(
    normals=FelixMarboutin.NORMALS.keys()
).daily(dts=[datetime(2023, 6, 21)])
"""
