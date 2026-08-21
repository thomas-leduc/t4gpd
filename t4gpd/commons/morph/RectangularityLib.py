"""
Created on 25 feb. 2025

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

from numpy import nan
from t4gpd.commons.CaliperLib import CaliperLib
from t4gpd.commons.DistanceFromPointsToCurveLib import DistanceFromPointsToCurveLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.morph.AbstractIndicesLib import AbstractIndicesLib


class RectangularityLib(AbstractIndicesLib):
    """
    classdocs
    """

    @staticmethod
    def _getColumns():
        return [
            "stretching",
            "a_rect_def",
            "p_rect_def",
            "mabr_major_mae",
            "mabr_major_mse",
            "mabr_major_rmse",
            "mabr_minor_mae",
            "mabr_minor_mse",
            "mabr_minor_rmse",
        ]

    @staticmethod
    def get_indices(geom, with_geom=False, suffix=""):
        result = {
            f"stretching{suffix}": nan,
            f"a_rect_def{suffix}": nan,
            f"p_rect_def{suffix}": nan,
            f"mabr_major_mae{suffix}": nan,
            f"mabr_major_mse{suffix}": nan,
            f"mabr_major_rmse{suffix}": nan,
            f"mabr_minor_mae{suffix}": nan,
            f"mabr_minor_mse{suffix}": nan,
            f"mabr_minor_rmse{suffix}": nan,
        }

        if GeomLib.isPuntal(geom) or GeomLib.isLineal(geom):
            if with_geom:
                result.update({"geometry": geom.minimum_rotated_rectangle})
            return result

        geomArea, geomPerim = geom.area, geom.length

        mabr, len1, len2 = CaliperLib().mabr(geom)
        mabrArea, mabrPerim = mabr.area, mabr.length

        mabr_major_mae = nan
        mabr_major_mse = nan
        mabr_major_rmse = nan
        mabr_minor_mae = nan
        mabr_minor_mse = nan
        mabr_minor_rmse = nan
        if 0 < len1 * len2:
            major = CaliperLib.major_axis(mabr)
            mabr_major_mae = DistanceFromPointsToCurveLib.mae(geom, major)
            mabr_major_mse = DistanceFromPointsToCurveLib.mse(geom, major)
            mabr_major_rmse = DistanceFromPointsToCurveLib.rmse(geom, major)

            minor = CaliperLib.minor_axis(mabr)
            mabr_minor_mae = DistanceFromPointsToCurveLib.mae(geom, minor)
            mabr_minor_mse = DistanceFromPointsToCurveLib.mse(geom, minor)
            mabr_minor_rmse = DistanceFromPointsToCurveLib.rmse(geom, minor)

        stretching = (
            min(len1, len2) / max(len1, len2) if (0.0 < max(len1, len2)) else nan
        )
        areaRectDefect = geomArea / mabrArea if (0.0 < mabrArea) else nan
        perimRectDefect = mabrPerim / geomPerim if (0.0 < geomPerim) else nan

        result = {
            f"stretching{suffix}": stretching,
            f"a_rect_def{suffix}": areaRectDefect,
            f"p_rect_def{suffix}": perimRectDefect,
            f"mabr_major_mae{suffix}": mabr_major_mae,
            f"mabr_major_mse{suffix}": mabr_major_mse,
            f"mabr_major_rmse{suffix}": mabr_major_rmse,
            f"mabr_minor_mae{suffix}": mabr_minor_mae,
            f"mabr_minor_mse{suffix}": mabr_minor_mse,
            f"mabr_minor_rmse{suffix}": mabr_minor_rmse,
        }
        if with_geom:
            result.update({"geometry": mabr})
        return result

    @staticmethod
    def _indices(row, with_geom=False):
        return RectangularityLib.get_indices(row.geometry, with_geom=with_geom)

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        gdf = GeoDataFrameDemos.theChineseCharacterForReach()
        # gdf = GeoDataFrameDemos.singleBuildingInNantes()
        mabr = RectangularityLib.indices(gdf, with_geom=True, merge_by_index=True)

        major = mabr.copy(deep=True)
        major.geometry = major.geometry.apply(CaliperLib.major_axis)
        minor = mabr.copy(deep=True)
        minor.geometry = minor.geometry.apply(CaliperLib.minor_axis)

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, color="grey")
        mabr.boundary.plot(ax=ax, color="red")
        major.plot(ax=ax, color="black")
        minor.plot(ax=ax, color="black", linestyle="--")
        ax.axis("square")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return mabr


# mabr = RectangularityLib.test()
