"""
Created on 27 Feb. 2026

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

import matplotlib.colors as mcolors
from geopandas import GeoDataFrame
from matplotlib.patches import FancyArrowPatch
from matplotlib.pyplot import colormaps
from numpy import cumsum, hypot, issubdtype, number, ones, repeat
from shapely import get_coordinates, get_num_coordinates
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class ArrowsLib(object):
    """
    classdocs
    """

    @staticmethod
    def plot(
        gdf,
        ax,
        column=None,
        color="black",
        cmap="viridis",
        arrowstyle="-|>",
        linewidth=1e-3,
        scale_body=1e-3,
        wing_size=10,
        min_segment_length=1e-6,
    ):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        # GeoDataFrame
        geoms = gdf.geometry.explode(index_parts=False).values

        # Extract all coordinates
        coords = get_coordinates(geoms)
        counts = get_num_coordinates(geoms)
        offsets = cumsum(counts)
        mask = ones(len(coords) - 1, dtype=bool)
        mask[offsets[:-1] - 1] = False

        p0 = coords[:-1][mask]  # starting points
        p1 = coords[1:][mask]  # ending points

        vec = p1 - p0
        lengths = hypot(vec[:, 0], vec[:, 1])
        valid = lengths > min_segment_length
        p0 = p0[valid]
        p1 = p1[valid]
        vec = vec[valid]
        mid = 0.5 * (p0 + p1)

        # Define the body of the arrow around the middle
        # proportionally reduced body
        half_vec = 0.5 * scale_body * vec
        arrow_start = mid - half_vec
        arrow_end = mid + half_vec

        if column is None:
            colors = [color] * len(arrow_start)
        elif column:
            if column not in gdf.columns:
                raise ValueError(f"Column '{column}' not found in GeoDataFrame.")
            values = gdf.explode(index_parts=False)[column].values
            n_segments = get_num_coordinates(geoms) - 1

            values = repeat(values, n_segments)
            values = values[valid]

            if issubdtype(values.dtype, number):
                norm = mcolors.Normalize(vmin=values.min(), vmax=values.max())
                cmap = colormaps[cmap]
                colors = cmap(norm(values))
            else:
                colors = values

        # Create vectorized arrows
        arrows = [
            FancyArrowPatch(
                posA=start,
                posB=end,
                arrowstyle=arrowstyle,
                mutation_scale=wing_size,  # wing size
                color=color,
                linewidth=linewidth,
            )
            for start, end, color in zip(arrow_start, arrow_end, colors)
        ]

        # Add all arrows in batch
        for arrow in arrows:
            ax.add_patch(arrow)

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        paths = GeoDataFrameDemos.districtRoyaleInNantesPaths()

        # PLOTTING
        fig, ax = plt.subplots(figsize=(10, 10))
        cmap = "viridis"
        paths.plot(ax=ax, column="gid", cmap=cmap, linewidth=0.1)
        ArrowsLib.plot(paths, ax, column="gid", cmap=cmap, wing_size=20)
        # ArrowsLib.plot(paths, ax, color="red", wing_size=20)
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# ArrowsLib.test()
