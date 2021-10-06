'''
Created on 18 dec. 2020

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
from numpy import pi, sqrt
from t4gpd.commons.ChrystalAlgorithm import ChrystalAlgorithm
from t4gpd.commons.DiameterLib import DiameterLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class CircularityIndices(AbstractGeoprocess):
    '''
    classdocs
    '''

    @staticmethod
    def runWithArgs(row):
        geom = row.geometry
        area, perim = geom.area, geom.length
        _, diamLen, _ = DiameterLib.diameter(geom)

        gravelius = perim / sqrt(4.0 * pi * area) if (0.0 < area) else None
        jaggedness = (perim * perim) / area if (0.0 < area) else None
        miller = (4.0 * pi * area) / (perim * perim) if (0.0 < perim) else None
        morton = (4.0 * area) / (pi * diamLen * diamLen) if (0.0 < diamLen) else None

        _, _, radius = ChrystalAlgorithm(geom).run()
        mbcArea = pi * radius * radius        
        areaCircDefect = area / mbcArea if (0.0 < mbcArea) else None

        return {
            'gravelius': gravelius,
            'jaggedness': jaggedness,
            'miller': miller,
            'morton': morton,
            'a_circ_def': areaCircDefect
            }
