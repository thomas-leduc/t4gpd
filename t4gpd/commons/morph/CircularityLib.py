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

from numpy import nan, pi, sqrt
from shapely import minimum_bounding_circle
from t4gpd.commons.ChrystalAlgorithm import ChrystalAlgorithm
from t4gpd.commons.DiameterLib import DiameterLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.morph.AbstractIndicesLib import AbstractIndicesLib


class CircularityLib(AbstractIndicesLib):
    """
    classdocs
    """

    @staticmethod
    def _getColumns():
        return ["gravelius", "jaggedness", "miller", "morton", "a_circ_def"]

    @staticmethod
    def _indices(row, with_geom=False):
        geom = row.geometry
        result = {
            "gravelius": nan,
            "jaggedness": nan,
            "miller": 0,
            "morton": 0,
            "a_circ_def": 0,
        }

        if GeomLib.isPuntal(geom) or GeomLib.isLineal(geom):
            if with_geom:
                result.update({"geometry": minimum_bounding_circle(geom)})
            return result

        area, perim = geom.area, geom.length
        _, diamLen, _ = DiameterLib.diameter(geom)

        gravelius = perim / sqrt(4.0 * pi * area) if (0.0 < area) else nan
        jaggedness = (perim * perim) / area if (0.0 < area) else nan
        miller = (4.0 * pi * area) / (perim * perim) if (0.0 < perim) else nan
        morton = (4.0 * area) / (pi * diamLen * diamLen) if (0.0 < diamLen) else nan

        mbc, _, radius = ChrystalAlgorithm(geom).run()
        mbcArea = pi * radius * radius
        areaCircDefect = area / mbcArea if (0.0 < mbcArea) else nan

        result = {
            "gravelius": gravelius,
            "jaggedness": jaggedness,
            "miller": miller,
            "morton": morton,
            "a_circ_def": areaCircDefect,
        }

        if with_geom:
            result.update({"geometry": mbc})
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        gdf = GeoDataFrameDemos.theChineseCharacterForReach()
        # gdf = GeoDataFrameDemos.singleBuildingInNantes()
        mbc = CircularityLib.indices(gdf, with_geom=True, merge_by_index=True)

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, color="grey")
        mbc.boundary.plot(ax=ax, color="red")
        ax.axis("square")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return mbc


# mbc = CircularityLib.test()
