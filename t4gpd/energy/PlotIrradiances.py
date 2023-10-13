'''
Created on 3 oct 2023

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
from datetime import datetime
from numpy import linspace, pi
from t4gpd.energy.Angstrom import Angstrom
from t4gpd.energy.Dogniaux import Dogniaux
from t4gpd.energy.Perez import Perez
from t4gpd.energy.Perraudeau import Perraudeau
from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut


class PlotIrradiances(object):
    '''
    classdocs
    '''
    @staticmethod
    def plot1(dt=datetime(2021, 6, 21), ofile=None):
        # PEREZ MODEL PARAMETERS:
        delta = 0.12
        epsilon = 6.3
        dayInYear = dt.timetuple().tm_yday

        Xdeg, Xrad = linspace(0, 90, 91), linspace(0, pi/2, 91)

        y1 = [Dogniaux.directNormalIrradiance(x) for x in Xrad]
        y2 = [Perez.directSolarIrradiance(
            x, dayInYear, delta, epsilon) for x in Xrad]
        y3 = [Perraudeau.directNormalIrradiance(x) for x in Xrad]
        y4 = [PerrinDeBrichambaut.directNormalIrradiance(
            x, skyType=PerrinDeBrichambaut.PURE_SKY) for x in Xrad]
        y5 = [PerrinDeBrichambaut.directNormalIrradiance(
            x, skyType=PerrinDeBrichambaut.STANDARD_SKY) for x in Xrad]
        y6 = [PerrinDeBrichambaut.directNormalIrradiance(
            x, skyType=PerrinDeBrichambaut.POLLUTED_SKY) for x in Xrad]
        y7 = [Perez.diffuseSolarIrradiance(x, dayInYear, delta) for x in Xrad]
        y8 = [PerrinDeBrichambaut.diffuseSolarIrradiance(
            x, skyType=PerrinDeBrichambaut.PURE_SKY) for x in Xrad]
        y9 = [PerrinDeBrichambaut.diffuseSolarIrradiance(
            x, skyType=PerrinDeBrichambaut.STANDARD_SKY) for x in Xrad]
        ya = [PerrinDeBrichambaut.diffuseSolarIrradiance(
            x, skyType=PerrinDeBrichambaut.POLLUTED_SKY) for x in Xrad]

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        ax.set_title(
            "Direct Normal Irradiance (DNI) + Diffuse Horizontal Irradiance (DHI)", fontsize=16)
        ax.set_xlabel("Solar Altitude Angle [$^o$]", fontsize=16)
        ax.set_ylabel("Irradiance [W.m$^{-2}$]", fontsize=16)
        ax.set_ylim(0, 1200)
        ax.grid(True)
        _lines = ax.plot(Xdeg, y1, "b-", Xdeg, y2, "r-", Xdeg, y3, "k-", Xdeg, y4, "m-.",
                         Xdeg, y5, "g-.", Xdeg, y6, "c-.", Xdeg, y7, "r--", Xdeg, y8, "m--",
                         Xdeg, y9, "g--", Xdeg, ya, "c--")
        ax.legend(_lines, ["Dogniaux's DNI", "Perez's DNI", "Perraudeau's DNI",
                           "Perrin de Br.'s DNI (Pure sky)",
                           "Perrin de Br.'s DNI (Standard sky)",
                           "Perrin de Br.'s DNI (Polluted sky)",
                           "Perez's diffuse model",
                           "Perrin de Br.'s diffuse model (Pure sky)",
                           "Perrin de Br.'s diffuse model (Standard sky)",
                           "Perrin de Br.'s diffuse model (Polluted sky)"
                           ], loc="upper center", ncol=2, fontsize=12)
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

    @staticmethod
    def plot2(ofile=None):
        Xdeg, Xrad = linspace(0, 90, 91), linspace(0, pi/2, 91)
        Y1 = [PerrinDeBrichambaut.directNormalIrradiance(
            x, skyType=PerrinDeBrichambaut.STANDARD_SKY) for x in Xrad]
        Y2 = [PerrinDeBrichambaut.diffuseSolarIrradiance(
            x, skyType=PerrinDeBrichambaut.STANDARD_SKY) for x in Xrad]

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        ax.set_ylim(0, 1200)
        ax.set_xlabel("Solar altitude angle [$^o$]", fontsize=20)
        ax.set_ylabel("Irradiance [W.m$^{-2}$]", fontsize=20)
        ax.grid(True)
        ax.plot(Xdeg, Y1, label="Direct Normal Irradiance (DNI)",
                linestyle="dotted", linewidth=3, color="black")
        ax.plot(Xdeg, Y2, label="Diffuse Horizontal Irradiance (DHI)",
                linestyle="dashdot", linewidth=3, color="black")

        nuples = [
            (20, 50, 8, "red", "solid"),
            (20, 50, 4, "green", "solid"),
            (20, 50, 0, "blue", "solid"),
            (30, 75, 8, "red", "dashed"),
            (30, 75, 4, "green", "dashed"),
            (30, 75, 0, "blue", "dashed"),
        ]
        for Tair, RH, N, color, ls in nuples:
            Y3 = [Angstrom.lowg_wave_irradiance(Tair, RH, N) for _ in Xdeg]
            ax.plot(
                Xdeg, Y3, label=f"LW from the atmos. (Ta={Tair:.0f}, RH={RH}%, N={N})", linestyle=ls, color=color)
        ax.legend()

        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)


# PlotIrradiances.plot1()
# PlotIrradiances.plot2()
