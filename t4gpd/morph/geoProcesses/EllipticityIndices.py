"""
Created on 18 dec. 2020

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
"""

from numpy import isnan, pi
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.ellipse.EllipseLib import EllipseLib
from t4gpd.commons.ellipse.EllipticHullLib import EllipticHullLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class EllipticityIndices(AbstractGeoprocess):
    """
    classdocs
    """

    def __init__(self, threshold=None, debug=False, with_geom=False):
        """
        Constructor
        """
        self.mabe = EllipticHullLib(threshold, debug)
        self.with_geom = with_geom

    def runWithArgs(self, row):
        geom = row.geometry

        if GeomLib.isLineal(geom):
            if self.with_geom:
                return {
                    "geometry": geom.minimum_rotated_rectangle,
                    "flattening": 0,
                    "a_elli_def": 1,
                    "p_elli_def": 1,
                }
            return {
                "flattening": 0,
                "a_elli_def": 1,
                "p_elli_def": 1,
            }

        geomArea = geom.area
        geomPerim = geom.length

        # [Point(centre), semiXAxis, semiYAxis, azim, nodes, methName]
        centre, semiXAxis, semiYAxis, azim, _, _ = (
            self.mabe.getMinimumAreaBoundingEllipse(geom)
        )

        mabeArea = pi * semiXAxis * semiYAxis
        if (isnan(mabeArea)) or (mabeArea < geomArea):
            raise Exception(
                "Minimum-area bounding ellipse is %s (input geom area: %.1f)!"
                % (str(mabeArea), geomArea)
            )
        mabePerim = EllipseLib.getEllipsePerimeter(semiXAxis, semiYAxis)

        flattening = (
            min(semiXAxis, semiYAxis) / max(semiXAxis, semiYAxis)
            if (0.0 < max(semiXAxis, semiYAxis))
            else None
        )
        areaEllipDefect = geomArea / mabeArea if (0.0 < mabeArea) else None
        perimEllipDefect = mabePerim / geomPerim if (0.0 < geomPerim) else None

        if self.with_geom:
            # EllipseLib.getEllipseContour(centre, semiXAxis, semiYAxis, azim, npoints=40)
            mabe = EllipseLib.getEllipseContour(centre, semiXAxis, semiYAxis, azim)
            return {
                "geometry": mabe,
                "flattening": flattening,
                "a_elli_def": areaEllipDefect,
                "p_elli_def": perimEllipDefect,
            }

        return {
            "flattening": flattening,
            "a_elli_def": areaEllipDefect,
            "p_elli_def": perimEllipDefect,
        }
