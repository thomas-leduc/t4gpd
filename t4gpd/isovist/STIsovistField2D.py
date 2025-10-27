"""
Created on 24 jul. 2023

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
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

# from t4gpd.commons.raycasting.PrepareMasksLib import PrepareMasksLib
from t4gpd.commons.raycasting.RayCasting2DLib import RayCasting2DLib


class STIsovistField2D(GeoProcess):
    """
    classdocs
    """

    def __init__(
        self, buildings, viewpoints, nRays=64, rayLength=100.0, withIndices=False
    ):
        """
        Constructor
        """
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, "buildings GeoDataFrame")
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpoints, "viewpoints GeoDataFrame")

        if not GeoDataFrameLib.shareTheSameCrs(buildings, viewpoints):
            raise Exception(
                "Illegal argument: buildings and viewpoints are expected to share the same crs!"
            )

        self.buildings = buildings
        # CLEAN GEOMETRIES
        self.buildings.geometry = self.buildings.geometry.apply(lambda g: g.buffer(0))

        # the following instruction seems to slow down processing
        # self.buildings = PrepareMasksLib.getMasksAsBipoints(
        #     buildings, oriented=True, make_valid=True)

        self.rays = RayCasting2DLib.get2DPanopticRaysGeoDataFrame(
            viewpoints, rayLength, nRays
        )
        self.nRays = nRays
        self.withIndices = withIndices

    def run(self):
        isovRaysField, isovField = RayCasting2DLib.multipleRayCast2D(
            self.buildings, self.rays, self.withIndices
        )
        return isovRaysField, isovField

    def test(ofile=None):
        """
        Test method for the class.
        """
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos4 import GeoDataFrameDemos4
        from t4gpd.demos.NantesBDT import NantesBDT
        from t4gpd.morph.STPointsDensifier import STPointsDensifier

        buildings = NantesBDT.buildings()
        path = GeoDataFrameDemos4.comfortPathInNantesTrack()
        viewpoints = STPointsDensifier(path, distance=400).run()
        viewpoints.gid = range(len(viewpoints))

        isovRaysField, isovField = STIsovistField2D(
            buildings, viewpoints, nRays=64, rayLength=100.0
        ).run()

        minx, miny, maxx, maxy = isovField.buffer(5).total_bounds

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        buildings.plot(ax=ax, color="grey")
        path.plot(ax=ax, color="grey", linestyle="dashed", linewidth=1)
        viewpoints.plot(ax=ax, column="gid", marker="+")
        isovField.plot(
            ax=ax, column="gid", alpha=0.5, legend=True, legend_kwds={"shrink": 0.8}
        )
        isovRaysField.plot(ax=ax, column="gid", alpha=0.5)
        ax.axis("off")
        ax.axis([minx, maxx, miny, maxy])
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        if not ofile is None:
            buildings.to_file(ofile, layer="buildings")
            viewpoints.to_file(ofile, layer="viewpoints")
            isovRaysField.to_file(ofile, layer="isovRaysField")
            isovField.to_file(ofile, layer="isovField")

        return isovRaysField, isovField


# isovRaysField, isovField = STIsovistField2D.test()
