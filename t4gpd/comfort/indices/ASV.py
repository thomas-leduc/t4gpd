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
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice


class ASV(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg', WS_ms='WS_ms_Avg',
                 SRUp='SR01Up_1_Avg'):
        '''
        Constructor

        ASV: Actual Sensetion Vote after Nikolopoulou (2004) stated in Coccolo et al. (2016) [-]

        AirTC: air temperature [C]
        RH: relative humidity [%]
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]
        SRUp: incoming shortwave radiation [W.m-2]
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, RH, WS_ms, SRUp):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.RH = RH
        self.WS_ms = WS_ms
        self.SRUp = SRUp

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]
        WS_ms = row[self.WS_ms]
        SRUp = row[self.SRUp]

        # ASV: Actual Sensetion Vote after (Grosdemouge, 2020, p.105)
        # https://tel.archives-ouvertes.fr/tel-03123710
        ASV = 0.049 * AirTC + 0.001 * SRUp - 0.051 * WS_ms + 0.014 * RH - 2.079

        # ASV: Actual Sensetion Vote after Nikolopoulou (2004) stated in Coccolo et al. (2016) [-]
        # ASV = 0.068 * AirTC + 0.0006 * SRUp - 0.107 * WS_ms - 0.002 * RH - 0.69
        return { 'ASV': ASV }
