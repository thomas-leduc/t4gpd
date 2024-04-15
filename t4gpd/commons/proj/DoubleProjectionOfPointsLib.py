'''
Created on 30 jan. 2024

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
from t4gpd.commons.CartesianProductLib import CartesianProductLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.proj.DoubleProjectionLib import DoubleProjectionLib


class DoubleProjectionOfPointsLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def points(sensors, streetlights, horizon=None, h0=0.0, size=1, projectionName="Stereographic",
               encode=True):
        if not GeoDataFrameLib.shareTheSameCrs(sensors, streetlights):
            raise Exception(
                "Illegal argument: sensors and streetlights must share shames CRS!")

        prj = DoubleProjectionLib.projectionSwitch(projectionName)

        sensors2 = sensors.copy(deep=True)
        sensors2.geometry = sensors2.geometry.apply(
            lambda geom: geom if geom.has_z else GeomLib.forceZCoordinateToZ0(geom, h0))

        if horizon is None:
            result = CartesianProductLib.product(sensors2, streetlights)
        else:
            result = CartesianProductLib.product_within_distance2(
                sensors2, streetlights, horizon)

        result["geometry"] = result.apply(
            lambda row: prj(row.geometry_x, row.geometry_y, size=size), axis=1)
        result["depth"] = result.geometry.apply(lambda p: p.z)
        result.geometry = result.apply(
            lambda row: GeomLib.forceZCoordinateToZ0(
                row.geometry, row.geometry_x.z), axis=1)

        if encode:
            result.geometry_x = result.geometry_x.apply(lambda g: g.wkt)
            result.geometry_y = result.geometry_y.apply(lambda g: g.wkt)

        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar
        from geopandas import clip
        from t4gpd.demos.GeoDataFrameDemosC import GeoDataFrameDemosC
        from t4gpd.morph.STGrid import STGrid

        iris = GeoDataFrameDemosC.irisTastavin()
        buildings = GeoDataFrameDemosC.irisTastavinBuildings()
        roads = GeoDataFrameDemosC.irisTastavinRoads()
        streetlights = GeoDataFrameDemosC.irisTastavinStreetlights()
        trees = GeoDataFrameDemosC.irisTastavinTrees()

        streetlights.geometry = streetlights.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, 12))

        dx = 150
        grid = STGrid(buildings, dx=dx, dy=None, indoor=False, intoPoint=True,
                      encode=True, withDist=False).execute()  # < 15 sec
        sensors = clip(grid, iris, keep_geom_type=True)

        projectionName = "Isoaire"
        projectionName = "Orthogonal"
        projectionName = "Stereographic"
        pp = DoubleProjectionOfPointsLib.points(
            sensors, streetlights, horizon=100, h0=0.0,
            size=1, projectionName=projectionName)

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.35 * 8.26))
        ax.set_title(
            f"Montpellier (34), IRIS Tastavin ({projectionName})", size=28)
        iris.boundary.plot(ax=ax, color="red", linestyle="dotted")
        buildings.plot(ax=ax, color="grey")
        # big_buildings.plot(ax=ax, color="lightgrey")
        # grid.boundary.plot(ax=ax, color="green")
        sensors.buffer(1.0).boundary.plot(ax=ax, color="red")
        pp.plot(ax=ax, column="depth", cmap="Spectral",
                marker="+", legend=True)
        # skymaps.plot(ax=ax, color="black", linewidth=0.15)
        ax.axis("off")
        # ax.legend(loc="lower left", fontsize=18)
        scalebar = ScaleBar(dx=1.0, units="m", length_fraction=None, box_alpha=0.85,
                            width_fraction=0.005, location="lower right", frameon=True)
        ax.add_artist(scalebar)
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return pp


# pp = DoubleProjectionOfPointsLib.test()
