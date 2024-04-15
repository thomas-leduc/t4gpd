'''
Created on 10 nov. 2023

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
'''
from geopandas import GeoDataFrame, overlay
from shapely import MultiLineString, union_all
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PrepareMasksLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def extrudeBuildingsOnFlatland(buildings, elevationFieldname="HAUTEUR", oriented=True,
                                   make_valid=True):
        result = buildings.copy(deep=True)
        if make_valid:
            result.geometry = result.geometry.apply(lambda g: g.buffer(0))
        result.geometry = result.apply(
            lambda rows: GeomLib.forceZCoordinateToZ0(
                rows.geometry, z0=rows[elevationFieldname]), axis=1)
        if oriented:
            result.geometry = result.geometry.apply(
                lambda g: GeomLib.reverseRingOrientation(g.normalize()))
        return result

    @staticmethod
    def getMasksAsBipoints(buildings, oriented=True, make_valid=True, union=False):
        # result = buildings.geometry.to_frame()
        result = buildings.copy(deep=True)
        if make_valid:
            result.geometry = result.geometry.apply(lambda g: g.buffer(0))
        if union:
            result = GeoDataFrame(
                [{"geometry": union_all(result.geometry)}], crs=buildings.crs)
        if oriented:
            result.geometry = result.geometry.apply(
                lambda g: GeomLib.reverseRingOrientation(g.normalize()))
        result.geometry = result.geometry.apply(lambda g: MultiLineString(
            GeomLib.toListOfBipointsAsLineStrings(g)))
        result = result.explode(ignore_index=True, index_parts=True)
        return result

    @staticmethod
    def removeNonVisible25DMasks(viewpoints, masks, elevationFieldname, horizon, h0):
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpoints, "GeoDataFrame")
        if not isinstance(masks, GeoDataFrame):
            raise IllegalArgumentTypeException(masks, "GeoDataFrame")
        if not elevationFieldname in masks:
            raise Exception(
                f"{elevationFieldname} is not a relevant field name!")
        if not GeoDataFrameLib.shareTheSameCrs(viewpoints, masks):
            raise Exception(
                "Illegal argument: viewpoints and masks are expected to share the same crs!")

        viewpoints2 = viewpoints.copy(deep=True)
        viewpoints2.geometry = viewpoints2.geometry.apply(
            lambda geom: geom if geom.has_z else GeomLib.forceZCoordinateToZ0(geom, h0))
        viewpoints2["__VIEWPOINT__"] = viewpoints2.geometry
        viewpoints2.geometry = viewpoints2.geometry.apply(
            lambda g: g.buffer(horizon))

        masks2 = overlay(
            masks[[elevationFieldname, "geometry"]], viewpoints2, how="intersection")
        masks2.geometry = masks2.apply(
            lambda row: GeomLib.forceZCoordinateToZ0(
                row.geometry, row[elevationFieldname]-row.__VIEWPOINT__.z),
            axis=1)
        masks2.geometry = masks2.geometry.apply(
            lambda g: GeomLib.reverseRingOrientation(g.normalize()))
        masks2.geometry = masks2.apply(
            lambda row: MultiLineString(
                GeomLib.toListOfBipointsAsLineStringsInFrontOf(
                    row.__VIEWPOINT__, row.geometry)), axis=1)
        masks2 = masks2.dissolve(by="__VIEWPOINT__", as_index=False)
        masks2.geometry = masks2.geometry.apply(
            lambda geom: geom if isinstance(
                geom, MultiLineString) else MultiLineString([geom]))
        return masks2

"""
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STGrid import STGrid

        # buildings = GeoDataFrameDemos.ensaNantesBuildings()
        buildings = GeoDataFrameDemos.regularGridOfPlots2(nlines=4, ncols=4)
        buildings["HAUTEUR"] = 10

        vp = STGrid(buildings, dx=100, intoPoint=True, indoor=False).run()
        masks = PrepareMasksLib.removeNonVisible25DMasks(
            vp, buildings, elevationFieldname="HAUTEUR", horizon=40, h0=1.10)
        # masks.to_csv("/tmp/1.csv")

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, color="grey")
        vp.plot(ax=ax, column="gid", marker="+")
        masks.plot(ax=ax, column="gid", linewidth=5)
        plt.tight_layout()
        plt.show()


PrepareMasksLib.test()
"""