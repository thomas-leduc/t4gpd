"""
Created on 11 Feb. 2025

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

from datetime import date, timedelta
from numpy import deg2rad
from locale import LC_ALL, setlocale
from pandas import DatetimeIndex, Timestamp, date_range
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.LatLonLib import LatLonLib
from t4gpd.commons.sun.SunModel import SunModel

import matplotlib.pyplot as plt


class SunModelPlotting(object):
    """
    classdocs
    """

    @staticmethod
    def __latlon_to_str(gdf):
        lat, lon = LatLonLib.fromGeoDataFrameToLatLon(gdf)
        lat = LatLonLib.sexagesimalDegreePrettyPrinter(
            LatLonLib.decimalDegree2sexagesimalDegree(lat), opt="latitude"
        )
        lon = LatLonLib.sexagesimalDegreePrettyPrinter(
            LatLonLib.decimalDegree2sexagesimalDegree(lon), opt="longitude"
        )
        return f"{lat}, {lon}"

    @staticmethod
    def __every_n_days(gdf, altitude, year, tz, step=5):
        N = SunModel.ndays_per_year(year)
        dt0 = Timestamp(f"{year}-01-01")
        daysInYear = range(0, N + 1, step)
        every_n_days = DatetimeIndex([dt0 + timedelta(days=n) for n in daysInYear])

        sun_model = SunModel(gdf, altitude)
        return N, daysInYear, sun_model.sun_rise_set(every_n_days, tz=tz)

    @staticmethod
    def __plot_per_day_of_year(gdf, year, tz, title, y0):
        fig, ax = plt.subplots(figsize=(1.2 * 8.26, 0.9 * 8.26))

        latlon = SunModelPlotting.__latlon_to_str(gdf)
        ax.set_title(f"{title}: {latlon}", fontsize=16)
        ax.set_xlim(0, 365)
        ax.set_xlabel("Day of year", fontsize=16)

        PAIRS = [
            (3, "Spring equinox"),
            (6, "Summer solstice"),
            (9, "Autumn equinox"),
            (12, "Winter solstice"),
        ]
        for month, label in PAIRS:
            x0 = Timestamp(f"{year}-{month}-21 12:00", tz=tz).day_of_year
            ax.axvline(x=x0, linestyle="dashdot", color="red", linewidth=1)
            ax.text(
                x0 - 10,
                y0,
                label,
                fontsize=16,
                rotation=90,
                color="red",
                ha="center",
                va="center",
            )
        ax.grid()
        return fig, ax

    @staticmethod
    def polar(
        gdf=LatLonLib.NANTES,
        altitude=0,
        models=["circular", "pvlib"],
        year=date.today().year,
        tz="UTC",
        ofile=None,
    ):
        solstices_equinox = DatetimeIndex(
            [
                Timestamp(f"{year}-03-21"),
                Timestamp(f"{year}-06-21"),
                Timestamp(f"{year}-12-21"),
            ]
        )

        ncols = len(models)
        fig, axes = plt.subplots(
            figsize=(1.2 * 8.26, 0.7 * 8.26),
            nrows=1,
            ncols=ncols,
            squeeze=False,
            subplot_kw={"projection": "polar"},
        )
        latlon = SunModelPlotting.__latlon_to_str(gdf)
        fig.suptitle(f"Polar diagram: {latlon}", fontsize=20)

        for nc, model in enumerate(models):
            sun_model = SunModel(gdf, altitude, model=model)
            sun_rise_set = sun_model.sun_rise_set(solstices_equinox, tz=tz)

            ax = axes[0, nc]
            # ax.set_title(model, pad=30)

            # NORTH IS ON TOP
            ax.set_theta_zero_location("N")
            # CLOCKWISE
            ax.set_theta_direction(-1)
            # LABEL POSITIONS
            # ax.set_rlabel_position(0)
            ax.set_ylim(0, 90)

            for month, color in [(3, "green"), (6, "red"), (12, "blue")]:
                day = Timestamp(f"{year}-{month}-21")
                sunrise = sun_rise_set.loc[day, "sunrise"]
                sunset = sun_rise_set.loc[day, "sunset"]
                dts = date_range(sunrise, sunset, freq="10min", tz=tz)
                df = sun_model.positions(dts)
                ax.plot(deg2rad(df.azimuth), 90 - df.elevation, color=color)

            for hour in range(6, 19, 2):
                start = Timestamp(f"{year}-01-01 {hour:02d}:00")
                end = Timestamp(f"{year}-12-31 {hour:02d}:00")
                dts = date_range(start, end, freq="5D")
                df = sun_model.positions(dts)
                ax.plot(
                    deg2rad(df.azimuth),
                    90 - df.elevation,
                    color="brown",
                    linewidth=1.05,
                    linestyle="solid",
                )

            ax.set_rgrids(range(0, 90, 10), labels=[f"{a}°" for a in range(90, 0, -10)])
            ax.set_thetagrids(
                range(0, 360, 15), labels=[f"{a}°" for a in range(0, 360, 15)]
            )
        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def solar_altitude_at_noon(
        gdf=LatLonLib.NANTES,
        altitude=0,
        models=["pvlib", "circular"],
        year=date.today().year,
        tz="UTC",
        ofile=None,
    ):
        # CALCULATIONS
        N = SunModel.ndays_per_year(year)
        dt0 = Timestamp(f"{year}-01-01 12")
        daysInYear = range(0, N + 1, 5)
        every_n_days = DatetimeIndex([dt0 + timedelta(days=n) for n in daysInYear])

        for nc, model in enumerate(models):
            sun_model = SunModel(gdf, altitude, model=model)
            sunpos = sun_model.positions(every_n_days)

            fieldname = "apparent_elevation" if (model == "pvlib") else "elevation"

            if (0 == nc):
                # PLOTTING
                ymin, ymax = sunpos[fieldname].min(), sunpos[fieldname].max()
                y0 = ymin + 0.5 * (ymax - ymin)

                fig, ax = SunModelPlotting.__plot_per_day_of_year(
                    gdf, year, tz, "Solar at noon", y0
                )
                ax.set_ylabel("Solar altitude at noon [°]", fontsize=16)
            ax.plot(daysInYear, sunpos[fieldname], label=model)

        if (1 == nc):
            ax.legend(fontsize=14)
        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def sunrise_sunset(
        gdf=LatLonLib.NANTES,
        altitude=0,
        year=date.today().year,
        tz="UTC",
        ofile=None,
    ):
        # CALCULATIONS
        N, daysInYear, sun_rise_set = SunModelPlotting.__every_n_days(
            gdf, altitude, year, tz, step=10
        )
        sun_rise_set["sunrise_hr"] = (
            sun_rise_set.sunrise.dt.hour + sun_rise_set.sunrise.dt.minute / 60
        )
        sun_rise_set["sunset_hr"] = (
            sun_rise_set.sunset.dt.hour + sun_rise_set.sunset.dt.minute / 60
        )

        # PLOTTING
        ymin, ymax = sun_rise_set.sunrise_hr.min(), sun_rise_set.sunset_hr.max()
        y0 = ymin + 0.5 * (ymax - ymin)

        fig, ax = SunModelPlotting.__plot_per_day_of_year(
            gdf, year, tz, "Sunrise/sunset", y0
        )
        ax.set_ylabel(f"Time ({tz})", fontsize=16)
        ax.plot(daysInYear, sun_rise_set.sunrise_hr, daysInYear, sun_rise_set.sunset_hr)
        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def day_lengths(
        gdf=LatLonLib.NANTES,
        altitude=0,
        year=date.today().year,
        tz="UTC",
        ofile=None,
    ):
        # CALCULATIONS
        N, daysInYear, sun_rise_set = SunModelPlotting.__every_n_days(
            gdf, altitude, year, tz, step=5
        )
        sun_rise_set["day_length"] = (
            sun_rise_set.sunset.dt.hour + sun_rise_set.sunset.dt.minute / 60
        ) - (sun_rise_set.sunrise.dt.hour + sun_rise_set.sunrise.dt.minute / 60)

        # PLOTTING
        ymin, ymax = sun_rise_set.day_length.min(), sun_rise_set.day_length.max()
        y0 = ymin + 0.5 * (ymax - ymin)

        fig, ax = SunModelPlotting.__plot_per_day_of_year(
            gdf, year, tz, "Daylight hours", y0
        )
        ax.set_ylabel("Daylight hours", fontsize=16)
        ax.plot(daysInYear, sun_rise_set.day_length)

        ymin, ymax = sun_rise_set.day_length.min(), sun_rise_set.day_length.max()
        y0 = ymin + 0.5 * (ymax - ymin)
        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def solar_panorama(
        gdf=LatLonLib.NANTES,
        altitude=0,
        models=["pvlib"],
        # models=["circular", "pvlib"],
        year=date.today().year,
        tz="UTC",
        ofile=None,
    ):
        # CALCULATIONS
        solstices_equinox = DatetimeIndex(
            [Timestamp(f"{year}-{month:02d}-21") for month in [3, 6, 12]]
        )

        solstices_equinox_2 = DatetimeIndex(
            [
                Timestamp(f"{year}-{month:02d}-21 {hour:02d}")
                for month in [12, 3, 6]
                for hour in [8, 10, 12, 14, 16]
            ]
        )

        # PLOTTING
        ncols = len(models)
        fig, axes = plt.subplots(
            figsize=(ncols * 0.9 * 8.26, 0.9 * 8.26),
            nrows=1,
            ncols=ncols,
            squeeze=False,
        )

        latlon = SunModelPlotting.__latlon_to_str(gdf)
        fig.suptitle(f"Solar panorama: {latlon}", fontsize=16)

        for nc, model in enumerate(models):
            sun_model = SunModel(gdf, altitude, model=model)
            sun_rise_set = sun_model.sun_rise_set(solstices_equinox, tz=tz)
            sun_positions2 = sun_model.positions(solstices_equinox_2)

            ax = axes[0, nc]
            # ax.set_title(model, pad=30)

            for month, color in [(3, "green"), (6, "red"), (12, "blue")]:
                day = Timestamp(f"{year}-{month}-21")
                setlocale(LC_ALL, "en_US.utf8")
                label = day.strftime("%b. %d")
                sunrise = sun_rise_set.loc[day, "sunrise"]
                sunset = sun_rise_set.loc[day, "sunset"]
                dts = date_range(sunrise, sunset, freq="10min", tz=tz)
                df = sun_model.positions(dts)
                if "apparent_elevation" in df:
                    ax.plot(df.azimuth, df.apparent_elevation, color=color, label=label)
                else:
                    ax.plot(df.azimuth, df.elevation, color=color, label=label)

            for hour in [8, 10, 12, 14, 16]:
                azimuths = sun_positions2[
                    sun_positions2.index.hour == hour
                ].azimuth.to_list()
                if "apparent_elevation" in sun_positions2:
                    elevations = sun_positions2[
                        sun_positions2.index.hour == hour
                    ].apparent_elevation.to_list()
                else:
                    elevations = sun_positions2[
                        sun_positions2.index.hour == hour
                    ].elevation.to_list()
                ax.plot(
                    azimuths,
                    elevations,
                    color="black",
                    linewidth=1.05,
                    linestyle="dashed",
                )
                ax.text(
                    (3 * azimuths[1] + azimuths[2]) / 4,
                    (3 * elevations[1] + elevations[2]) / 4,
                    f"{hour}:00",
                    fontsize=9,
                ).set_color("black")
            ax.legend()
            ax.grid()
            ax.set_ylim(0, 90)
            ax.set_xlabel("Solar azimuth [°]", fontsize=16)
            ax.set_ylabel("Solar altitude [°]", fontsize=16)

        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def solar_panorama_2(
        gdf=LatLonLib.NANTES,
        altitude=0,
        models=["pvlib"],
        # models=["circular", "pvlib"],
        year=date.today().year,
        tz="UTC",
        ofile=None,
    ):
        # CALCULATIONS
        solstices_equinox = DatetimeIndex(
            [Timestamp(f"{year}-{month:02d}-21") for month in [3, 6, 12]]
        )

        # PLOTTING
        ncols = len(models)
        fig, axes = plt.subplots(
            figsize=(ncols * 0.9 * 8.26, 0.9 * 8.26),
            nrows=1,
            ncols=ncols,
            squeeze=False,
        )

        latlon = SunModelPlotting.__latlon_to_str(gdf)
        fig.suptitle(f"Solar panorama: {latlon}", fontsize=16)

        for nc, model in enumerate(models):
            sun_model = SunModel(gdf, altitude, model=model)
            sun_rise_set = sun_model.sun_rise_set(solstices_equinox, tz=tz)

            ax = axes[0, nc]
            # ax.set_title(model, pad=30)

            for month, color in [(3, "green"), (6, "red"), (12, "blue")]:
                day = Timestamp(f"{year}-{month}-21")
                setlocale(LC_ALL, "en_US.utf8")
                label = day.strftime("%b. %d")
                sunrise = sun_rise_set.loc[day, "sunrise"]
                sunset = sun_rise_set.loc[day, "sunset"]
                dts = date_range(sunrise, sunset, freq="10min", tz=tz)
                df = sun_model.positions(dts)
                df["hour"] = df.index.hour + df.index.minute / 60
                if "apparent_elevation" in df:
                    ax.plot(df.hour, df.apparent_elevation, color=color, label=label)
                else:
                    ax.plot(df.hour, df.elevation, color=color, label=label)

            ax.legend()
            ax.grid()
            ax.set_ylim(0, 90)
            ax.set_xlabel(f"Daylight hours ({tz})", fontsize=16)
            ax.set_ylabel("Solar altitude [°]", fontsize=16)

        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def isochrones(
        attribute,
        gdf=LatLonLib.NANTES,
        altitude=0,
        models=["pvlib"],
        # models=["circular", "pvlib"],
        year=date.today().year,
        tz="UTC",
        ofile=None,
    ):
        # CALCULATIONS
        MINUTES, HOURS = range(0, 60, 3), range(1, 24)
        # DAYS, MONTHS = [21, 11, 1], range(12, 0, -1)
        DAYS, MONTHS = range(28, 0, -1), range(12, 0, -1)

        every_timestep = DatetimeIndex(
            [
                Timestamp(f"{year}-{month}-{day} {hour:02d}:{minute:02d}", tz="UTC")
                for month in MONTHS
                for day in DAYS
                for hour in HOURS
                for minute in MINUTES
            ]
        )

        sun_model = SunModel(gdf, altitude)
        if attribute == "elevation":
            df = sun_model.positions(every_timestep)
            vmax = 90
            matrix = df.apparent_elevation.to_numpy()
        elif attribute in ["ghi", "dni", "dhi"]:
            df = sun_model.clearsky_irradiances(every_timestep)
            vmax = 1000
            matrix = df[attribute].to_numpy()
        else:
            raise IllegalArgumentTypeException(
                attribute, "'elevation', 'ghi', 'dni', or 'dhi'"
            )

        matrix = matrix.reshape(len(DAYS) * len(MONTHS), -1)
        matrix[matrix < 0] = 0

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        img = ax.imshow(matrix, cmap="viridis", interpolation="nearest", vmax=vmax)
        ax.set_xticks(range(1, len(HOURS) * len(MINUTES), len(MINUTES)))
        ax.set_xticklabels(range(1, 1+len(HOURS)))
        ax.set_yticks(range(1, len(MONTHS) * len(DAYS), len(DAYS)))
        ax.set_yticklabels(range(1, 1+len(MONTHS)))
        fig.colorbar(img, ax=ax, shrink=0.6)

        x, y = range(matrix.shape[1]), range(matrix.shape[0])
        contours = ax.contour(x, y, matrix, levels=5, colors="white", linewidths=1)
        ax.clabel(contours, inline=True, fontsize=8, fmt="%.2f")

        fig.tight_layout()
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)
