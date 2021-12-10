'''
Created on 11 mai 2021

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
from pandas.core.frame import DataFrame
from t4gpd.comfort.algo.WindSpeedExtrapolationLib import WindSpeedExtrapolationLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice


class WCT(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', WS_ms='WS_ms_Avg'):
        '''
        Constructor

        AirTC: air temperature [C]
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]

        According to Coccolo et al. (2016), the Wind Chill Temperature (WCT)
        considers the cooling power of wind by taking into account the wind 
        speed at a height of 10 m (m.s-1). It can be applied to analyze the 
        thermal comfort in a cold environment (Coccolo et al., 2016)
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, WS_ms):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.WS_ms = WS_ms

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        WS_ms = row[self.WS_ms]

        # Calculation of wind speed in 10 m - extrapolation of wind speed in 1.1 m 
        # after Lam et al. (2018)
        WS_ms_10 = WindSpeedExtrapolationLib.windSpeedExtrapolation(WS_ms)
        _ws_tmp = WS_ms_10 ** 0.16

        # Wind Chill Temperature (WCT) stated in Coccolo et al. (2016) [C]
        WCT = 13.12 + 0.6215 * AirTC - 11.37 * _ws_tmp + 0.3965 * AirTC * _ws_tmp

        return { 'WCT': WCT }
