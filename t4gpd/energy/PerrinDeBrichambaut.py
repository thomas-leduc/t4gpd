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
from numpy import exp, sin
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
        angle = AngleLib.toDegrees(solarAltitudeAngle)
        
        if (PerrinDeBrichambaut.PURE_SKY == skyType):
            angle = AngleLib.toRadians(angle + 1.0)
            return 1210.0 * exp(-1.0 / (6.0 * sin(angle)))

        elif (PerrinDeBrichambaut.STANDARD_SKY == skyType):
            # angle = Angle.toRadians(angle + 1.6)
            angle = AngleLib.toRadians(angle + 2.0)
            # return 1230.0 * exp(-1.0 / (3.8 * sin(angle)))
            return 1230.0 * exp(-1.0 / (4.0 * sin(angle)))

        elif (PerrinDeBrichambaut.POLLUTED_SKY == skyType):
            angle = AngleLib.toRadians(angle + 3.0)
            return 1260.0 * exp(-1.0 / (2.3 * sin(angle)))
