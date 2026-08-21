"""
Created on 16 Nov. 2025

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

from geopandas import GeoDataFrame, sjoin
from numpy import ceil, floor
from shapely import box
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class IGNTilingLib(object):
    """
    classdocs
    """

    @staticmethod
    def grid(gdf, prefix="", suffix="", step=1000):
        """
        Generate a grid of IGN tiles intersecting the given GeoDataFrame.

        Args:
            gdf (GeoDataFrame): The input GeoDataFrame.
            prefix (str): The prefix for the tile labels.
            suffix (str): The suffix for the tile labels.
            step (int): The step size for the grid.
                step=1000 -> LiDAR HD
                step=5000 -> RGE ALTI 5m
                step=10000 -> COSIA

        Returns:
            GeoDataFrame: The grid of IGN tiles.
        """
        
        def __gid(x, y, step):
            match step:
                case 1000:
                    _x, _y = x // step, (y + step) // step
                    return f"{_x:04d}_{_y:04d}"
                case 5000:
                    _x, _y = x // 1000, (y + 5000)// 1000
                    return f"{_x:04d}_{_y:04d}"
                case 10000:
                    _x, _y = x // step, (y + step) // step
                    _x, _y = 10 * _x, 10 * _y
                    return f"{_x:03d}_{_y:04d}"
            raise NotImplementedError(f"Step size {step} not implemented!")

        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if not gdf.crs.is_projected:
            raise Exception("The given GeoDataFrame is a geographic (lat/lon) one!")

        minx, miny, maxx, maxy = gdf.total_bounds
        minx = step * floor(minx / step).astype(int)
        maxx = step * ceil(maxx / step).astype(int)
        miny = step * floor(miny / step).astype(int)
        maxy = step * ceil(maxy / step).astype(int)
        result = GeoDataFrame(
            [
                {
                    # gid, label: ULC convention
                    "gid": __gid(x, y, step),
                    "label": f"{prefix}{__gid(x, y, step)}{suffix}",
                    "geometry": box(x, y, x + step, y + step),
                }
                for x in range(minx, maxx, step)
                for y in range(miny, maxy, step)
            ],
            crs=gdf.crs,
        )
        result = sjoin(result, gdf[["geometry"]], how="inner", predicate="intersects")
        result.drop(columns=["index_right"], inplace=True)
        result.sort_values(by="gid", inplace=True)
        return result

    @staticmethod
    def test(ofile=None):
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemosA import GeoDataFrameDemosA

        roi = GeoDataFrameDemosA.ileDeNantes()
        grid = IGNTilingLib.grid(roi)

        # SERIALIZATION
        grid[["label"]].to_csv("/tmp/ign_dalles.txt", header=False, index=False)

        # PLOTTING
        fig, ax = plt.subplots(figsize=(1.7 * 8.26, 1 * 8.26))
        roi.boundary.plot(ax=ax, color="red", linestyle="dashed")
        grid.boundary.plot(ax=ax, color="blue", linestyle="solid", linewidth=0.6)
        grid.apply(
            lambda x: ax.annotate(
                text=x.gid,
                xy=x.geometry.centroid.coords[0],
                color="black",
                size=10,
                ha="center",
            ),
            axis=1,
        )
        ax.axis("off")
        fig.tight_layout()
        if ofile:
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)


# IGNTilingLib.test()
