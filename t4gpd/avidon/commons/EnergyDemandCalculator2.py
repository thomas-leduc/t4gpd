'''
Created on 4 mars 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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

from numpy import dot, matmul, multiply, vectorize
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.avidon.commons.AbstractEnergyDemand import AbstractEnergyDemand


class EnergyDemandCalculator2(AbstractEnergyDemand):
    '''
    classdocs
    '''

    def __init__(self, dt, D=None, S=None, E=None):
        '''
        Constructor
        '''
        super().__init__(D, S, E)
        if isinstance(dt, datetime):
            self.dt = dt
        else:
            raise IllegalArgumentTypeException(S, 'datetime')

        _eval_vector = vectorize(self.__eval)
        self.D = _eval_vector(self.D) / 100.0
        self.E = _eval_vector(self.E)
        self.S = _eval_vector(self.S) / 100.0

    def __eval(self, ch):
        h, w = self.dt.hour, self.dt.weekday()
        delta = lambda t: self._unitImpulse(t)
        rect = lambda t0, t1, t: self._indicatorFunction(t0, t1, t)
        snd = lambda x: self._randomVariates(x)
        # snd = lambda x: x
        return eval(ch) if isinstance(ch, str) else ch 

    def energyDemandOfITEquipment(self, C):
        return dot(matmul(self.D, multiply(self.S, C)), self.E)
