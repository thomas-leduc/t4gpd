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
from numpy import isnan
from pandas.core.frame import DataFrame
from t4gpd.comfort.algo.ETULib import ETULib
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class ETU(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg', WS_ms='WS_ms_Avg',
                 T_mrt='T_mrt', N='N', Albedo='Albedo_1_Avg', SRUp='SR01Up_1_Avg',
                 SRDn='SR01Dn_1_Avg', IRUp='IR01UpCo_1_Avg', IRDn='IR01DnCo_1_Avg'):
        '''
        Constructor

        AirTC: air temperature [C]
        RH: relative humidity [%]
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]
        T_mrt: Mean radiant temperature [C]
        N:
        Albedo:
        SRUp:
        SRDn:
        IRUp:
        IRDn:
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, RH, WS_ms, T_mrt, N, Albedo, SRUp, SRDn,
                          IRUp, IRDn):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.RH = RH
        self.WS_ms = WS_ms
        self.T_mrt = T_mrt

        self.N = N
        self.Albedo = Albedo
        self.SRUp, self.SRDn = SRUp, SRDn
        self.IRUp, self.IRDn = IRUp, IRDn

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]
        WS_ms = row[self.WS_ms]
        T_mrt = row[self.T_mrt]

        N = row[self.N]
        Albedo = row[self.Albedo]
        SRUp, SRDn = row[self.SRUp], row[self.SRDn]
        IRUp, IRDn = row[self.IRUp], row[self.IRDn]

        if (N is None) or isnan(N):
            return {
                'ETU': None,
                'dif_NUATF': None,
                'dif_SERFL': None,
                'dif_ERFS': None,
                'dif_SEHF': None,
                'dif_EVCF': None
                }

        ETU, dif_NUATF, dif_SERFL, dif_ERFS, dif_SEHF, dif_EVCF = ETULib.assess_etu(
            AirTC, RH, WS_ms, T_mrt, N, Albedo, SRUp, SRDn, IRUp, IRDn)

        return {
            'ETU': ETU,
            'dif_NUATF': dif_NUATF,
            'dif_SERFL': dif_SERFL,
            'dif_ERFS': dif_ERFS,
            'dif_SEHF': dif_SEHF,
            'dif_EVCF': dif_EVCF
            }
