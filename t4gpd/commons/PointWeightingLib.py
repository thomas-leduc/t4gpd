"""
Created on 4 Nov. 2025

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

from geopandas import GeoDataFrame
from numpy import vstack
from shapely import Point
from sklearn.neighbors import BallTree
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PointWeightingLib(object):
    """
    classdocs
    """

    @staticmethod
    def weighByInverseDistance(pts, maxDist, listOfNeighbors=False, copy=False):
        def __sumOfInverseDistances(t):
            if 0 == len(t):
                return 0
            return sum([1 / x for x in t if 0 < x])

        if not isinstance(pts, GeoDataFrame):
            raise IllegalArgumentTypeException(pts, "GeoDataFrame")
        if not all(pts.geometry.apply(lambda g: isinstance(g, Point))):
            raise IllegalArgumentTypeException(pts, "GeoDataFrame of shapely.Point")
        if copy:
            pts = pts.copy()

        xy = vstack([pts.geometry.x, pts.geometry.y]).T
        tree = BallTree(xy, leaf_size=16, metric="minkowski")

        # Subtract 1 to exclude the point itself
        # counts = tree.query_radius(xy, r=maxDist, count_only=True) - 1
        # pts["count_neighbors"] = counts
        ind, dist = tree.query_radius(
            xy, r=maxDist, count_only=False, return_distance=True
        )
        # pts["count_neighbors"] = asarray(map(lambda t: len(t) - 1, ind))
        pts["weight"] = dist
        pts["weight"] = pts.weight.apply(lambda t: __sumOfInverseDistances(t))

        if listOfNeighbors:
            pts["neighbors"] = ind
            pts["neighbors"] = pts.apply(
                lambda row: list(set(row.neighbors) - {row.gid}), axis=1
            )

        return pts

    @staticmethod
    def test(ofile=None):
        import matplotlib.pyplot as plt
        from numpy.random import default_rng
        from shapely import points

        maxDist, N = 2.5, 12
        rng = default_rng(123)
        pts = rng.integers(low=0, high=10, size=(N, 2))
        pts = GeoDataFrame({"gid": range(N), "geometry": points(pts)})

        pts = PointWeightingLib.weighByInverseDistance(
            pts, maxDist, listOfNeighbors=True
        )
        pts["count_neighbors"] = pts.neighbors.apply(lambda t: len(t))

        # MAPPING
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_title(f"MaxDist = {maxDist}", fontsize=24)
        pts.plot(ax=ax, column="count_neighbors", cmap="cividis", legend=True)
        pts.apply(
            lambda x: ax.annotate(
                text=f"P$_{{{x.gid}}}$ ({x.count_neighbors})\nw={x.weight:.2f}",
                xy=x.geometry.coords[0],
                color="black",
                size=10,
                ha="left",  # if (0 == x.gid%2) else "right",
                va="bottom",  # if (0 == x.gid%2) else "top",
            ),
            axis=1,
        )
        fig.tight_layout()
        if ofile:
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)
        return pts


# pts = PointWeightingLib.test()
