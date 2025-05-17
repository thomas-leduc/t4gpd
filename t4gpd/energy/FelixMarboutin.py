"""
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
"""

import matplotlib.pyplot as plt
from locale import LC_ALL, setlocale
from numpy import linspace, sqrt
from pandas import DataFrame, Timedelta, Timestamp, date_range
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.energy.DirectSolarIrradianceLib import DirectSolarIrradianceLib


class FelixMarboutin(GeoProcess):
    """
    classdocs

    Irradiance is understood as instantaneous density of solar radiation incident on a given
    surface, typically expressed in W/m2.

    Irradiation is the sum of irradiance over a time period (e.g. 1 hour, day, month, etc.)
    expressed in J/m2. However, in daily routine Wh/m2 are more commonly used.
    """

    R = sqrt(2) / 2
    NORMALS = {
        "Roof": {
            "normalvector": (0, 0, 1),
            "linestyle": "dashdot",
            "linewidth": 2.25,
            "color": "black",
        },
        "Ground": {
            "normalvector": (0, 0, -1),
            "linestyle": "solid",
            "linewidth": 2.25,
            "color": "black",
        },
        "N": {
            "normalvector": (0, 1, 0),
            "linestyle": "solid",
            "linewidth": 2.25,
            "color": "blue",
        },
        "S": {
            "normalvector": (0, -1, 0),
            "linestyle": "solid",
            "linewidth": 2.25,
            "color": "red",
        },
        "E": {
            "normalvector": (1, 0, 0),
            "linestyle": "dashed",
            "linewidth": 2.75,
            "color": "darkorange",
        },
        "W": {
            "normalvector": (-1, 0, 0),
            "linestyle": "dashed",
            "linewidth": 2.75,
            "color": "brown",
        },
        "NE": {
            "normalvector": (R, R, 0),
            "linestyle": "dotted",
            "linewidth": 2.25,
            "color": "blue",
        },
        "NW": {
            "normalvector": (-R, R, 0),
            "linestyle": "dotted",
            "linewidth": 2.25,
            "color": "red",
        },
        "SW": {
            "normalvector": (-R, -R, 0),
            "linestyle": "dotted",
            "linewidth": 2.25,
            "color": "darkorange",
        },
        "SE": {
            "normalvector": (R, -R, 0),
            "linestyle": "dotted",
            "linewidth": 2.25,
            "color": "brown",
        },
    }

    @staticmethod
    def daily(
        days,
        labels=["Roof", "N", "S", "E", "W"],
        gdf=LatLonLib.NANTES,
        model="pvlib",
        pivot=False,
        ofile=None,
    ):
        freq = "10min"
        pairs = [
            (label, FelixMarboutin.NORMALS[label]["normalvector"]) for label in labels
        ]
        lat, _ = LatLonLib.fromGeoDataFrameToLatLon(gdf)

        # PLOTTING
        magn = 0.9
        nrows, ncols = (len(days), 1) if pivot else (1, len(days))
        fig, axes = plt.subplots(
            ncols=ncols,
            nrows=nrows,
            figsize=(ncols * magn * 8.26, nrows * 0.8 * magn * 8.26),
            squeeze=False,
        )
        fig.suptitle(f"Direct Solar Irradiance, lat. {lat:+.1f}°N", size=20)

        for n, day in enumerate(days):
            nr, nc = divmod(n, ncols)
            ax = axes[nr, nc]

            dts = date_range(
                start=day.normalize(),
                end=day.normalize() + Timedelta(days=1),
                freq=freq,
                inclusive="left",
            )
            di = DirectSolarIrradianceLib.multiple_direct_irradiance(
                pairs, dts, gdf=gdf, model=model
            )
            X = di.index.hour * 60 + di.index.minute

            setlocale(LC_ALL, "en_US.utf8")
            ax.set_title(f"{day.strftime('%b %d')}st", fontsize=18)

            for label, _ in pairs:
                kwh = di[label].sum() * 1e-3 / (len(di) / 24)
                ax.plot(
                    X,
                    di[label],
                    linestyle=FelixMarboutin.NORMALS[label]["linestyle"],
                    color=FelixMarboutin.NORMALS[label]["color"],
                    linewidth=FelixMarboutin.NORMALS[label]["linewidth"],
                    label=f"{label} {kwh:.1f} kWh/m$^2$",
                )
            ax.set_ylim([0, 1000])
            if (nrows - 1) == nr:
                ax.set_xlabel("Hour (UTC)", fontsize=14)
            if 0 == nc:
                ax.set_ylabel("Instantaneous irradiance [W.m$^{-2}$]", fontsize=14)
            xticks = linspace(0, 60 * 24, 24 // 4, endpoint=False, dtype=int)
            ax.set_xticks(xticks)
            ax.set_xticklabels([f"{m//60}" for m in xticks], color="k", fontsize=14)
            ax.legend(loc="upper left", framealpha=0.5, ncol=2, fontsize=14)

        if ofile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

        return di

    @staticmethod
    def annual(
        labels=["Roof", "N", "S", "E", "W"],
        gdf=LatLonLib.NANTES,
        model="pvlib",
        ofile=None,
    ):
        freq = "10min"
        pairs = [
            (label, FelixMarboutin.NORMALS[label]["normalvector"]) for label in labels
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
            di = DirectSolarIrradianceLib.multiple_direct_irradiance(
                pairs, dts, gdf=gdf, model=model
            )
            for label, _ in pairs:
                row[label] = di[label].sum()
            rows.append(row)

        df = DataFrame(rows)
        df["day_of_year"] = df.timestamp.dt.dayofyear

        # PLOTTING
        fig, ax = plt.subplots(figsize=(8.26, 0.55 * 8.26))
        fig.suptitle(f"Direct Solar Irradiation, lat. {lat:+.1f}°N", size=20)
        ax.set_xlabel("Day of year", fontsize=14)
        ax.set_ylabel("Daily irradiation [kWh/m$^2$]", fontsize=14)
        ax.tick_params(axis="x", labelsize=14)
        ax.tick_params(axis="y", labelsize=14)

        for label, _ in pairs:
            mwh = day_step * df[label].sum() * 1e-6
            ax.plot(
                df.day_of_year,
                df[label] * 1e-3,
                linestyle=FelixMarboutin.NORMALS[label]["linestyle"],
                color=FelixMarboutin.NORMALS[label]["color"],
                linewidth=FelixMarboutin.NORMALS[label]["linewidth"],
                label=f"{label}: {mwh:.2f} MWh/m$^2$",
            )

        for month, label in [
            (3, "Spring\n\nequinox"),
            (6, "Summer\n\nsolstice"),
            (9, "Autumn\n\nequinox"),
            (12, "Winter\n\nsolstice"),
        ]:
            x0 = Timestamp(f"2025-{month}-21", tz="UTC").day_of_year
            ax.vlines(
                x=x0, ymin=-0.5, ymax=6, linestyle="-.", color="blue", linewidth=1
            )
            ax.text(
                x0,
                0,
                label,
                fontsize=12,
                rotation=90,
                color="blue",
                ha="center",
                va="bottom",
            )

        ax.legend(loc="upper left", framealpha=0.5, ncol=2, fontsize=14)

        if ofile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)
        return df


"""
days = [Timestamp(f"2025-{m}-21") for m in [3, 6, 12]]
days = [Timestamp(f"2025-{m}-21") for m in [12, 3, 6]]

labels=["Roof", "N", "S", "E", "W"]
labels=["Roof", "NE", "NW", "SW", "SE"]
labels=["Roof", "N", "S", "E", "W", "NE", "NW", "SW", "SE"]

di = FelixMarboutin.daily(days, labels, pivot=False, ofile=None)
di = FelixMarboutin.daily(days, labels, pivot=True, ofile=None)
di = FelixMarboutin.annual(labels, ofile=None)
"""
