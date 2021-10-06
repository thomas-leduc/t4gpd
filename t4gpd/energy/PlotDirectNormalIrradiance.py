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
from t4gpd.energy.Dogniaux import Dogniaux
from t4gpd.energy.Perez import Perez
from t4gpd.energy.Perraudeau import Perraudeau
from t4gpd.energy.PerrinDeBrichambaut import PerrinDeBrichambaut


class PlotDirectNormalIrradiance(object):
    '''
    classdocs
    '''
    @staticmethod
    def plot(dt=datetime(2020, 3, 21)):
        # PEREZ MODEL PARAMETERS:
        delta = 0.12
        epsilon = 6.3
        dayInYear = dt.timetuple().tm_yday

        mainFig = plt.figure(1)
        mainFig.clear()

        x = list(range(0, 91, 1))

        y1 = [Dogniaux.directNormalIrradiance(AngleLib.toRadians(_x)) for _x in x]
        y2 = [Perez.directSolarIrradiance(AngleLib.toRadians(_x), dayInYear, delta, epsilon) for _x in x]
        y3 = [Perraudeau.directNormalIrradiance(AngleLib.toRadians(_x)) for _x in x]
        y4 = [PerrinDeBrichambaut.directNormalIrradiance(AngleLib.toRadians(_x), skyType=PerrinDeBrichambaut.PURE_SKY) for _x in x]
        y5 = [PerrinDeBrichambaut.directNormalIrradiance(AngleLib.toRadians(_x), skyType=PerrinDeBrichambaut.STANDARD_SKY) for _x in x]
        y6 = [PerrinDeBrichambaut.directNormalIrradiance(AngleLib.toRadians(_x), skyType=PerrinDeBrichambaut.POLLUTED_SKY) for _x in x]

        plt.title('Direct Normal Irradiance')
        plt.xlabel('Solar Altitude Angle')
        plt.ylabel('Direct Normal Irradiance (W/m2)')
        plt.grid(True)
        _d, _p1, _p2, _pdb_c, _pdb_s, _pdb_p = plt.plot(x, y1, 'b-', x, y2, 'c-', x, y3, 'k-', x, y4, 'm--', x, y5, 'g--', x, y6, 'r--')
        plt.legend((_d, _p1, _p2, _pdb_c, _pdb_s, _pdb_p), (
            'Dogniaux\'s model',
            'Perez\'s model',
            'Perraudeau\'s model',
            'Perrin de Brichambaut\'s model (Pure sky)',
            'Perrin de Brichambaut\'s model (Standard sky)',
            'Perrin de Brichambaut\'s model (Polluted sky)',
        ))
        plt.show()

# PlotDirectNormalIrradiance.plot()
