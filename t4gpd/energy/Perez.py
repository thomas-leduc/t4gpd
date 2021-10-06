'''
Created on 25 aug 2020

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
from numpy import cos, pi, sin


class Perez(object):
    '''
    classdocs
    voir ~/prj/solenetb/src/trunk/solene.core.orig/luminance_ciel.c
    irradiance du rayonnement solaire extra-atmospherique sur une surface perpendiculaire au rayon
    '''
    SOLAR_CONSTANT = 1367.0
    '''
    http://atmospheres.gsfc.nasa.gov/climate/index.php?section=136
    The total solar irradiance (TSI), improperly called "solar constant" until a few years ago,
    has been found to change about 0.1% in an 11-year solar sunspot activity. The current most
    accurate TSI values from the Total Irradiance Monitor (TIM) on NASA's Solar Radiation and
    Climate Experiment ( SORCE ) is 1360.8 +/- 0.5 W/m2 during the 2008 solar minimum as compared
    to previous estimates of 1365.4 +/- 1.3 W/m2 established in the 1990s.
    '''
    TOTAL_SOLAR_IRRADIANCE = 1360.8

    @staticmethod
    def __dogniauxOpticalAirMass(solarAltitudeAngle):
        # ~ https://en.wikipedia.org/wiki/Air_mass_%28astronomy%29
        # ~ d'apres (Miguet, 2000; p. 164)
        y = (3.885 + solarAltitudeAngle) ** (-1.253)
        z = sin(solarAltitudeAngle)
        return (1.0 / (z + 0.15 * y))

    @staticmethod
    def __eccentricity(dayInYear):
        # ~ d'apres (Miguet, 2000; p. 162)
        k = (2 * pi * (dayInYear - 1)) / 365.0
        return (1.00011 + 0.034221 * cos(k) + 0.00128 * sin(k) + 0.000719 * cos(2 * k) + 0.000077 * sin(2 * k))

    @staticmethod
    def diffuseSolarIrradiance(solarAltitudeAngle, dayInYear, delta):
        # ~ delta: sky's brightness (Perez et al., 1993)
        airMass = Perez.__dogniauxOpticalAirMass(solarAltitudeAngle)
        eccentricity = Perez.__eccentricity(dayInYear)
        return ((delta * Perez.SOLAR_CONSTANT * eccentricity) / airMass)

    @staticmethod
    def directSolarIrradiance(solarAltitudeAngle, dayInYear, delta, epsilon):
        # ~ delta: sky's brightness (Perez et al., 1993)
        # ~ epsilon: sky's clearness (Perez et al., 1993)
        de = Perez.diffuseSolarIrradiance(solarAltitudeAngle, dayInYear, delta)
        z = pi / 2.0 - solarAltitudeAngle
        return de * (epsilon - 1.0) * (1.0 + 1.041 * z ** 3)
