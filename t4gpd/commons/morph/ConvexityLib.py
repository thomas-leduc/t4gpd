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
from shapely import get_parts
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.morph.AbstractIndicesLib import AbstractIndicesLib


class ConvexityLib(AbstractIndicesLib):
    """
    classdocs
    """

    @staticmethod
    def _getColumns():
        return ["n_con_comp", "a_conv_def", "p_conv_def", "big_concav", "small_conc"]

    @staticmethod
    def _indices(row, with_geom=False):
        geom = row.geometry
        result = {
            "n_con_comp": nan,
            "a_conv_def": nan,
            "p_conv_def": nan,
            "big_concav": nan,
            "small_conc": nan,
        }

        if GeomLib.isPuntal(geom) or GeomLib.isLineal(geom):
            if with_geom:
                result.update({"geometry": geom.convex_hull})
            return result

        geomArea, geomPerim = geom.area, geom.length

        chull = geom.convex_hull
        chullArea = chull.area
        chullPerim = chull.length

        connectedComponents = get_parts(chull.difference(geom))

        nConnectedComponents = len(connectedComponents)
        areaConvexityDefect = geomArea / chullArea if (0.0 < chullArea) else nan
        perimConvexityDefect = chullPerim / geomPerim if (0.0 < geomPerim) else nan

        bigConcavities = (
            sum([g.area**2 for g in connectedComponents]) / nConnectedComponents
            if (0 < nConnectedComponents)
            else nan
        )
        smallConcavities = (
            sum([g.area ** (-2) for g in connectedComponents if (0.0 < g.area)])
            / nConnectedComponents
            if (0 < nConnectedComponents)
            else nan
        )

        result = {
            "n_con_comp": nConnectedComponents,
            "a_conv_def": areaConvexityDefect,
            "p_conv_def": perimConvexityDefect,
            "big_concav": bigConcavities,
            "small_conc": smallConcavities,
        }
        if with_geom:
            result.update({"geometry": chull})
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        gdf = GeoDataFrameDemos.theChineseCharacterForReach()
        # gdf = GeoDataFrameDemos.singleBuildingInNantes()
        chull = ConvexityLib.indices(gdf, with_geom=True, merge_by_index=True)

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, color="grey")
        chull.boundary.plot(ax=ax, color="red")
        ax.axis("square")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return chull


# chull = ConvexityLib.test()
