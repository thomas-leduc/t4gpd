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
from t4gpd.comfort.algo.TmrtGlobeTemperatureLib import TmrtGlobeTemperatureLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice


class TmrtGlobeTemperature(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='Temperature', GlobeTC='GlobeTemperature',
                 WS_ms='WindSpeed'):
        '''
        Constructor

        AirTC: air temperature [C]
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, GlobeTC, WS_ms):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.GlobeTC = GlobeTC
        self.WS_ms = WS_ms

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        GlobeTC = row[self.GlobeTC]
        WS_ms = row[self.WS_ms]

        # calculation of the mean radiant temperature [C]
        # Mean radiant temperature after (Thorsson et al., 2007) based on observed globe temperature:
        T_mrt = TmrtGlobeTemperatureLib.assess_tmrt(AirTC, GlobeTC, WS_ms)

        return { 'T_mrt': T_mrt }
