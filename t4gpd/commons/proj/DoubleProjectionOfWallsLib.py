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
import warnings
from numpy import cos, linspace, mean, pi, sin
from shapely import LinearRing, MultiLineString, MultiPolygon, Point, Polygon, union_all
from shapely.affinity import scale, translate
from shapely.ops import substring
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.raycasting.PrepareMasksLib import PrepareMasksLib
from t4gpd.commons.proj.DoubleProjectionLib import DoubleProjectionLib
from t4gpd.commons.WarnUtils import WarnUtils


class DoubleProjectionOfWallsLib(object):
    '''
    classdocs
    '''
    CIRCLE = LinearRing(zip(cos(linspace(0, 2*pi, 90)),
                        sin(linspace(0, 2*pi, 90))))
    warnings.formatwarning = WarnUtils.format_Warning_alt

    @staticmethod
    def __project_2d_point_onto_unit_circle(viewpoint, p, circle):
        curv_absc = circle.project(Point(p), normalized=True)
        pp = circle.interpolate(curv_absc, normalized=True)
        return [pp.x, pp.y, viewpoint[2]], curv_absc

    @staticmethod
    def __double_projection_of_LineString(prj, viewpoint, lineStringMask,
                                          size, npts, circle):
        pts = [lineStringMask.interpolate(
            x, normalized=True).coords[0] for x in linspace(0, 1, npts)]

        ppts = [prj(viewpoint, p, size) for p in pts]
        z0 = mean([p.z for p in ppts])

        pA, curvA = DoubleProjectionOfWallsLib.__project_2d_point_onto_unit_circle(
            viewpoint, ppts[0], circle)
        pB, curvB = DoubleProjectionOfWallsLib.__project_2d_point_onto_unit_circle(
            viewpoint, ppts[-1], circle)

        if (curvA < curvB):
            if (0.9 <= 1 - curvB + curvA):
                # TL 13.03.2024: Debug DoubleProjectionOfWallsLibTest.testWalls3()
                warnings.warn(f"Issue with viewpoint={viewpoint} and {lineStringMask.wkt}")
                return None
            arc1 = substring(circle,
                             start_dist=curvB,
                             end_dist=1,
                             normalized=True)
            arc2 = substring(circle,
                             start_dist=0,
                             end_dist=curvA,
                             normalized=True)
            arcPts = [(p[0], p[1], viewpoint[2]) for p in arc1.coords] +\
                [(p[0], p[1], viewpoint[2]) for p in arc2.coords]
        else:
            arc = substring(circle,
                            start_dist=curvB,
                            end_dist=curvA,
                            normalized=True)
            arcPts = [(p[0], p[1], viewpoint[2]) for p in arc.coords]

        return GeomLib.forceZCoordinateToZ0(Polygon(ppts + arcPts), z0=z0)

    @staticmethod
    def __double_projection_of_MultiLineString(prj, viewpoint, multiLineStringOfMasks,
                                               horizon, size, npts, circle):
        # FROM MultiLineString TO MultiPolygon
        circle = translate(circle, xoff=viewpoint.x, yoff=viewpoint.y)

        viewpoint = viewpoint.coords[0]
        multiPolygonOfMasks = [
            # GeomLib.forceZCoordinateToZ0(circle.buffer(1e-3), z0=-1)
        ]
        for lineStringMask in multiLineStringOfMasks.geoms:
            _polygon = DoubleProjectionOfWallsLib.__double_projection_of_LineString(
                prj, viewpoint, lineStringMask, size, npts, circle)
            if (_polygon is not None):
                multiPolygonOfMasks.append(_polygon)
        return MultiPolygon(multiPolygonOfMasks)

    @staticmethod
    def walls(sensors, buildings, horizon=100.0, elevationFieldname="HAUTEUR",
              h0=0.0, size=1, projectionName="Stereographic", npts=5,
              aggregate=True):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, sensors):
            raise Exception(
                "Illegal argument: buildings and sensors must share shames CRS!")

        prj = DoubleProjectionLib.projectionSwitch(projectionName)

        sensors2 = sensors.copy(deep=True)
        sensors2.geometry = sensors2.geometry.apply(
            lambda geom: geom if geom.has_z else GeomLib.forceZCoordinateToZ0(geom, h0))

        # PRE-PROCESSING
        masks = PrepareMasksLib.removeNonVisible25DMasks(
            sensors2, buildings, elevationFieldname, horizon, h0
        )
        circle = scale(DoubleProjectionOfWallsLib.CIRCLE,
                       xfact=size, yfact=size, origin=(0, 0))

        # PROCESSING
        masks.geometry = masks.apply(
            lambda row: DoubleProjectionOfWallsLib.__double_projection_of_MultiLineString(
                prj, row.__VIEWPOINT__, row.geometry, horizon, size=size, npts=npts, circle=circle),
            axis=1)

        # POST-PROCESSING
        masks.drop(columns=["__VIEWPOINT__"], inplace=True)
        if aggregate:
            masks.geometry = masks.geometry.apply(
                lambda geom: union_all(geom.geoms)
            )
            if ("isoaire" == projectionName.lower()):
                tmp = pi * size**2
                masks["svf"] = masks.geometry.apply(
                    lambda geom: geom.area / tmp)
        else:
            masks = masks.explode(ignore_index=True)
            masks["depth"] = masks.geometry.apply(
                lambda geom: geom.exterior.coords[0][2])

        return masks


def main():
    import matplotlib.pyplot as plt
    from geopandas import clip
    from matplotlib_scalebar.scalebar import ScaleBar
    from shapely.geometry import box
    from t4gpd.commons.proj.DoubleProjectionOfPointsLib import DoubleProjectionOfPointsLib
    from t4gpd.demos.GeoDataFrameDemosC import GeoDataFrameDemosC
    from t4gpd.morph.STGrid import STGrid

    iris = GeoDataFrameDemosC.irisTastavin()
    buildings = GeoDataFrameDemosC.irisTastavinBuildings()
    streetlights = GeoDataFrameDemosC.irisTastavinStreetlights()

    streetlights.geometry = streetlights.geometry.apply(
        lambda geom: GeomLib.forceZCoordinateToZ0(geom, 12))

    dx = 150
    grid = STGrid(buildings, dx=dx, dy=None, indoor=False, intoPoint=True,
                  encode=True, withDist=False).execute()  # < 15 sec
    sensors = clip(grid, iris, keep_geom_type=True)
    # sensors = sensors[sensors.gid == 6]

    size = 4
    projectionName = "Isoaire"
    # projectionName="Orthogonal"
    # projectionName = "Stereographic"
    pp = DoubleProjectionOfPointsLib.points(
        sensors, streetlights, h0=0,
        size=size, projectionName=projectionName)
    pmasks = DoubleProjectionOfWallsLib.walls(
        sensors, buildings, horizon=100.0, elevationFieldname="HAUTEUR",
        h0=0.0, size=size, projectionName=projectionName, npts=5, aggregate=False)

    # iris.to_file("/tmp/iris.shp")
    # buildings.to_file("/tmp/buildings.shp")
    # streetlights.to_file("/tmp/streetlights.shp")
    # sensors.to_file("/tmp/sensors.shp")
    # pp.to_file("/tmp/pp.shp")
    # pmasks.to_file("/tmp/pmasks.shp")

    minx, miny, maxx, maxy = box(
        *sensors[sensors.gid == 6].total_bounds).buffer(6.0).bounds
    fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.35 * 8.26))
    ax.set_title(
        f"Montpellier (34), IRIS Tastavin ({projectionName})", size=28)
    iris.boundary.plot(ax=ax, color="red", linestyle="dotted")
    buildings.plot(ax=ax, color="grey")
    sensors.plot(ax=ax, color="black", marker="P")
    pmasks.plot(ax=ax, column="depth", cmap="Spectral",
                edgecolor="black", alpha=0.75)
    pp.plot(ax=ax, column="depth", cmap="Spectral", marker="+", legend="True")
    ax.axis("off")
    # ax.axis([minx, maxx, miny, maxy])
    scalebar = ScaleBar(dx=1.0, units="m", length_fraction=None, box_alpha=0.85,
                        width_fraction=0.005, location="lower right", frameon=True)
    ax.add_artist(scalebar)
    fig.tight_layout()
    plt.show()
    plt.close(fig)

    return pp, pmasks


# pp, pmasks = main()
