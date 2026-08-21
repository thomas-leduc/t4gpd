"""
Created on 25 Feb. 2026

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

from geopandas import GeoDataFrame, overlay, sjoin
from shapely import (
    Geometry,
    MultiLineString,
    MultiPolygon,
    Polygon,
    STRtree,
    box,
    union_all,
)
from shapely.geometry import CAP_STYLE, JOIN_STYLE
from shapely.ops import voronoi_diagram
from shapely.prepared import prep
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.PointsDensifierLib import PointsDensifierLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib


class SkeletonLib(object):
    """
    classdocs
    """

    @staticmethod
    def morphological_tessellation(
        gdf: GeoDataFrame, bbox: GeoDataFrame, samplingDist: float, shrink: float = 0
    ) -> GeoDataFrame:
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if bbox is None:
            bbox = GeoDataFrame(
                {"geometry": [box(*gdf.total_bounds)]},
                crs=gdf.crs,
            )
        if not isinstance(bbox, GeoDataFrame):
            raise IllegalArgumentTypeException(bbox, "GeoDataFrame")

        # from libpysal.cg.voronoi import voronoi_frames
        # polygons = gdf.geometry.apply(lambda geom: geom.buffer(0))
        # vor, _ = voronoi_frames(
        #     polygons, shrink=0.1, segment=0, grid_size=1e-6
        # )
        # vor = vor.set_index(polygons.index)
        # return vor

        polygons = gdf[
            gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
            & (~gdf.geometry.is_empty)
        ].geometry.copy(deep=True)

        polygons = polygons.apply(
            lambda geom: geom.buffer(
                -abs(shrink), cap_style=CAP_STYLE.flat, join_style=JOIN_STYLE.mitre
            )
        )
        polygons = polygons.apply(lambda geom: geom.normalize())

        pts = polygons.apply(
            lambda geom: PointsInPolygonsLib.select_points_in_polygon(
                PointsDensifierLib.densify_geometry(
                    geom,
                    samplingDist,
                    adjustableDist=True,
                    distToTheSubstrate=1e-3,
                ),
                geom,
            )
        )

        pts = union_all(pts)
        vor = voronoi_diagram(pts, tolerance=0, edges=False)
        vor = GeoDataFrame([{"geometry": v} for v in vor.geoms], crs=gdf.crs)

        vor = sjoin(vor, gdf[["geometry"]], how="inner", predicate="intersects")
        vor = vor.dissolve(by="index_right", as_index=True)

        gdf_geoms_array = gdf.geometry.values
        gdf_tree = STRtree(gdf_geoms_array)
        geom_to_index = {geom: i for i, geom in zip(gdf.index, gdf_geoms_array)}

        result_geoms = []
        for idx, vor_geom in zip(vor.index, vor.geometry):
            candidates = gdf_tree.query(vor_geom)
            candidates_filtered = [
                gdf_geoms_array[b]
                for b in candidates
                if geom_to_index[gdf_geoms_array[b]] != idx
            ]
            if not candidates_filtered:
                result_geoms.append(vor_geom)
            else:
                union_gdf = union_all(candidates_filtered)
                result_geoms.append(vor_geom.difference(union_gdf))
        vor = GeoDataFrame(geometry=result_geoms, index=vor.index, crs=vor.crs)

        #  The following operations preserve the indexes of the GeoDataFrame vor
        vor = overlay(vor.assign(_orig_idx=vor.index), bbox, how="intersection")
        vor.index = vor["_orig_idx"]
        vor = vor.drop(columns="_orig_idx")

        return vor

    @staticmethod
    def skeletonize(
        gdf: GeoDataFrame, samplingDist: float, copy: bool = True
    ) -> GeoDataFrame:
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if copy:
            gdf = gdf.copy()
        gdf["geometry"] = gdf.geometry.apply(
            lambda geom: SkeletonLib.skeletonize_geometry(geom, samplingDist)
        )
        return gdf

    @staticmethod
    def skeletonize_the_void(
        gdf: GeoDataFrame, bbox: GeoDataFrame, samplingDist: float
    ) -> GeoDataFrame:
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if bbox is None:
            bbox = GeoDataFrame(
                {"geometry": [box(*gdf.total_bounds)]},
                crs=gdf.crs,
            )
        if not isinstance(bbox, GeoDataFrame):
            raise IllegalArgumentTypeException(bbox, "GeoDataFrame")

        _gdf = gdf[["geometry"]].copy(deep=True)
        # Use a buffer to avoid slivers
        _gdf["geometry"] = gdf.geometry.apply(lambda geom: geom.buffer(1e-3))

        pts = union_all(PointsDensifierLib.densify(_gdf, samplingDist).geometry)
        vor = voronoi_diagram(pts, tolerance=0, edges=True)
        vor = GeoDataFrame(
            {"geometry": GeomLib.toListOfBipointsAsLineStrings(vor)}, crs=gdf.crs
        )

        # vor = overlay(vor, gdf, how="difference")
        joined = sjoin(vor, _gdf, predicate="intersects", how="left")
        vor = joined[joined.index_right.isna()].drop(columns="index_right")

        vor = overlay(vor, bbox, how="intersection")
        return vor

    @staticmethod
    def skeletonize_geometry(geom: Geometry, samplingDist: float) -> MultiLineString:
        if not isinstance(geom, (Polygon, MultiPolygon)):
            raise IllegalArgumentTypeException(geom, "Polygon or MultiPolygon")
        # Use a buffer to avoid slivers
        geom = geom.buffer(1e-3)
        prep_geom = prep(geom)

        pts = PointsDensifierLib.densify_geometry(
            geom, samplingDist, adjustableDist=True, distToTheSubstrate=None
        )

        vor = voronoi_diagram(pts, tolerance=0, edges=True)
        # The following instruction does not allow "leaf" to be deleted
        # vor = vor.intersection(geom)
        vor = filter(prep_geom.contains, GeomLib.toListOfBipointsAsLineStrings(vor))
        vor = union_all(list(vor))
        return vor

    @staticmethod
    def test(ofile=None):
        from matplotlib import pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox

        # buildings = GeoDataFrameDemos.singleBuildingInNantes()
        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        # buildings = GeoDataFrame(
        #     {"geometry": [box(0, 0, 10, 10), box(0, 10, 10, 20), box(30, 0, 40, 20)]},
        #     crs="epsg:2154",
        # )

        bbox = STBBox(buildings, buffDist=10.0).run()
        # skeleton = SkeletonLib.skeletonize(buildings, samplingDist=5.0)
        skeleton = SkeletonLib.skeletonize_the_void(
            buildings, bbox=bbox, samplingDist=1.0
        )

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, edgecolor="dimgrey", color="lightgrey", linewidth=0.3)
        skeleton.plot(ax=ax, color="red", linewidth=0.3)
        ax.axis("off")
        fig.tight_layout()
        if ofile is not None:
            fig.savefig(ofile, bbox_inches="tight", pad_inches=0)
        else:
            plt.show()
        plt.close(fig)

        # buildings.to_file("/tmp/db.gpkg", layer="buildings")
        # skeleton.to_file("/tmp/db.gpkg", layer="skeleton")

        return skeleton

    @staticmethod
    def test2(ofile=None):
        from matplotlib import pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STBBox import STBBox

        # buildings = GeoDataFrameDemos.singleBuildingInNantes()
        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        # buildings = GeoDataFrame(
        #     {"geometry": [box(0, 0, 10, 10), box(0, 10, 10, 20), box(30, 0, 40, 20)]},
        #     crs="epsg:2154",
        # )

        bbox = STBBox(buildings, buffDist=10.0).run()
        plots = SkeletonLib.morphological_tessellation(
            buildings, bbox=bbox, samplingDist=0.2, shrink=1e-3
        )

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, edgecolor="dimgrey", color="lightgrey", linewidth=0.3)
        plots.boundary.plot(ax=ax, color="red", linewidth=0.5)
        ax.axis("off")
        fig.tight_layout()
        if ofile is not None:
            fig.savefig(ofile, bbox_inches="tight", pad_inches=0)
        else:
            plt.show()
        plt.close(fig)

        buildings.to_file("/tmp/db.gpkg", layer="buildings")
        plots.to_file("/tmp/db.gpkg", layer="plots")

        return plots


# skeleton = SkeletonLib.test(ofile=None)
# plots = SkeletonLib.test2(ofile=None)
