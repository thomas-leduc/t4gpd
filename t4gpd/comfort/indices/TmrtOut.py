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
from t4gpd.comfort.algo.TmrtOutLib import TmrtOutLib
from t4gpd.comfort.indices.AbstractThermalComfortIndice import AbstractThermalComfortIndice
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class TmrtOut(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, N='N', SRUp='SR01Up_1_Avg', SRDn='SR01Dn_1_Avg',
                 IRUp='IR01UpCo_1_Avg', IRDn='IR01DnCo_1_Avg'):
        '''
        Constructor

        N:
        SRUp:
        SRDn:
        IRUp:
        IRDn:
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (N, SRUp, SRDn, IRUp, IRDn):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.N = N
        self.SRUp = SRUp
        self.SRDn = SRDn
        self.IRUp = IRUp
        self.IRDn = IRDn

    def runWithArgs(self, row):
        N = row[self.N]
        SRUp = row[self.SRUp]
        SRDn = row[self.SRDn]
        IRUp = row[self.IRUp]
        IRDn = row[self.IRDn]

        if (N is None) or isnan(N):
            return { 'Tmrt_OUT': None }

        # Tmrt_OUT: outdoor mean radiant temperature
        Tmrt_OUT = TmrtOutLib.assess_tmrt_out(N, SRUp, SRDn, IRUp, IRDn)

        return { 'Tmrt_OUT': Tmrt_OUT }
