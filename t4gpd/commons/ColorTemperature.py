'''
Created on 23 juin 2023

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
from numpy import log, power


class ColorTemperature(object):
    '''
    classdocs
    '''

    @staticmethod
    def convert_K_to_RGB(colour_temperature):
        """
        Converts from K to RGB, algorithm courtesy of 
        http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
        https://gist.github.com/petrklus/b1f427accdf7438606a6
        """
        def setMinMax(value, minValue, maxValue): return min(
            max(value, minValue), maxValue)

        # range check
        colour_temperature = setMinMax(colour_temperature, 1000, 40000)
        tmp_internal = colour_temperature / 100.0

        # red
        if tmp_internal <= 66:
            red = 255
        else:
            red = 329.698727446 * power(tmp_internal - 60, -0.1332047592)
            red = setMinMax(red, 0, 255)

        # green
        if tmp_internal <= 66:
            green = 99.4708025861 * log(tmp_internal) - 161.1195681661
        else:
            green = 288.1221695283 * power(tmp_internal - 60, -0.0755148492)
        green = setMinMax(green, 0, 255)

        # blue
        if tmp_internal >= 66:
            blue = 255
        elif tmp_internal <= 19:
            blue = 0
        else:
            blue = 138.5177312231 * \
                log(tmp_internal - 10) - 305.0447927307
            blue = setMinMax(blue, 0, 255)

        # return red, green, blue
        return int(round(red)), int(round(green)), int(round(blue))
