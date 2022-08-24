'''
Created on 25 aug. 2020

@author: tleduc

Copyright 2020 Thomas Leduc

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
from datetime import datetime

from t4gpd.commons.AngleLib import AngleLib

import matplotlib.pyplot as plt
from numpy  import arange
from t4gpd.energy.Dogniaux import Dogniaux
from t4gpd.energy.Perez import Perez
from t4gpd.energy.Perraudeau import Perraudeau
from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut


class PlotDirectNormalIrradiance(object):
    '''
    classdocs
    '''

    @staticmethod
    def plot(dt=datetime(2020, 3, 21), ofile=None):
        # PEREZ MODEL PARAMETERS:
        delta = 0.12
        epsilon = 6.3
        dayInYear = dt.timetuple().tm_yday

        xDeg = arange(0, 91, 1)
        xRad = AngleLib.toRadians(xDeg)

        y1 = [Dogniaux.directNormalIrradiance(x) for x in xRad]
        y2 = [Perez.directSolarIrradiance(x, dayInYear, delta, epsilon) for x in xRad]
        y3 = [Perraudeau.directNormalIrradiance(x) for x in xRad]
        y4 = [PerrinDeBrichambaut.directNormalIrradiance(x, skyType=PerrinDeBrichambaut.PURE_SKY) for x in xRad]
        y5 = [PerrinDeBrichambaut.directNormalIrradiance(x, skyType=PerrinDeBrichambaut.STANDARD_SKY) for x in xRad]
        y6 = [PerrinDeBrichambaut.directNormalIrradiance(x, skyType=PerrinDeBrichambaut.POLLUTED_SKY) for x in xRad]
        y7 = [Perez.diffuseSolarIrradiance(x, dayInYear, delta) for x in xRad]
        y8 = [PerrinDeBrichambaut.diffuseSolarIrradiance(x, skyType=PerrinDeBrichambaut.PURE_SKY) for x in xRad]
        y9 = [PerrinDeBrichambaut.diffuseSolarIrradiance(x, skyType=PerrinDeBrichambaut.STANDARD_SKY) for x in xRad]
        ya = [PerrinDeBrichambaut.diffuseSolarIrradiance(x, skyType=PerrinDeBrichambaut.POLLUTED_SKY) for x in xRad]

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        ax.set_title('Direct Normal Irradiance (DNI) + Diffuse Solar Irradiance', fontsize=16)
        ax.set_xlabel('Solar Altitude Angle', fontsize=16)
        ax.set_ylabel('Solar Irradiance [W.m$^{-2}$]', fontsize=16)
        ax.set_ylim(0, 1200)
        ax.grid(True)
        _lines = ax.plot(xDeg, y1, 'b-', xDeg, y2, 'r-', xDeg, y3, 'k-', xDeg, y4, 'm-.',
                         xDeg, y5, 'g-.', xDeg, y6, 'c-.', xDeg, y7, 'r--', xDeg, y8, 'm--',
                         xDeg, y9, 'g--', xDeg, ya, 'c--')
        ax.legend(_lines, ["Dogniaux's DNI", "Perez's DNI", "Perraudeau's DNI",
                           "Perrin de Br.'s DNI (Pure sky)",
                           "Perrin de Br.'s DNI (Standard sky)",
                           "Perrin de Br.'s DNI (Polluted sky)",
                           "Perez's diffuse model",
                           "Perrin de Br.'s diffuse model (Pure sky)",
                           "Perrin de Br.'s diffuse model (Standard sky)",
                           "Perrin de Br.'s diffuse model (Polluted sky)"
                           ], loc='upper center', ncol=2, fontsize=12)
        if ofile is None:
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches='tight')
        plt.close(fig)


# PlotDirectNormalIrradiance.plot(ofile='/tmp/irrad.pdf')
