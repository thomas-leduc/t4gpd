"""
Created on 26 avr. 2022

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

from datetime import datetime, timezone
from locale import LC_ALL, setlocale
from numpy import asarray, dot, linspace, ndarray, sqrt
from numpy.linalg import norm
from pandas import DataFrame, Timedelta, Timestamp, date_range
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunModel import SunModel

import matplotlib.pyplot as plt


class DirectSolarIrradianceLib(object):
    """
    classdocs

    Irradiance is understood as instantaneous density of solar radiation incident on a given
    surface, typically expressed in W/m2.

    Irradiation is the sum of irradiance over a time period (e.g. 1 hour, day, month, etc.)
    expressed in J/m2. However, in daily routine Wh/m2 are more commonly used.
    """

    @staticmethod
    def direct_irradiance(normal, dts, gdf=LatLonLib.NANTES, model="pvlib"):
        """
        Direct Irradiance (DI in [W/m2]) is the amount of instantaneous solar radiation
        received per unit area by a surface whose normal is given as an input parameter.
        """
        if not isinstance(normal, (list, ndarray, tuple)) or (
            len(normal) not in [2, 3]
        ):
            raise IllegalArgumentTypeException(
                normal, "list or tuple of X, Y, and Z components"
            )
        if not Epsilon.equals(1.0, norm(normal), 1e-3):
            raise IllegalArgumentTypeException(normal, "unit vector")

        normal = asarray([*normal, 0.0] if (2 == len(normal)) else normal)

        sunModel = SunModel(gdf=gdf, altitude=0, model=model)
        df = sunModel.positions_clearsky_irradiances_and_sun_beam_direction(dts)
        df["dotProd"] = dot(df.sun_beam_direction.to_list(), normal)
        df["di"] = df.apply(
            lambda row: (
                row.dotProd * row.dni
                if (0.0 < row.apparent_elevation) and (0.0 < row.dotProd)
                else 0.0
            ),
            axis=1,
        )
        df.drop(columns=["dotProd"], inplace=True)
        return df

    @staticmethod
    def multiple_direct_irradiance(pairs, dts, gdf=LatLonLib.NANTES, model="pvlib"):
        sunModel = SunModel(gdf=gdf, altitude=0, model=model)
        df = sunModel.positions_clearsky_irradiances_and_sun_beam_direction(dts)
        for label, normal in pairs:
            if not isinstance(normal, (list, ndarray, tuple)) or (
                len(normal) not in [2, 3]
            ):
                raise IllegalArgumentTypeException(
                    normal, "list or tuple of X, Y, and Z components"
                )
            if not Epsilon.equals(1.0, norm(normal), 1e-3):
                raise IllegalArgumentTypeException(normal, "unit vector")

            normal = asarray([*normal, 0.0] if (2 == len(normal)) else normal)
            df["dotProd"] = dot(df.sun_beam_direction.to_list(), normal)
            df[label] = df.apply(
                lambda row: (
                    row.dotProd * row.dni
                    if (0.0 < row.apparent_elevation) and (0.0 < row.dotProd)
                    else 0.0
                ),
                axis=1,
            )
        df.drop(columns=["dotProd"], inplace=True)
        return df

    @staticmethod
    def noMaskDI(normal, dt, gdf=LatLonLib.NANTES, model="pvlib"):
        """
        Direct Irradiance (DI in [W/m2]) is the amount of instantaneous solar radiation
        received per unit area by a surface whose normal is given as an input parameter.
        """
        if not isinstance(normal, (list, tuple)) or (len(normal) not in [2, 3]):
            raise IllegalArgumentTypeException(
                normal, "list or tuple of X, Y, and Z components"
            )
        if not Epsilon.equals(1.0, norm(normal), 1e-3):
            raise IllegalArgumentTypeException(normal, "unit vector")

        if not isinstance(dt, datetime):
            raise IllegalArgumentTypeException(dt, "datetime")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        normal = (*normal, 0.0) if (2 == len(normal)) else normal

        sunModel = SunModel(gdf=gdf, altitude=0, model=model)
        sunModel = sunModel.positions_clearsky_irradiances_and_sun_beam_direction([dt])
        solarAlti = sunModel.loc[dt, "apparent_elevation"]
        radDir = sunModel.loc[dt, "sun_beam_direction"]

        dotProd = dot(radDir, normal)

        if (0.0 < solarAlti) and (0.0 < dotProd):
            dni = sunModel.loc[dt, "dni"]
            di = dotProd * dni
            return di
        return 0.0

    @staticmethod
    def noMaskDNI(dt, gdf=LatLonLib.NANTES, model="pvlib"):
        """
        Direct Normal Irradiance (DNI in [W/m2]) is the amount of solar radiation received
        per unit area by a surface that is always held perpendicular (or normal) to the rays
        that come in a straight line from the direction of the sun at its current position in
        the sky.
        """
        if not isinstance(dt, datetime):
            raise IllegalArgumentTypeException(dt, "datetime")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        sunModel = SunModel(gdf=gdf, altitude=0, model="pvlib")
        sunModel = sunModel.positions_clearsky_irradiances_and_sun_beam_direction([dt])
        solarAlti = sunModel.loc[dt, "apparent_elevation"]

        if 0.0 < solarAlti:
            return sunModel.loc[dt, "dni"]
        return 0.0

    @staticmethod
    def plot(label, normal, gdf=LatLonLib.NANTES, ofile=None):
        magn = 0.5

        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        days = [Timestamp(f"2025-{month}-21", tz="UTC") for month in [3, 6, 12]]
        freq = "10min"

        # PLOTTING
        fig, axes = plt.subplots(
            nrows=1,
            ncols=3,
            figsize=(3 * magn * 8.26, 1.3 * magn * 8.26),
            squeeze=False,
        )
        fig.suptitle(f"Direct Solar Irradiance, lat={lat:+.1f}°", size=20)
        for nc, day in enumerate(days):
            ax = axes[0, nc]
            dts = date_range(
                start=day.normalize(),
                end=day.normalize() + Timedelta(days=1),
                freq=freq,
                inclusive="left",
            )
            di = DirectSolarIrradianceLib.direct_irradiance(
                normal, dts, gdf=gdf, model="pvlib"
            )
            X = di.index.hour * 60 + di.index.minute

            setlocale(LC_ALL, "en_US.utf8")
            ax.set_title(f"{label} - {day.strftime('%b %d')}st", fontsize=14)
            ax.set_xlabel("Hour (UTC)", fontsize=14)
            ax.plot(X, di.di, linestyle="-", color="black", linewidth=2, label="DI")
            ax.plot(X, di.dni, linestyle=":", color="grey", linewidth=3, label="DNI")
            xticks = linspace(0, 60 * 24, 24 // 4, endpoint=False, dtype=int)
            ax.set_xticks(xticks)
            ax.set_xticklabels([f"{m//60}" for m in xticks], color="k", fontsize=14)
            if 0 == nc:
                ax.set_ylabel("Instantaneous irradiance [W.m$^{-2}$]", fontsize=14)
            ax.set_xlim([0, 24 * 60])
            ax.set_ylim([0, 1000])
            ax.legend()
            ax.grid()
        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, format="pdf", bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def plotAtkinsonAnnuel(gdf=LatLonLib.NANTES, ofile=None):
        t = 1.0 / sqrt(2.0)
        PAIRS1 = [
            ("Roof", (0, 0, 1)),
            ("N", (0, 1, 0)),
            ("W", (-1, 0, 0)),
            ("S", (0, -1, 0)),
            ("E", (1, 0, 0)),
        ]
        PAIRS2 = [
            ("Roof", (0, 0, 1)),
            ("NE", (t, t, 0)),
            ("NW", (-t, t, 0)),
            ("SW", (-t, -t, 0)),
            ("SE", (t, -t, 0)),
        ]

        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(gdf)

        day_step, freq = 10, "1h"
        days = [
            Timestamp(f"2025-{month}-{day}", tz="UTC")
            for month in range(1, 13)
            for day in range(1, 28, day_step)
        ]

        rows = []
        for day in days:
            row = {"timestamp": day}
            dts = date_range(
                start=day.normalize(),
                end=day.normalize() + Timedelta(days=1),
                freq=freq,
                inclusive="left",
            )
            for label, pairs in [
                ("Roof+N+E+S+W", PAIRS1),
                ("Roof+NE+SE+SW+NW", PAIRS2),
            ]:
                di = DirectSolarIrradianceLib.multiple_direct_irradiance(
                    pairs, dts, gdf=gdf, model="pvlib"
                )
                for sublabel, _ in pairs:
                    row[sublabel] = di[sublabel].sum()
            rows.append(row)

        df = DataFrame(rows)
        df["day_of_year"] = df.timestamp.dt.dayofyear
        df["Roof+N+E+S+W"] = df["Roof"] + df["N"] + df["E"] + df["S"] + df["W"]
        df["Roof+NE+SE+SW+NW"] = df["Roof"] + df["NE"] + df["SE"] + df["SW"] + df["NW"]

        mwh1 = day_step * df["Roof+N+E+S+W"].sum() * 1e-6
        mwh2 = day_step * df["Roof+NE+SE+SW+NW"].sum() * 1e-6
        df["Roof+N+E+S+W"] *= 1e-3
        df["Roof+NE+SE+SW+NW"] *= 1e-3

        # PLOTTING
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(1.2 * 8.26, 0.6 * 8.26))
        fig.suptitle(f"Direct Solar Irradiation, lat={lat:+.1f}°", size=20)
        ax.plot(
            df.day_of_year,
            df["Roof+N+E+S+W"],
            color="black",
            label=f"Roof+N+E+S+W ({mwh1:.2f} MWh/m$^3$)",
            linestyle=":",
            linewidth=2,
        )
        ax.plot(
            df.day_of_year,
            df["Roof+NE+SE+SW+NW"],
            color="grey",
            label=f"Roof+NE+SE+SW+NW ({mwh2:.2f} MWh/m$^3$)",
            linestyle="-",
            linewidth=2,
        )
        ax.set_xlabel("Day of year", fontsize=14)
        ax.set_ylabel("Daily irradiation [kWh]", fontsize=14)

        for month, label in [
            (3, "Spring\n\nequinox"),
            (6, "Summer\n\nsolstice"),
            (9, "Autumn\n\nequinox"),
            (12, "Winter\n\nsolstice"),
        ]:
            x0 = Timestamp(f"2025-{month}-21", tz="UTC").day_of_year
            ax.vlines(
                x=x0, ymin=5.5, ymax=16, linestyle="-.", color="blue", linewidth=1
            )
            ax.text(
                x0,
                7,
                label,
                fontsize=12,
                rotation=90,
                color="blue",
                ha="center",
                va="bottom",
            )

        ax.set_ylim([5, 18])
        ax.grid(color="gray", linestyle=":", linewidth=1)
        ax.legend(loc="upper center", framealpha=0.5, ncol=2, fontsize=12)

        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

        # return df


"""
DirectSolarIrradianceLib.plot("South orientation", (0, -1, 0), "/tmp/south.pdf")
DirectSolarIrradianceLib.plot("East orientation", (1, 0, 0), "/tmp/east.pdf")
DirectSolarIrradianceLib.plot("West orientation", (-1, 0, 0), "/tmp/west.pdf")
DirectSolarIrradianceLib.plot("Roof", (0, 0, 1), "/tmp/roof.pdf")

DirectSolarIrradianceLib.plotAtkinsonAnnuel("/tmp/atkinson_annuel.pdf")
"""
