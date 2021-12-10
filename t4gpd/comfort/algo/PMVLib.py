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
from pythermalcomfort.models import pmv_ppd
try:
    from pythermalcomfort.psychrometrics import v_relative
except ImportError:
    from pythermalcomfort.utilities import v_relative
from t4gpd.comfort.algo.ConstantsLib import ConstantsLib


class PMVLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def assess_pmv(AirTC, RH, WS_ms, T_mrt):
        # https://pythermalcomfort.readthedocs.io

        # Estimates the relative air speed which combines the average air speed of the
        # space plus the relative air speed caused by the body movement.
        vr = v_relative(WS_ms, ConstantsLib.M_met)

        # The PMV is an index that predicts the mean value of the thermal sensation votes (self-
        # reported perceptions) of a large group of people on a sensation scale expressed from -3
        # to +3 corresponding to the categories "cold", "cool", "slightly cool", "neutral", 
        # "slightly warm", "warm", and "hot".
        tdb, tr, vr, rh, met, clo = (AirTC, T_mrt, vr, RH, ConstantsLib.M_met, ConstantsLib.Clo)
        _result = pmv_ppd(tdb, tr, vr, rh, met, clo, wme=0, standard='ISO', units='SI')

        return _result['pmv']
