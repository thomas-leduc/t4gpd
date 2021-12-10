'''
Created on 3 feb. 2021

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
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice
from t4gpd.comfort.indices.ETU import ETU
from t4gpd.comfort.indices.PET import PET
from t4gpd.comfort.indices.PMV import PMV
from t4gpd.comfort.indices.PT import PT
from t4gpd.comfort.indices.SET import SET
from t4gpd.comfort.indices.SETmist import SETmist
from t4gpd.comfort.indices.TmrtOut import TmrtOut
from t4gpd.comfort.indices.UTCI import UTCI


class UniversalThermalIndices(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg', WS_ms='WS_ms_Avg', T_mrt='T_mrt',
                 N='N', Albedo='Albedo_1_Avg', SRUp='SR01Up_1_Avg', SRDn='SR01Dn_1_Avg',
                 IRUp='IR01UpCo_1_Avg', IRDn='IR01DnCo_1_Avg'):
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
        self.ops = [
            PET(sensorsGdf, AirTC, RH, WS_ms, T_mrt),
            PMV(sensorsGdf, AirTC, RH, WS_ms, T_mrt),
            PT(sensorsGdf, AirTC, RH, WS_ms, T_mrt),
            UTCI(sensorsGdf, AirTC, RH, WS_ms, T_mrt),
            SET(sensorsGdf, AirTC, RH, WS_ms, T_mrt),
            ETU(sensorsGdf, AirTC, RH, WS_ms, T_mrt, N, Albedo, SRUp, SRDn, IRUp, IRDn),
            TmrtOut(sensorsGdf, N, SRUp, SRDn, IRUp, IRDn),
            SETmist(sensorsGdf, AirTC, RH, WS_ms, T_mrt)
            ]

    def runWithArgs(self, row):
        result = dict()
        for op in self.ops:
            result.update(op.runWithArgs(row))
        return result
