'''
Created on 28 sept. 2020

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
from numpy import arctan, cos, mean, sin, sum, pi


class SVFLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def svf1981(heights, widths):
        '''
        Based on:
        Oke, T. R. 1981. "Canyon geometry and the nocturnal heat island:Comparison of scale model and
        field observations." Journal of Climatology, 1 (237-254).

        Cited in:
        Swaid, Hanna. 1993. "The Role of Radiative-Convective Interaction in Creating the Microclimate 
        of Urban Street Canyons." Boundary-Layer Meteorology 64 (3): 231-59. doi:10.1007/BF00708965.
        '''
        tmp = [(cos(arctan(heights[i] / widths[i])) if (0.0 < widths[i]) else float('inf'))
               for i in range(len(widths))]
        return float(mean(tmp))

    @staticmethod
    def svf2018(heights, widths):
        '''
        Based on:
        Bernard, J., Bocher, E., Petit, G. and Palominos, S. (2018) "Sky View Factor Calculation in 
        Urban Context: Computational Performance and Accuracy Analysis of Two Open and Free GIS Tools.",
        Climate, 6(3), p. 60. doi: 10.3390/cli6030060.
        '''
        dpi = 2. * pi
        a = dpi / len(widths)
        tmp = [(sin(arctan(heights[i] / widths[i])) if (0.0 < widths[i]) else float('inf'))
               for i in range(len(widths))]
        # BUG DANS IBID. (eq. 4)
        # tmp = [a * x * x for x in tmp]
        tmp = [a * x for x in tmp]
        # print "svf = %.5f" % ((dpi - sum(tmp)) / dpi)
        return float((dpi - sum(tmp)) / dpi)
