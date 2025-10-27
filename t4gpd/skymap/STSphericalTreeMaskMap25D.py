"""
Created on 26 May 2025

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
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.proj.DoubleProjectionOfSpheresLib import DoubleProjectionOfSpheresLib


class STSphericalTreeMaskMap25D(GeoProcess):
    """
    classdocs
    """

    def __init__(
        self,
        viewpoints,
        trees,
        horizon,
        crownRadiusFieldname,
        h0=1.18,
        size=4.0,
        projectionName="Stereographic",
        npts=4,
    ):
        """
        Constructor
        """
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpoints, "viewpoints GeoDataFrame")
        if not isinstance(trees, GeoDataFrame):
            raise IllegalArgumentTypeException(trees, "trees GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(viewpoints, trees):
            raise Exception(
                "Illegal argument: viewpoints and trees are expected to share the same crs!"
            )
        self.viewpoints = viewpoints
        self.trees = trees
        self.horizon = horizon
        self.crownRadiusFieldname = crownRadiusFieldname
        self.h0 = h0
        self.size = size
        self.projectionName = projectionName
        self.npts = npts

    def run(self):
        ptrees = DoubleProjectionOfSpheresLib.trees(
            self.viewpoints,
            self.trees,
            horizon=self.horizon,
            crownRadiusFieldname=self.crownRadiusFieldname,
            h0=self.h0,
            size=self.size,
            projectionName=self.projectionName,
            npts=self.npts,
        )
        return ptrees

    def test():
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar
        from t4gpd.demos.GeoDataFrameDemos6 import GeoDataFrameDemos6
        from t4gpd.morph.STPointsDensifier import STPointsDensifier
        from t4gpd.skymap.STBodyMaskMap25D import STBodyMaskMap25D

        h0 = 1.18
        buildings = GeoDataFrameDemos6.nizanDistrictInNantesBuildings()
        path = GeoDataFrameDemos6.nizanDistrictInNantesPath1()
        trees = GeoDataFrameDemos6.nizanDistrictInNantesTrees()
        trees.geometry = trees.apply(
            lambda row: GeomLib.forceZCoordinateToZ0(
                # row.geometry, row.h_arbre - row.r_houppier
                row.geometry,
                row.h_arbre - h0,
            ),
            axis=1,
        )
        sensors = STPointsDensifier(path, distance=30).run()
        sensors = sensors.loc[:, ["geometry"]]
        sensors.insert(0, "gid", range(len(sensors)))

        projectionName = "Stereographic"
        bodymasks = STBodyMaskMap25D(
            sensors, h0=h0, size=1, epsilon=1e-2, projectionName=projectionName
        ).run()
        treemasks = STSphericalTreeMaskMap25D(
            sensors,
            trees,
            horizon=30,
            crownRadiusFieldname="r_houppier",
            h0=h0,
            size=1,
            projectionName=projectionName,
            npts=8,
        ).run()

        # PLOTTING
        minx, miny, maxx, maxy = path.buffer(5).total_bounds

        fig, ax = plt.subplots(figsize=(1.8 * 8.26, 0.6 * 8.26))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="darkgrey")
        path.plot(ax=ax, color="grey", linestyle="-.", linewidth=1)
        trees.plot(ax=ax, color="green", marker="o")
        trees.apply(
            lambda x: ax.annotate(
                text=f"h={x.geometry.z:.1f}\nr={x.r_houppier:.1f}",
                xy=x.geometry.coords[0][:2],
                color="green",
                size=10,
                ha="left",
                va="bottom",
            ),
            axis=1,
        )
        bodymasks.plot(ax=ax, color="red")
        treemasks.plot(ax=ax, color="lightgreen")
        sensors.plot(ax=ax, color="red", marker="P")
        scalebar = ScaleBar(
            dx=1.0,
            units="m",
            length_fraction=None,
            width_fraction=0.005,
            location="lower left",
            frameon=True,
        )
        ax.add_artist(scalebar)
        ax.axis("off")
        ax.axis([minx, maxx, miny, maxy])
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return bodymasks, treemasks


# bodymasks, treemasks = STSphericalTreeMaskMap25D.test()
# print(treemasks)
