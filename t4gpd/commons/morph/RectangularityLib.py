"""
Created on 25 feb. 2025

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

from numpy import nan
from t4gpd.commons.CaliperLib import CaliperLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.morph.AbstractIndicesLib import AbstractIndicesLib


class RectangularityLib(AbstractIndicesLib):
    """
    classdocs
    """

    @staticmethod
    def _getColumns():
        return ["stretching", "a_rect_def", "p_rect_def"]

    @staticmethod
    def _indices(row, with_geom=False):
        geom = row.geometry
        result = {"stretching": nan, "a_rect_def": nan, "p_rect_def": nan}

        if GeomLib.isPuntal(geom) or GeomLib.isLineal(geom):
            if with_geom:
                result.update({"geometry": geom.minimum_rotated_rectangle})
            return result

        geomArea, geomPerim = geom.area, geom.length

        mabr, len1, len2 = CaliperLib().mabr(geom)
        mabrArea, mabrPerim = mabr.area, mabr.length

        stretching = (
            min(len1, len2) / max(len1, len2) if (0.0 < max(len1, len2)) else nan
        )
        areaRectDefect = geomArea / mabrArea if (0.0 < mabrArea) else nan
        perimRectDefect = mabrPerim / geomPerim if (0.0 < geomPerim) else nan

        result = {
            "stretching": stretching,
            "a_rect_def": areaRectDefect,
            "p_rect_def": perimRectDefect,
        }
        if with_geom:
            result.update({"geometry": mabr})
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        gdf = GeoDataFrameDemos.theChineseCharacterForReach()
        # gdf = GeoDataFrameDemos.singleBuildingInNantes()
        mabr = RectangularityLib.indices(gdf, with_geom=True, merge_by_index=True)

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, color="grey")
        mabr.boundary.plot(ax=ax, color="red")
        ax.axis("square")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return mabr


# mabr = RectangularityLib.test()
