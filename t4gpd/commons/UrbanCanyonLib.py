"""
Created on 28 Apr. 2026

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
from shapely import box, points, union_all
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.grid.FastGridLib import FastGridLib


class UrbanCanyonLib(object):
    """
    classdocs
    """

    @staticmethod
    def __pre_processing(
        buildings: GeoDataFrame, d: float, join_style: str = "mitre"
    ) -> GeoDataFrame:
        """
        Identifies squares and/or urban canyons based on built-up areas using
        morphological closure.

        Algorithm
        ----------
        1. Dilation: each building is expanded by +d
        2. Union: geometric union of all expanded footprints
        3. Erosion: the union is eroded by -d (= morphological closure)
        4. Subtraction from the bbox:
            - squares  = bbox - closure
            - canyons  = closure - union(original buildings)
                       = (bbox - buildings) - (bbox - closure)
        """
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(
                buildings, "buildings must be a GeoDataFrame."
            )
        if not buildings.crs.is_projected:
            raise IllegalArgumentTypeException(
                buildings, "buildings must have a projected CRS."
            )
        if d <= 0:
            raise IllegalArgumentTypeException(d, "'d' must be positive.")

        bbox = box(*buildings.total_bounds)
        dilated = buildings.geometry.buffer(d, join_style=join_style)
        union_dilated = union_all(dilated)
        epsilon = 1e-2
        closing = union_dilated.buffer(-d - epsilon, join_style=join_style)
        return bbox, closing

    @staticmethod
    def delineate_canyons(
        buildings: GeoDataFrame,
        d: float,
        join_style: str = "mitre",
        min_area: float = 0,
    ) -> GeoDataFrame:
        """
        Identifies squares and/or urban canyons based on built-up areas using
        morphological closure.

        Algorithm
        ----------
        1. Dilation: each building is expanded by +d
        2. Union: geometric union of all expanded footprints
        3. Erosion: the union is eroded by -d (= morphological closure)
        4. Subtraction from the bbox:
            - squares  = bbox - closure
            - canyons  = closure - union(original buildings)
                       = (bbox - buildings) - (bbox - closure)
        """
        _, closing = UrbanCanyonLib.__pre_processing(buildings, d, join_style)
        canyons_geom = closing.difference(union_all(buildings.geometry))

        canyons = GeoDataFrame(
            {"geometry": [canyons_geom], "type": ["canyons"]}, crs=buildings.crs
        )
        canyons = canyons.explode(ignore_index=True)
        canyons = (
            canyons[canyons.geometry.area >= min_area]
            .reset_index(drop=True)
            .copy(deep=True)
        )

        return canyons

    @staticmethod
    def delineate_canyons_and_squares(
        buildings: GeoDataFrame,
        d: float,
        join_style: str = "mitre",
        min_area: float = 0,
    ) -> GeoDataFrame:
        """
        Identifies squares and/or urban canyons based on built-up areas using
        morphological closure.

        Algorithm
        ----------
        1. Dilation: each building is expanded by +d
        2. Union: geometric union of all expanded footprints
        3. Erosion: the union is eroded by -d (= morphological closure)
        4. Subtraction from the bbox:
            - squares  = bbox - closure
            - canyons  = closure - union(original buildings)
                       = (bbox - buildings) - (bbox - closure)
        """
        bbox, closing = UrbanCanyonLib.__pre_processing(buildings, d, join_style)
        canyons_geom = closing.difference(union_all(buildings.geometry))
        squares_geom = bbox.difference(closing)

        result = GeoDataFrame(
            {"geometry": [squares_geom, canyons_geom], "type": ["square", "canyons"]},
            crs=buildings.crs,
        )
        result = result.explode(ignore_index=True)
        result = (
            result[result.geometry.area >= min_area]
            .reset_index(drop=True)
            .copy(deep=True)
        )

        return result

    @staticmethod
    def delineate_squares(
        buildings: GeoDataFrame,
        d: float,
        join_style: str = "mitre",
        min_area: float = 0,
    ) -> GeoDataFrame:
        """
        Identifies squares and/or urban canyons based on built-up areas using
        morphological closure.

        Algorithm
        ----------
        1. Dilation: each building is expanded by +d
        2. Union: geometric union of all expanded footprints
        3. Erosion: the union is eroded by -d (= morphological closure)
        4. Subtraction from the bbox:
            - squares  = bbox - closure
            - canyons  = closure - union(original buildings)
                       = (bbox - buildings) - (bbox - closure)
        """
        bbox, closing = UrbanCanyonLib.__pre_processing(buildings, d, join_style)
        squares_geom = bbox.difference(closing)

        squares = GeoDataFrame(
            {"geometry": [squares_geom], "type": ["square"]}, crs=buildings.crs
        )
        squares = squares.explode(ignore_index=True)
        squares = (
            squares[squares.geometry.area >= min_area]
            .reset_index(drop=True)
            .copy(deep=True)
        )

        return squares

    @staticmethod
    def point_labeling(
        sensors: GeoDataFrame,
        buildings: GeoDataFrame,
        d: float,
        join_style: str = "mitre",
        min_area: float = 0,
        predicate: str = "intersects",
    ) -> GeoDataFrame:
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(
                sensors, "sensors must be a GeoDataFrame."
            )
        if not GeoDataFrameLib.shareTheSameCrs(sensors, buildings):
            raise Exception(
                "sensors and buildings must share the same CRS.",
            )
        if predicate not in ["intersects", "within"]:
            raise IllegalArgumentTypeException(
                predicate, "predicate must be either 'intersects' or 'within'."
            )
        gdf = UrbanCanyonLib.delineate_canyons_and_squares(
            buildings, d, join_style=join_style, min_area=min_area
        )
        # predicate="within": checks whether the point is strictly inside
        # the polygon. Use "intersects" to include points on the boundary
        result = (
            sjoin(sensors, gdf[["geometry", "type"]], how="left", predicate=predicate)
            .drop(columns="index_right")
            .loc[lambda df: ~df.index.duplicated(keep="first")]
        )
        result.fillna(value={"type": "other"}, inplace=True)
        return result

    @staticmethod
    def compute_hw_ratio(
        canyons: GeoDataFrame,
        buildings: GeoDataFrame,
        height_col: str = "hauteur",
        buffer_adjacency: float = 0.5,  # tolerance for detecting adjacent buildings
        h_agg: str = "mean",  # "mean" | "median" | "max"
        join_style: str = "mitre",
    ) -> GeoDataFrame:
        """
        Calculates the H/W ratio for each urban canyon.

        Parameters
        ----------
        canyons : GeoDataFrame
            Canyon polygons (output of the `delineate_canyons` function).
        buildings : GeoDataFrame
            Buildings constructed with a tall column.
        height_col : str
            Name of the height column in buildings.
        buffer_adjacency : float
            Buffer (CRS unit) for detecting adjacent buildings.
        h_agg : str
            Aggregation function for the heights of adjacent buildings.

        Returns
        -------
        GeoDataFrame
            canyons with new columns: W, H, H_W_ratio.
        """

        # ------------------------------------------------------------------
        # 1. Width W: short side of the bounding rectangle
        # ------------------------------------------------------------------
        def _width(geom):
            rect = geom.minimum_rotated_rectangle
            pts = points(rect.exterior.coords)
            sides = [pts[i].distance(pts[i + 1]) for i in range(4)]
            return min(sides)

        w = canyons.geometry.apply(_width)

        # ------------------------------------------------------------------
        # 2. Height H: aggregation of adjacent buildings
        # ------------------------------------------------------------------
        canyons_buf = canyons[["geometry"]].copy()
        canyons_buf["geometry"] = canyons_buf["geometry"].buffer(
            buffer_adjacency, join_style=join_style
        )
        adj = sjoin(
            buildings[[height_col, "geometry"]],
            canyons_buf,
            how="inner",
            predicate="intersects",
        )
        agg_fn = {"mean": "mean", "median": "median", "max": "max"}[h_agg]
        h = adj.groupby("index_right")[height_col].agg(agg_fn).rename("H")

        # ------------------------------------------------------------------
        # 3. H/W Ratio
        # ------------------------------------------------------------------
        h_over_w = h / w

        return w, h, h_over_w

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        min_area = 50

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        squares = UrbanCanyonLib.delineate_squares(buildings, d=10, min_area=min_area)
        canyons = UrbanCanyonLib.delineate_canyons(buildings, d=10, min_area=min_area)

        gdf = UrbanCanyonLib.delineate_canyons_and_squares(
            buildings, d=10, min_area=min_area
        )
        # squares = gdf.query("type == 'square'").copy(deep=True)
        # canyons = gdf.query("type == 'canyons'").copy(deep=True)

        fig, ax = plt.subplots(figsize=(10, 10))
        buildings.plot(ax=ax, color="lightgray", edgecolor="black")
        squares.plot(ax=ax, color="none", edgecolor="red", hatch="///", alpha=0.5)
        canyons.plot(ax=ax, color="none", edgecolor="blue", hatch="...", alpha=0.5)
        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return squares, canyons, gdf

    @staticmethod
    def test2():
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        rgb = ListedColormap(["red", "green", "blue"])
        min_area = 50

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        sensors = FastGridLib.grid(
            buildings, dx=10, dy=None, intoPoint=True, withRowsCols=False
        )
        sensors2 = UrbanCanyonLib.point_labeling(
            sensors, buildings, d=10, min_area=min_area
        )
        assert len(sensors) == len(sensors2)

        squares = UrbanCanyonLib.delineate_squares(buildings, d=10, min_area=min_area)
        canyons = UrbanCanyonLib.delineate_canyons(buildings, d=10, min_area=min_area)

        fig, ax = plt.subplots(figsize=(10, 10))
        buildings.plot(ax=ax, color="lightgray", edgecolor="black")
        squares.plot(ax=ax, color="red", edgecolor="red", alpha=0.15)
        canyons.plot(ax=ax, color="blue", edgecolor="blue", alpha=0.15)
        sensors2.plot(
            ax=ax, column="type", marker="o", markersize=5, cmap=rgb, legend=True
        )
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return squares, canyons, sensors2

    @staticmethod
    def test3():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        min_area = 50

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        # squares = UrbanCanyonLib.delineate_squares(buildings, d=10, min_area=min_area)
        # canyons = UrbanCanyonLib.delineate_canyons(buildings, d=10, min_area=min_area)

        gdf = UrbanCanyonLib.delineate_canyons_and_squares(
            buildings, d=10, min_area=min_area
        )
        w, h, h_over_w = UrbanCanyonLib.compute_hw_ratio(
            gdf, buildings, height_col="HAUTEUR", buffer_adjacency=0.5
        )
        gdf["w_canyon"] = w
        gdf["h_canyon"] = h
        gdf["h_over_w"] = h_over_w

        squares = gdf.query("type == 'square'").copy(deep=True)
        canyons = gdf.query("type == 'canyons'").copy(deep=True)

        fig, ax = plt.subplots(figsize=(10, 10))
        buildings.plot(ax=ax, color="lightgray", edgecolor="black")
        buildings.apply(
            lambda x: ax.annotate(
                text=f"{x.HAUTEUR:.1f}",
                xy=x.geometry.centroid.coords[0],
                color="red",
                size=9,
                ha="center",
            ),
            axis=1,
        )
        squares.plot(ax=ax, color="red", edgecolor="red", alpha=0.25)
        canyons.plot(ax=ax, color="blue", edgecolor="blue", alpha=0.25)
        gdf.apply(
            lambda x: ax.annotate(
                text=f"H={x.h_canyon:.1f}\nW={x.w_canyon:.1f}\nH/W={x.h_over_w:.1f}",
                xy=x.geometry.centroid.coords[0],
                color="black",
                size=9,
                ha="center",
            ),
            axis=1,
        )
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        buildings.to_file("/tmp/debug.gpkg", layer="buildings", driver="GPKG")
        canyons.to_file("/tmp/debug.gpkg", layer="canyons", driver="GPKG")
        squares.to_file("/tmp/debug.gpkg", layer="squares", driver="GPKG")
        return squares, canyons, gdf


# squares, canyons, gdf = UrbanCanyonLib.test()
# squares, canyons, sensors = UrbanCanyonLib.test2()
# squares, canyons, gdf = UrbanCanyonLib.test3()
