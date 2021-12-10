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


class DI(AbstractThermalComfortIndice):
    '''
    classdocs
    '''

    def __init__(self, sensorsGdf, AirTC='AirTC_Avg', RH='RH_Avg'):
        '''
        Constructor

        AirTC: air temperature [C]
        RH: relative humidity [%]

        DI: Discomfort Index stated in Coccolo et al. (2016) [C]
        '''
        if not isinstance(sensorsGdf, DataFrame):
            raise IllegalArgumentTypeException(sensorsGdf, 'DataFrame')

        for fieldname in (AirTC, RH):
            if fieldname not in sensorsGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)

        self.AirTC = AirTC
        self.RH = RH

    def runWithArgs(self, row):
        AirTC = row[self.AirTC]
        RH = row[self.RH]

        # DI: Discomfort Index stated in Coccolo et al. (2016) [C]
        DI = AirTC - 0.55 * (1 - 0.01 * RH) * (AirTC - 14.5)

        return { 'DI': DI }
