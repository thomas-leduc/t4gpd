"""
Created on 13 sep. 2023

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
from geopandas import GeoDataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.grid.HexagonalTilingLib import HexagonalTilingLib


class STHexagonalGrid(GeoProcess):
    """
    classdocs
    """

    __slots__ = ("gdf", "dx", "dy", "indoor", "intoPoint", "encode", "withDist")

    def __init__(
        self,
        gdf,
        dx,
        dy=None,
        indoor=None,
        intoPoint=True,
        encode=True,
        withDist=False,
    ):
        """
        Constructor
        """
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        self.gdf = gdf
        self.dx = dx
        self.dy = dy
        if indoor in [None, True, False, "both"]:
            self.indoor = indoor
        else:
            raise Exception(
                "Illegal argument: indoor must be chosen in [None, True, False, 'both']!"
            )
        self.intoPoint = intoPoint
        self.encode = encode
        self.withDist = withDist

    def run(self):
        gridLib = HexagonalTilingLib(self.gdf, self.dx, self.dy, self.encode)

        if self.indoor is None:
            grid = gridLib.grid()
        elif "both" == self.indoor:
            grid = gridLib.indoorOutdoorGrid()
        elif self.indoor:
            grid = gridLib.indoorGrid()
        else:
            grid = gridLib.outdoorGrid()

        if self.intoPoint:
            grid.geometry = grid.centroid

        if self.withDist:
            grid = gridLib.distanceToNearestContour(grid)

        return grid

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        gdf = GeoDataFrameDemos.singleBuildingInNantes()
        grid = STHexagonalGrid(gdf, dx=10, dy=None, indoor=None, intoPoint=False).run()

        # PLOTTING
        fig, ax = plt.subplots(figsize=(1.0 * 8.26, 1.0 * 8.26))
        gdf.plot(ax=ax, color="lightgrey")
        grid.boundary.plot(ax=ax, color="red", linewidth=0.2)
        grid.apply(
            lambda x: ax.annotate(
                text=x.gid,
                xy=x.geometry.centroid.coords[0],
                color="blue",
                size=12,
                ha="center",
            ),
            axis=1,
        )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return gdf, grid

# gdf, grid = STHexagonalGrid.test()
