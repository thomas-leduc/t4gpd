'''
Created on 12 mai 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from t4gpd.comfort.algo.ConstantsLib import ConstantsLib


class TmrtGlobeTemperatureLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def assess_tmrt(AirTC, GlobeTC, WS_ms, GlobeEmissivity=ConstantsLib.epsi_glo,
                   GlobeDiameter=ConstantsLib.D_glo):
        # calculation of the mean radiant temperature [C]
        # Mean radiant temperature after (Thorsson et al., 2007) based on observed globe temperature:
        T_mrt = ((GlobeTC + ConstantsLib.T_kel) ** 4 + 
                 ((1.1e8 * WS_ms ** 0.6) / (GlobeEmissivity * GlobeDiameter ** 0.4)) * 
                 (GlobeTC - AirTC)) ** (1 / 4) - ConstantsLib.T_kel
        return T_mrt
