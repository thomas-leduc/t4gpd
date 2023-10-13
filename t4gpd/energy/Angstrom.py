'''
Created on 3 oct 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from numpy import exp


class Angstrom(object):
    '''
    classdocs

    http://dx.doi.org/10.1016/j.buildenv.2014.05.019
    Stephane Boltzmann's constant [W . m^-2 . K^-4]
    '''

    BOLTZMANN_CONSTANT = 5.67e-8

    @staticmethod
    def __vapor_pressure(Tair, RH):
        '''
        IN:
            Tair: Dry bulb temperature [C]
            RH: Relative humidity 0-100 [%]
        OUT:
            Water vapor pressure [hPa]

        http://dx.doi.org/10.1016/j.buildenv.2014.05.019

        section 2.2: Long-wave radiation from the atmosphere
        The vapor pressure Vp [hPa] can be computed using the Arden Buck equation
        '''
        return RH * 6.1121 * exp((18.678 - Tair / 234.4) * (Tair / (257.14 + Tair)))

    @staticmethod
    def lowg_wave_irradiance(Tair, RH, N):
        '''
        IN:
            Tair: Dry bulb temperature [C]
            RH: Relative humidity 0-100 [%]
            N: Degree of cloudiness [Octas]
        OUT:
            Downward atmospheric long-wave irradiance [W . m^-2]

        http://dx.doi.org/10.1016/j.buildenv.2014.05.019

        section 2.2: Long-wave radiation from the atmosphere
        Atmospheric long-wave radiation can be estimated as a function of ambient air
        temperature, vapor pressure, and cloud cover using the Angstrom formula

        Sky conditions are estimated in terms of how many eighths of the sky are
        covered in cloud, ranging from 0 Octas (completely clear sky) through to
        8 Octas (completely overcast)
        '''
        Vp = Angstrom.__vapor_pressure(Tair, RH)
        return Angstrom.BOLTZMANN_CONSTANT * \
            (Tair + 273.15) ** 4 * \
            (0.82 - 0.25 * 10 ** (-0.0945 * Vp)) * \
            (1 + 0.21 * (N/8) ** 2.5)
