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


class Dogniaux(object):
    '''
    classdocs
    d'apres (Miguet, 2000; p. 170)
    '''
    SOLAR_CONSTANT = 1367.0
    '''
    http://atmospheres.gsfc.nasa.gov/climate/index.php?section=136
    The total solar irradiance (TSI), improperly called "solar constant" until a few years ago,
    has been found to change about 0.1% in an 11-year solar sunspot activity. The current most
    accurate TSI values from the Total Irradiance Monitor (TIM) on NASA's Solar Radiation and
    Climate Experiment (SORCE) is 1360.8 +/- 0.5 W/m2 during the 2008 solar minimum as compared
    to previous estimates of 1365.4 +/- 1.3 W/m2 established in the 1990s.
    '''
    TOTAL_SOLAR_IRRADIANCE = 1360.8

    @staticmethod
    def __opticalAirMass(solarAltitudeAngle):
        # https://en.wikipedia.org/wiki/Air_mass_%28astronomy%29
        # d'apres (Miguet, 2000; p. 164)
        y = (3.885 + solarAltitudeAngle) ** (-1.253);
        z = sin(solarAltitudeAngle);
        return (1.0 / (z + 0.15 * y))

    @staticmethod
    def __extinctionAtmosphericCoefficient(atmosphericTrouble, angstromTurbidity):
        if (angstromTurbidity < 0.075):
            return 0.1512 - 0.0262 * atmosphericTrouble
        elif (angstromTurbidity < 0.15):
            return 0.1656 - 0.0215 * atmosphericTrouble
        else:
            return 0.2021 - 0.0193 * atmosphericTrouble

    @staticmethod
    def directNormalIrradiance(solarAltitudeAngle):
        # TODO: Corresponding plotted diagram does not match (Miguet, 2000; p. 172)
        atmosphericTrouble = 3.0  # ~ urban area (Miguet, 2000; p. 166)
        angstromTurbidity = 0.15

        tmp = Dogniaux.__opticalAirMass(solarAltitudeAngle) * Dogniaux.__extinctionAtmosphericCoefficient(atmosphericTrouble, angstromTurbidity) * atmosphericTrouble
        return Dogniaux.SOLAR_CONSTANT * exp(-tmp) * sin(solarAltitudeAngle)
