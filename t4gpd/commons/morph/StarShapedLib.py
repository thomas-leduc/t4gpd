"""
Created on 10 mar. 2025

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

from numpy import max, mean, median, min, nan, std
from shapely import MultiLineString, Polygon, get_parts, get_point
from t4gpd.commons.Entropy import Entropy
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.morph.AbstractIndicesLib import AbstractIndicesLib


class StarShapedLib(AbstractIndicesLib):
    """
    classdocs
    """

    @staticmethod
    def _getColumns():
        return [
            "min_raylen",
            "avg_raylen",
            "std_raylen",
            "max_raylen",
            "med_raylen",
            "entropy",
            "drift",
        ]

    @staticmethod
    def _indices(row, precision=1.0, base=2, with_geom=False):
        geom = row.geometry
        result = {
            "min_raylen": nan,
            "avg_raylen": nan,
            "std_raylen": nan,
            "max_raylen": nan,
            "med_raylen": nan,
            "entropy": nan,
            "drift": nan,
        }

        if isinstance(geom, MultiLineString) and (not geom.is_empty):
            viewpoint = set(get_point(get_parts(geom), 0))
            if 1 != len(viewpoint):
                raise IllegalArgumentTypeException(
                    geom, "MultiLineString with single viewpoint"
                )
            viewpoint = viewpoint.pop()
            centroid = Polygon(get_point(get_parts(geom), 1)).centroid
            drift = viewpoint.distance(centroid)

            lengths = GeomLib.fromMultiLineStringToLengths(geom)
            h = Entropy.createFromDoubleValuesArray(lengths, precision).h(base)

            result = {
                "min_raylen": min(lengths),
                "avg_raylen": mean(lengths),
                "std_raylen": std(lengths),
                "max_raylen": max(lengths),
                "med_raylen": median(lengths),
                "entropy": h,
                "drift": drift,
            }

            if with_geom:
                result.update({"geometry": geom})
            return result

        if with_geom:
            result.update({"geometry": MultiLineString()})
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from shapely import get_coordinates
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        gdf = GeoDataFrameDemos.theChineseCharacterForReach()
        # gdf = GeoDataFrameDemos.singleBuildingInNantes()
        gdf.geometry = gdf.geometry.apply(
            lambda geom: MultiLineString(
                [(geom.centroid.coords[0], rp) for rp in get_coordinates(geom)]
            )
        )
        ssl = StarShapedLib.indices(gdf, with_geom=True, merge_by_index=True)

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, color="grey")
        ssl.plot(ax=ax, color="red")
        ax.axis("square")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return ssl


# ssl = StarShapedLib.test()
