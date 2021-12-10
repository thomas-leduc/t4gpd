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
from pythermalcomfort.models import set_tmp
try:
    from pythermalcomfort.psychrometrics import v_relative
except ImportError:
    from pythermalcomfort.utilities import v_relative

from t4gpd.comfort.algo.ConstantsLib import ConstantsLib


class SETLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def assess_set(AirTC, RH, WS_ms, T_mrt):
        # https://pythermalcomfort.readthedocs.io

        # Estimates the relative air speed which combines the average air speed of the
        # space plus the relative air speed caused by the body movement.
        vr = v_relative(WS_ms, ConstantsLib.M_met)

        # Calculates the Standard Effective Temperature (SET). The SET is the temperature 
        # of an imaginary environment at 50% (rh), <0.1 m/s (20 fpm) average air speed (v),
        # and tr = tdb , in which the total heat loss from the skin of an imaginary 
        # occupant with an activity level of 1.0 met and a clothing level of 0.6 clo is the
        # same as that from a person in the actual environment with actual clothing and 
        # activity level.
        tdb, tr, v, rh, met, clo = (AirTC, T_mrt, vr, RH, ConstantsLib.M_met, ConstantsLib.Clo)
        SET = set_tmp(tdb, tr, v, rh, met, clo, wme=0,
                      body_surface_area=1.8258, p_atm=101325,
                      units='SI')
        return SET
