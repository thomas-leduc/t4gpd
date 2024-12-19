'''
Created on 27 sep. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from pymap3d import Ellipsoid


class SatelliteLib():
    '''
    classdocs
    '''
    CONSTELLATIONS = {"E": "Galileo", "G": "GPS", "R": "GLONASS"}
    NSAT = 94
    WGS84 = Ellipsoid.from_name("wgs84")

    @staticmethod
    def constellation(satName):
        firstLetter = satName[0]
        return SatelliteLib.CONSTELLATIONS[firstLetter]

    @staticmethod
    def get_satellite_name(i):
        if (0 <= i <= 31):
            return f"G{i+1:02d}"  # GPS
        if (32 <= i <= 57):
            return f"R{i-32+1:02d}"  # GLONASS
        if (58 <= i <= 93):
            return f"E{i-58+1:02d}"  # GALILEO
        raise Exception("Unreachable instruction!")
