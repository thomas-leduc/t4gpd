"""
Created on 10 nov. 2023

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
import warnings
from geopandas import GeoDataFrame, overlay, sjoin
from pandas import concat
from shapely import MultiLineString, union_all
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils


class PrepareMasksLib(object):
    """
    classdocs
    """

    @staticmethod
    def extrudeBuildingsOnFlatland(
        buildings, elevationFieldname="HAUTEUR", oriented=True, make_valid=True
    ):
        result = buildings.copy(deep=True)
        if make_valid:
            result.geometry = result.geometry.apply(lambda g: g.buffer(0))
        result.geometry = result.apply(
            lambda rows: GeomLib.forceZCoordinateToZ0(
                rows.geometry, z0=rows[elevationFieldname]
            ),
            axis=1,
        )
        if oriented:
            result.geometry = result.geometry.apply(
                lambda g: GeomLib.reverseRingOrientation(g.normalize())
            )
        return result

    @staticmethod
    def getMasksAsBipoints(buildings, oriented=True, make_valid=True, union=False):
        # result = buildings.geometry.to_frame()
        result = buildings.copy(deep=True)
        if make_valid:
            result.geometry = result.geometry.apply(lambda g: g.buffer(0))
        if union:
            result = GeoDataFrame(
                [{"geometry": union_all(result.geometry)}], crs=buildings.crs
            )
        if oriented:
            result.geometry = result.geometry.apply(
                lambda g: GeomLib.reverseRingOrientation(g.normalize())
            )
        result.geometry = result.geometry.apply(
            lambda g: MultiLineString(GeomLib.toListOfBipointsAsLineStrings(g))
        )
        result = result.explode(ignore_index=True, index_parts=True)
        return result

    @staticmethod
    def localMaskClipping(viewpoints, buildings, vp_pk, buffDist, strict=True):
        warnings.formatwarning = WarnUtils.format_Warning

        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpoints, "GeoDataFrame")
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(viewpoints, buildings):
            raise Exception(
                "Illegal argument: viewpoints and buildings are expected to share the same crs!"
            )
        if not DataFrameLib.isAPrimaryKey(viewpoints, vp_pk):
            raise IllegalArgumentTypeException(vp_pk, "primary key for viewpoints")
        if vp_pk in buildings:
            warnings.warn(f"{vp_pk} is also a buildings' column!")

        viewpoints2 = viewpoints[[vp_pk, "geometry"]].copy(deep=True)
        viewpoints2.geometry = viewpoints2.geometry.apply(
            lambda geom: geom.buffer(buffDist)
        )

        if strict:
            return overlay(buildings, viewpoints2, how="intersection")
        else:
            result = sjoin(buildings, viewpoints2, how="inner", predicate="intersects")
            result.drop(columns="index_right", inplace=True)
            return result

    @staticmethod
    def removeNonVisible25DMasks(
        viewpoints, masks, elevationFieldname, horizon, h0, encode=False
    ):
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpoints, "GeoDataFrame")
        if not isinstance(masks, GeoDataFrame):
            raise IllegalArgumentTypeException(masks, "GeoDataFrame")
        if not elevationFieldname in masks:
            raise Exception(f"{elevationFieldname} is not a relevant field name!")
        if not GeoDataFrameLib.shareTheSameCrs(viewpoints, masks):
            raise Exception(
                "Illegal argument: viewpoints and masks are expected to share the same crs!"
            )

        viewpoints2 = viewpoints.copy(deep=True)
        viewpoints2.geometry = viewpoints2.geometry.apply(
            lambda geom: geom if geom.has_z else GeomLib.forceZCoordinateToZ0(geom, h0)
        )
        viewpoints2["__VIEWPOINT_GEOM__"] = viewpoints2.geometry
        viewpoints2["__VIEWPOINT_PK__"] = range(len(viewpoints2))
        viewpoints2.geometry = viewpoints2.geometry.apply(lambda g: g.buffer(horizon))

        masks2 = overlay(masks, viewpoints2, how="intersection")
        masks2.geometry = masks2.apply(
            lambda row: GeomLib.forceZCoordinateToZ0(
                row.geometry, row[elevationFieldname] - row.__VIEWPOINT_GEOM__.z
            ),
            axis=1,
        )
        masks2.geometry = masks2.geometry.apply(
            lambda g: GeomLib.reverseRingOrientation(g.normalize())
        )
        masks2.geometry = masks2.apply(
            lambda row: MultiLineString(
                GeomLib.toListOfBipointsAsLineStringsInFrontOf(
                    row.__VIEWPOINT_GEOM__, row.geometry
                )
            ),
            axis=1,
        )
        if encode:
            masks2.__VIEWPOINT_GEOM__ = masks2.__VIEWPOINT_GEOM__.apply(
                lambda geom: geom.wkt
            )
        return masks2

    @staticmethod
    def test(ofile=None):
        import matplotlib.pyplot as plt
        from shapely import Point
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        # from t4gpd.morph.STGrid import STGrid

        # buildings = GeoDataFrameDemos.regularGridOfPlots2(nlines=4, ncols=4)
        # buildings["HAUTEUR"] = 10
        # vp = STGrid(buildings, dx=100, intoPoint=True, indoor=False).run()

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        viewpoints = GeoDataFrame(
            [{"gid": 100, "geometry": Point([355315, 6688413])}], crs=buildings.crs
        )

        masks = PrepareMasksLib.removeNonVisible25DMasks(
            viewpoints,
            buildings,
            elevationFieldname="HAUTEUR",
            horizon=40,
            h0=1.10,
            encode=True,
        )

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, color="grey")
        viewpoints.plot(ax=ax, column="gid", marker="+")
        masks.plot(ax=ax, column="gid", linewidth=5)
        plt.tight_layout()
        plt.show()

        if not ofile is None:
            buildings.to_file(ofile, layer="buildings")
            viewpoints.to_file(ofile, layer="viewpoints")
            masks.to_file(ofile, layer="masks")

        return masks

    @staticmethod
    def test2(ofile=None):
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos4 import GeoDataFrameDemos4
        from t4gpd.demos.NantesBDT import NantesBDT
        from t4gpd.morph.STPointsDensifier import STPointsDensifier

        buildings = NantesBDT.buildings()
        path = GeoDataFrameDemos4.comfortPathInNantesTrack()
        viewpoints = STPointsDensifier(path, distance=400).run()
        viewpoints.gid = range(len(viewpoints))

        masks = PrepareMasksLib.localMaskClipping(
            viewpoints, buildings, vp_pk="gid", buffDist=40, strict=False
        )

        minx, miny, maxx, maxy = masks.buffer(5).total_bounds

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, color="grey")
        path.plot(ax=ax, color="grey", linestyle="dashed", linewidth=1)
        viewpoints.plot(ax=ax, column="gid", marker="+")
        masks.plot(ax=ax, column="gid", legend=True)
        ax.axis("off")
        ax.axis([minx, maxx, miny, maxy])
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        if not ofile is None:
            buildings.to_file(ofile, layer="buildings")
            viewpoints.to_file(ofile, layer="viewpoints")
            masks.to_file(ofile, layer="masks")

        return masks


# masks = PrepareMasksLib.test("/tmp/PrepareMasksLib.gpkg")
# masks = PrepareMasksLib.test2("/tmp/PrepareMasksLib.gpkg")
