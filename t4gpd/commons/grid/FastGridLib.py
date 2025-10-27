"""
Created on 30 Sep. 2025

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
from numpy import ceil, linspace, meshgrid, vectorize
from shapely import Point, box


class FastGridLib(object):
    """
    classdocs
    """

    @staticmethod
    def grid(gdf, dx, dy=None, intoPoint=True, withRowsCols=False):
        dy = dx if (dy is None) else dy
        minx, miny, maxx, maxy = gdf.total_bounds
        ncols = int(ceil((maxx - minx) / dx))
        nrows = int(ceil((maxy - miny) / dy))

        xOffset = ((ncols * dx) - (maxx - minx)) / 2.0
        yOffset = ((nrows * dy) - (maxy - miny)) / 2.0

        x0, y0 = minx - xOffset, miny - yOffset
        if intoPoint:
            x0, y0 = x0 + 0.5 * dx, y0 + 0.5 * dy
            __foo = lambda x, y: Point(x, y)
        else:
            __foo = lambda x, y: box(x, y, x + dx, y + dy)

        x = linspace(x0, x0 + ncols * dx, ncols, endpoint=False)
        y = linspace(y0, y0 + nrows * dy, nrows, endpoint=False)
        X, Y = meshgrid(x, y)
        # geoms = [__foo(x, y) for x, y in zip(X.ravel(), Y.ravel())]
        geoms = vectorize(__foo)(X, Y).ravel()

        result = GeoDataFrame(
            {"gid": range(len(geoms)), "geometry": geoms}, crs=gdf.crs
        )
        if withRowsCols:
            result = result.assign(
                row=result.gid // ncols,
                column=result.gid % ncols,
            )
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox
        from t4gpd.morph.STGrid import STGrid

        buildings = GeoDataFrameDemos.singleBuildingInNantes()
        # buildings = GeoDataFrameDemos.ensaNantesBuildings()
        bbox = STBBox(buildings, 0).run()

        grid1 = FastGridLib.grid(buildings, dx=10, intoPoint=False, withRowsCols=True)
        grid11 = FastGridLib.grid(buildings, dx=10, intoPoint=True)

        grid2 = STGrid(buildings, dx=10, intoPoint=False).run()
        grid22 = STGrid(buildings, dx=10, intoPoint=True).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(12, 12))
        buildings.plot(ax=ax, color="grey")
        bbox.boundary.plot(ax=ax, color="black")

        grid1.boundary.plot(ax=ax, color="red", linestyle=":", linewidth=4)
        grid11.plot(ax=ax, color="red", marker="o", markersize=100)
        grid1.apply(
            lambda x: ax.annotate(
                text=f"{x.gid}\n({x.row},{x.column})",
                xy=x.geometry.bounds[:2],
                color="black",
                size=12,
                ha="left",
            ),
            axis=1,
        )

        grid2.boundary.plot(ax=ax, color="green", linestyle="-.")
        grid22.plot(ax=ax, color="green", marker="+", markersize=100)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# FastGridLib.test()
