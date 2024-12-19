'''
Created on 20 nov. 2024

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
from numpy import asarray, isnan, pi
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.ellipse.EllipseLib import EllipseLib
from t4gpd.commons.ellipse.EllipticHullLib import EllipticHullLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class EllipticityAxisIndices(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, threshold=None, debug=False, with_geom=False):
        '''
        Constructor
        '''
        self.mabe = EllipticHullLib(threshold, debug)
        self.with_geom = with_geom

    @staticmethod
    def __sort_of_linear_regression(mainAxis, pts):
        ppts = [mainAxis.interpolate(mainAxis.project(pt)) for pt in pts]
        dists = asarray([p.distance(pp) for p, pp in zip(pts, ppts)])
        mae, mse = dists.sum(), (dists ** 2).sum()
        return mae, mse

    def runWithArgs(self, row):
        geom = row.geometry

        pts = GeomLib.getListOfShapelyPoints(geom, withoutClosingLoops=True)
        chull = geom.convex_hull

        # [Point(centre), semiXAxis, semiYAxis, azim, nodes, methName]
        centre, semiXAxis, semiYAxis, azim, _, _ = self.mabe.getMinimumAreaBoundingEllipse(
            chull)

        geomArea = geom.area
        mabeArea = pi * semiXAxis * semiYAxis
        if (isnan(mabeArea)) or (mabeArea < geomArea):
            raise Exception(
                f"Minimum-area bounding ellipse is {mabeArea} (input geom area: {geomArea:.1f})!")

        mainAxis = EllipseLib.getEllipseMainAxis(
            centre, semiXAxis, semiYAxis, azim)
        flattening = min(semiXAxis, semiYAxis) / max(semiXAxis,
                                                     semiYAxis) if (0.0 < max(semiXAxis, semiYAxis)) else None
        mae, mse = EllipticityAxisIndices.__sort_of_linear_regression(
            mainAxis, pts)
        if self.with_geom:
            return {
                "geometry": mainAxis,
                "flattening": flattening,
                "ell_mae": mae,
                "ell_mse": mse
            }

        return {
            "flattening": flattening,
            "ell_mae": mae,
            "ell_mse": mse
        }
