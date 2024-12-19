'''
Created on 5 feb. 2024

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
from numpy import arcsin, arctan2, asarray, cos, linspace, mean, pi, sin, sqrt
from shapely import Point, Polygon
from t4gpd.commons.CartesianProductLib import CartesianProductLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.commons.proj.DoubleProjectionLib import DoubleProjectionLib


class DoubleProjectionOfSpheresLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def __tree_crown_mask_diameter(viewpoint, treeCrownCenter, treeCrownRadius):
        Ox, Oy, Oz = viewpoint.coords[0]
        Ax, Ay, Az = treeCrownCenter.coords[0]

        u = (Ax-Ox, Ay-Oy, 0)
        normU = sqrt(u[0]**2 + u[1]**2)
        u = (u[0]/normU, u[1]/normU, 0)

        r, d = treeCrownRadius, sqrt((Ax-Ox)**2 + (Ay-Oy)**2 + (Az-Oz)**2)

        if (d > r):
            beta = arcsin(r / d)
            if (Ax == Ox):
                alpha = pi / 2
            else:
                alpha = arctan2(Az-Oz, normU)

            magn = sqrt(d**2 - r**2)
            B = [
                Ox + cos(alpha + beta) * magn * u[0],
                Oy + cos(alpha + beta) * magn * u[1],
                Oz + sin(alpha + beta) * magn
            ]
            C = [
                Ox + cos(alpha - beta) * magn * u[0],
                Oy + cos(alpha - beta) * magn * u[1],
                Oz + sin(alpha - beta) * magn
            ]
            return [Ox, Oy, Oz], [Ax, Ay, Az], B, C
        raise Exception("TODO: To be developed!")

    @staticmethod
    def __tree_crown_mask_contour(O, A, B, npts):
        (Ox, Oy, Oz), (Ax, Ay, Az), (Bx, By, Bz) = O, A, B
        AA = asarray(A)
        u = asarray((Ax-Ox, Ay-Oy, Az-Oz))
        invNormU = 1 / sqrt(u[0]**2 + u[1]**2 + u[2]**2)
        u = invNormU * u
        v = asarray((Bx-Ax, By-Ay, Bz-Az))
        w = asarray(GeomLib3D.crossProduct(u, v))

        thetas = linspace(0, 2*pi, npts, endpoint=False)
        pts = [Point(AA + cos(theta) * v + sin(theta) * w) for theta in thetas]
        return pts

    @staticmethod
    def __projection_of_tree_crown(prj, viewpoint, treeCrownCenter,
                                   treeCrownRadius, size, npts):
        O, A, B, C = DoubleProjectionOfSpheresLib.__tree_crown_mask_diameter(
            viewpoint, treeCrownCenter, treeCrownRadius)

        if ("_stereographic_projection" == prj.__name__):
            ppB = prj(O, B, size)
            ppC = prj(O, C, size)

            depth = (ppB.z + ppC.z) / 2
            diameter = sqrt((ppC.x - ppB.x)**2 + (ppC.y - ppB.y)**2) / 2
            center = Point([(ppB.x + ppC.x) / 2, (ppB.y + ppC.y) / 2])
            disk = center.buffer(diameter/2)

            return GeomLib.forceZCoordinateToZ0(disk, z0=depth)

        pts = DoubleProjectionOfSpheresLib.__tree_crown_mask_contour(
            O, A, B, npts)
        ppts = [prj(viewpoint, p, size) for p in pts]
        z0 = mean([p.z for p in ppts])
        return GeomLib.forceZCoordinateToZ0(Polygon(ppts), z0=z0)

    @staticmethod
    def trees(sensors, trees, horizon, crownRadiusFieldname,
              h0=0.0, size=1, projectionName="Stereographic", npts=4):
        if not GeoDataFrameLib.shareTheSameCrs(trees, sensors):
            raise Exception(
                "Illegal argument: trees and sensors must share shames CRS!")

        prj = DoubleProjectionLib.projection_switch(projectionName)

        sensors2 = sensors.copy(deep=True)
        sensors2.geometry = sensors2.geometry.apply(
            lambda geom: geom if geom.has_z else GeomLib.forceZCoordinateToZ0(geom, h0))

        # PRE-PROCESSING
        result = CartesianProductLib.product_within_distance2(
            sensors2, trees, horizon)

        # PROCESSING
        result["geometry"] = result.apply(
            lambda row: DoubleProjectionOfSpheresLib.__projection_of_tree_crown(
                prj, row.geometry_x, row.geometry_y, row[crownRadiusFieldname], size=size, npts=npts),
            axis=1)

        # POST-PROCESSING
        result["depth"] = result.geometry.apply(
            lambda geom: geom.exterior.coords[0][2])

        return result

    def test():
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar
        from shapely.geometry import box
        from t4gpd.commons.proj.DoubleProjectionOfWallsLib import DoubleProjectionOfWallsLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.morph.STGrid import STGrid

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        trees = GeoDataFrameDemos.ensaNantesTrees()

        trees.geometry = trees.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, 12))
        trees["crown_radius"] = 4

        dx = 100
        grid = STGrid(buildings, dx=dx, dy=None, indoor=False, intoPoint=True,
                      encode=True, withDist=False).execute()  # < 15 sec
        sensors = grid

        size = 4
        # projectionName = "Isoaire"
        # projectionName = "orthogonal"
        projectionName = "Stereographic"
        pbuildings = DoubleProjectionOfWallsLib.walls(
            sensors, buildings, horizon=50.0, elevationFieldname="HAUTEUR",
            h0=0.0, size=size, projectionName=projectionName, npts=5, aggregate=False)
        ptrees = DoubleProjectionOfSpheresLib.trees(
            sensors, trees, horizon=50.0, crownRadiusFieldname="crown_radius",
            h0=0.0, size=size, projectionName=projectionName)

        # minx, miny, maxx, maxy = box(
        #     *sensors[sensors.gid == 6].total_bounds).buffer(6.0).bounds
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.35 * 8.26))
        ax.set_title(f"Nantes (44) ({projectionName})", size=28)
        buildings.plot(ax=ax, color="grey")
        sensors.plot(ax=ax, color="black", marker="P")
        trees.plot(ax=ax, color="green", marker=".")

        pbuildings.plot(ax=ax, column="depth", cmap="Spectral",
                        edgecolor="black", alpha=0.75)
        ptrees.plot(ax=ax, column="depth", cmap="Spectral",
                    edgecolor="black", alpha=0.75, legend="True")

        ax.axis("off")
        # ax.axis([minx, maxx, miny, maxy])
        # ax.legend(loc="lower left", fontsize=18)
        scalebar = ScaleBar(dx=1.0, units="m", length_fraction=None, box_alpha=0.85,
                            width_fraction=0.005, location="lower right", frameon=True)
        ax.add_artist(scalebar)
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return ptrees


# ptrees = DoubleProjectionOfSpheresLib.test()
