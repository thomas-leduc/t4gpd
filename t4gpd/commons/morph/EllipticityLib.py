"""
Created on 18 Apr. 2025

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

from numpy import abs, asarray, nan, pi, rad2deg
from shapely import Polygon
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.ellipse.EllipseLib import EllipseLib
from t4gpd.commons.ellipse.EllipticHullLib import EllipticHullLib
from t4gpd.commons.morph.AbstractIndicesLib import AbstractIndicesLib


class EllipticityLib(AbstractIndicesLib):
    """
    classdocs
    """

    @staticmethod
    def _getColumns():
        return [
            "mabe_azim",
            "mabe_area",
            "mabe_perim",
            "mabe_flattening",
            "mabe_mae",
            "mabe_mse",
            "a_elli_def",
            "p_elli_def",
        ]

    @staticmethod
    def _indices(row, with_geom=False):
        def __sort_of_linear_regression(mainAxis, pts):
            ppts = [mainAxis.interpolate(mainAxis.project(pt)) for pt in pts]
            dists = asarray([p.distance(pp) for p, pp in zip(pts, ppts)])
            mae, mse = abs(dists).mean(), (dists**2).mean()
            return mae, mse

        geom = row.geometry
        result = {
            "mabe_azim": nan,
            "mabe_area": nan,
            "mabe_perim": nan,
            "mabe_flattening": nan,
            "mabe_mae": nan,
            "mabe_mse": nan,
            "a_elli_def": nan,
            "p_elli_def": nan,
        }

        if geom.is_empty:
            if with_geom:
                result.update({"geometry": Polygon()})
            return result

        geomArea = geom.area
        geomPerim = geom.length

        threshold = 1e-3  ##### DEBUG
        op = EllipticHullLib(threshold, debug=False)
        centre, semiXAxis, semiYAxis, azim, _, _ = op.getMinimumAreaBoundingEllipse(
            geom
        )
        mabeArea = pi * semiXAxis * semiYAxis
        mabePerim = EllipseLib.getEllipsePerimeter(semiXAxis, semiYAxis)
        mabe = EllipseLib.getEllipseContour(centre, semiXAxis, semiYAxis, azim)

        axis = EllipseLib.getEllipseMainAxis(centre, semiXAxis, semiYAxis, azim)
        pts = GeomLib.getListOfShapelyPoints(geom, withoutClosingLoops=True)
        mabe_mae, mabe_mse = __sort_of_linear_regression(axis, pts)

        flattening = (
            min(semiXAxis, semiYAxis) / max(semiXAxis, semiYAxis)
            if (0.0 < max(semiXAxis, semiYAxis))
            else nan
        )
        areaEllipDefect = geomArea / mabeArea if (0.0 < mabeArea) else nan
        perimEllipDefect = mabePerim / geomPerim if (0.0 < geomPerim) else nan

        result = {
            "mabe_azim": rad2deg(azim),
            "mabe_area": mabeArea,
            "mabe_perim": mabePerim,
            "mabe_flattening": flattening,
            "mabe_mae": mabe_mae,
            "mabe_mse": mabe_mse,
            "a_elli_def": areaEllipDefect,
            "p_elli_def": perimEllipDefect,
        }

        if with_geom:
            result.update({"geometry": mabe})

        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        gdf = GeoDataFrameDemos.theChineseCharacterForReach()
        # gdf = GeoDataFrameDemos.singleBuildingInNantes()
        mabe = EllipticityLib.indices(gdf, with_geom=True, merge_by_index=True)

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, color="grey")
        mabe.boundary.plot(ax=ax, color="red")
        ax.axis("square")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return mabe


# mabe = EllipticityLib.test()
