'''
Created on 25 aug. 2020

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
from numpy import exp, pi, sin
from t4gpd.commons.AngleLib import AngleLib


class PerrinDeBrichambaut(object):
    '''
    classdocs

    Irradiance is understood as instantaneous density of solar radiation incident on a given
    surface, typically expressed in W/m2.

    Irradiation is the sum of irradiance over a time period (e.g. 1 hour, day, month, etc.)
    expressed in J/m2. However, in daily routine Wh/m2 are more commonly used.
    '''
    PURE_SKY = 0
    STANDARD_SKY = 1
    POLLUTED_SKY = 2

    @staticmethod
    def diffuseSolarIrradiance(solarAltitudeAngle, skyType=STANDARD_SKY):
        '''
        Ghodbane, M., & Boumeddane, B. (2016). Estimating solar radiation according to semi 
        empirical approach of Perrin de Brichambaut: application on several areas with different 
        climate in Algeria. International Journal of Energetica, 1(1), 20. 
        https://doi.org/10.47238/ijeca.v1i1.12
        '''
        assert (0 <= solarAltitudeAngle <= (pi / 2)), 'solarAltitudeAngle in radians!'

        if (PerrinDeBrichambaut.PURE_SKY == skyType):
            D = 0.75
        elif (PerrinDeBrichambaut.STANDARD_SKY == skyType):
            D = 1
        elif (PerrinDeBrichambaut.POLLUTED_SKY == skyType):
            D = 4 / 3

        return 125 * D * sin(solarAltitudeAngle) ** 0.4

    @staticmethod
    def directNormalIrradiance(solarAltitudeAngle, skyType=STANDARD_SKY):
        '''
        Direct Normal Irradiance is the amount of solar radiation received per unit area by a
        surface that is always held perpendicular (or normal) to the rays that come in a
        straight line from the direction of the sun at its current position in the sky.

        d'apres p.105 de :
        AFEDES. 1979. Memosol : Memento D'heliotechnique. ed. Editions Europeennes Thermique 
        et Industrie (EETI). Paris, France.

        et (Miguet, 2000; p. 168) :
        Eclairement energetique (W/m2) solaire direct et normal (pour une surface 
        perpendiculaire aux rayons solaires), en conditions d'insolation normales
        '''
        assert (0 <= solarAltitudeAngle <= (pi / 2)), 'solarAltitudeAngle in radians!'

        angle = AngleLib.toDegrees(solarAltitudeAngle)

        if (PerrinDeBrichambaut.PURE_SKY == skyType):
            A, B, C = 1210, 6, 1
        elif (PerrinDeBrichambaut.STANDARD_SKY == skyType):
            A, B, C = 1230, 4, 2
            # A, B, C = 1230, 3.8, 1.6
        elif (PerrinDeBrichambaut.POLLUTED_SKY == skyType):
            A, B, C = 1260, 2.3, 3

        return A * exp(-1 / (B * sin(AngleLib.toRadians(angle + C))))
