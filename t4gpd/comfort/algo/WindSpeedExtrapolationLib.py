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
from numpy import log


class WindSpeedExtrapolationLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def windSpeedExtrapolation(WS_ms, h=10.0):
        '''
        Ws_ms: wind speed recorded at pedestrian level (at height 1.1 m) [m.s-1]

        Calculation of wind speed in h=10 m - extrapolation of wind speed in 1.1 m after Lam et al.(2018)
        '''
        # Ws_ms_10 Wind speed in h=10 m [m.s-1]
        WS_ms_10 = WS_ms * ((log(h / 0.01)) / (log(1.1 / 0.01)))
        # TODO: WS_ms_10 = WS_ms * (log(100 * h) / log(110))
        return WS_ms_10
