"""
Created on 15 janv. 2021

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

from t4gpd.commons.morph.StarShapedLib import StarShapedLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class StarShapedIndices(AbstractGeoprocess):
    """
    classdocs
    """

    def __init__(self, precision=1.0, base=2):
        """
        Constructor
        """
        self.precision = precision
        self.base = base

    def runWithArgs(self, row):
        geom = row.geometry
        return StarShapedLib.indices(geom, self.precision, self.base)
