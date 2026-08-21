"""
Created on 18 Apr. 2025

@author: tleduc

Copyright 2020-2026 Thomas Leduc

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

    def get_indices(geom, with_geom=False, suffix=""):
        def __sort_of_linear_regression(mainAxis, pts):
            ppts = [mainAxis.interpolate(mainAxis.project(pt)) for pt in pts]
            dists = asarray([p.distance(pp) for p, pp in zip(pts, ppts)])
            mae, mse = abs(dists).mean(), (dists**2).mean()
            return mae, mse

        result = {
            f"mabe_azim{suffix}": nan,
            f"mabe_area{suffix}": nan,
            f"mabe_perim{suffix}": nan,
            f"mabe_flattening{suffix}": nan,
            f"mabe_mae{suffix}": nan,
            f"mabe_mse{suffix}": nan,
            f"a_elli_def{suffix}": nan,
            f"p_elli_def{suffix}": nan,
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
            f"mabe_azim{suffix}": rad2deg(azim),
            f"mabe_area{suffix}": mabeArea,
            f"mabe_perim{suffix}": mabePerim,
            f"mabe_flattening{suffix}": flattening,
            f"mabe_mae{suffix}": mabe_mae,
            f"mabe_mse{suffix}": mabe_mse,
            f"a_elli_def{suffix}": areaEllipDefect,
            f"p_elli_def{suffix}": perimEllipDefect,
        }

        if with_geom:
            result.update({"geometry": mabe})

        return result

    @staticmethod
    def _indices(row, with_geom=False):
        return EllipticityLib.get_indices(row.geometry, with_geom=with_geom)

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
