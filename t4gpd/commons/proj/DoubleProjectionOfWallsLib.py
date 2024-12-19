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
from geopandas import GeoDataFrame
from numpy import asarray, cos, dot, linspace, mean, pi, sin, sum
from pandas import concat
from shapely import LineString, LinearRing, Point, Polygon, get_parts, union_all
from shapely.affinity import scale, translate
from shapely.ops import substring
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.overlap.OverlapLib import OverlapLib
from t4gpd.commons.raycasting.PrepareMasksLib import PrepareMasksLib
from t4gpd.commons.proj.DoubleProjectionLib import DoubleProjectionLib
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.commons.raycasting.SurroundingMasks25DLib import SurroundingMasks25DLib


class DoubleProjectionOfWallsLib(object):
    '''
    classdocs
    '''
    CIRCLE = LinearRing(zip(cos(linspace(0, 2*pi, 90)),
                        sin(linspace(0, 2*pi, 90))))
    NO_IDX = -123456789
    warnings.formatwarning = WarnUtils.format_Warning_alt

    @staticmethod
    def __project_2d_point_onto_unit_circle(viewpoint, p, circle):
        curv_absc = circle.project(Point(p), normalized=True)
        pp = circle.interpolate(curv_absc, normalized=True)
        return [pp.x, pp.y, viewpoint[2]], curv_absc

    @staticmethod
    def __double_projection_of_LineString(prj, viewpoint, lineStringMask,
                                          size, npts, circle):
        circle = translate(circle, xoff=viewpoint.x, yoff=viewpoint.y)

        pts = [lineStringMask.interpolate(
            x, normalized=True).coords[0] for x in linspace(0, 1, npts)]

        viewpoint = viewpoint.coords[0]
        ppts = [prj(viewpoint, p, size) for p in pts]
        z0 = mean([p.z for p in ppts])

        pA, curvA = DoubleProjectionOfWallsLib.__project_2d_point_onto_unit_circle(
            viewpoint, ppts[0], circle)
        pB, curvB = DoubleProjectionOfWallsLib.__project_2d_point_onto_unit_circle(
            viewpoint, ppts[-1], circle)

        if (curvA < curvB):
            if (0.9 <= 1 - curvB + curvA):
                # TL 13.03.2024: Debug DoubleProjectionOfWallsLibTest.testWalls3()
                warnings.warn(
                    f"Issue with viewpoint={viewpoint} and {lineStringMask.wkt}")
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
    def __foo(reverse_prj, size, masks, rayLength):
        vppks = sorted(masks.__VIEWPOINT_PK__.unique())

        masks4 = []
        for vppk in vppks:
            masks2 = masks.loc[masks[vppk ==
                                     masks.__VIEWPOINT_PK__].index,
                               ["__MASK_IDS__", "__VIEWPOINT_PK__", "__VIEWPOINT_GEOM__", "__WALL_MASK__", "geometry"]]
            vpgeom = masks2.__VIEWPOINT_GEOM__.tolist()[0]

            masks3 = OverlapLib.overlap(
                masks2, fieldnames=["__MASK_IDS__", "__WALL_MASK__"], patchid="patch_id")
            masks3["__VIEWPOINT_PK__"] = vppk
            masks3["__VIEWPOINT_GEOM__"] = vpgeom
            masks3["__REPRESENTATIVE_POINT__"] = masks3.geometry.apply(
                lambda geom: GeomLib.forceZCoordinateToZ0(geom.representative_point(), z0=vpgeom.z))
            masks3["__MASK_AREA__"] = masks3.geometry.apply(
                lambda geom: geom.area)
            masks4.append(masks3)

        masks4 = GeoDataFrame(concat(masks4), crs=masks.crs)
        masks4.__REPRESENTATIVE_POINT__ = masks4.apply(
            lambda row: reverse_prj(
                row.__VIEWPOINT_GEOM__, row.__REPRESENTATIVE_POINT__, size),
            axis=1)
        masks4["__1ST_FRONT__"] = masks4.apply(lambda row: DoubleProjectionOfWallsLib.__managing_overlapping_fronts(
            row.__VIEWPOINT_GEOM__, row.__REPRESENTATIVE_POINT__, row.__WALL_MASK__, rayLength), axis=1)

        def __get_id(ids, mid): return f"ERR_{vppk}" if (
            DoubleProjectionOfWallsLib.NO_IDX == mid) else ids[mid]
        masks4["__MASK_DIST__"] = masks4.__1ST_FRONT__.apply(lambda v: v[0])
        masks4["__MASK_ID__"] = masks4.apply(lambda row: __get_id(
            row.__MASK_IDS__, row.__1ST_FRONT__[1]), axis=1)

        def __get_wall_mask(
            wall_masks, mid): return LineString([]) if (DoubleProjectionOfWallsLib.NO_IDX == mid) else wall_masks[mid]
        masks4["__WALL_MASK__"] = masks4.apply(lambda row: __get_wall_mask(
            row.__WALL_MASK__, row.__1ST_FRONT__[1]), axis=1)

        masks4 = masks4.dissolve(by=["__VIEWPOINT_PK__", "__MASK_ID__", "__WALL_MASK__"], aggfunc={
                                 "__VIEWPOINT_GEOM__": "first", "__MASK_DIST__": list,
                                 "__MASK_AREA__": list}, as_index=True)

        def __get_dist(dists, areas): return dot(
            asarray(areas), asarray(dists)) / sum(asarray(areas))
        masks4["__DEPTH__"] = masks4.apply(lambda row: __get_dist(
            row.__MASK_DIST__, row.__MASK_AREA__), axis=1)

        masks4.reset_index(drop=False, inplace=True)
        masks4.drop(columns=["__MASK_DIST__", "__MASK_AREA__"], inplace=True)
        return masks4

    @staticmethod
    def __managing_overlapping_fronts(viewpoint, representative_point, wall_masks, rayLength):
        vp, rp, d = viewpoint, representative_point, viewpoint.distance(
            representative_point)
        ray = LineString([
            (vp.x, vp.y),
            (vp.x + (rp.x - vp.x) * (rayLength / d),
             vp.y + (rp.y - vp.y) * (rayLength / d)),
        ])

        minDist, minIdx = float("inf"), DoubleProjectionOfWallsLib.NO_IDX
        for idx, __WALL_MASK__ in enumerate(wall_masks):
            dist = vp.distance(ray.intersection(__WALL_MASK__))
            if (dist < minDist):
                minDist, minIdx = dist, idx

        # if minIdx is None:
        #     for idx, __WALL_MASK__ in enumerate(wall_masks):
        #         dist = ray.distance(__WALL_MASK__)
        #         if (dist < minDist):
        #             minDist, minIdx = dist, idx

        return minDist, minIdx
        # return minIdx

    @staticmethod
    def walls(sensors, buildings, maskidFieldname="ID", elevationFieldname="HAUTEUR",
              horizon=100.0, h0=0.0, size=1, projectionName="Stereographic", npts=5,
              aggregate=True, encode=True):
        if not GeoDataFrameLib.shareTheSameCrs(buildings, sensors):
            raise Exception(
                "Illegal argument: buildings and sensors must share shames CRS!")

        rayLength = GeoDataFrameLib.getBBoxDiagonal(buildings).length

        prj = DoubleProjectionLib.projection_switch(projectionName)
        reverse_prj = DoubleProjectionLib.reverse_projection_switch(
            projectionName)

        sensors2 = sensors.copy(deep=True)
        sensors2.geometry = sensors2.geometry.apply(
            lambda geom: geom if geom.has_z else GeomLib.forceZCoordinateToZ0(geom, h0))

        # PRE-PROCESSING
        masks = buildings.assign(__MASK_IDS__=lambda row: row[maskidFieldname])
        masks = PrepareMasksLib.removeNonVisible25DMasks(
            sensors2, masks, elevationFieldname, horizon, h0
        )
        # masks.to_csv("/tmp/1.csv", index=False, sep=";")  # DEBUG
        # masks = SurroundingMasks25DLib.removeHidden25DMasks(masks)
        # masks.to_csv("/tmp/2.csv", index=False, sep=";")  # DEBUG

        circle = scale(DoubleProjectionOfWallsLib.CIRCLE,
                       xfact=size, yfact=size, origin=(0, 0))

        # PROCESSING
        masks = masks.explode(ignore_index=True)  # Debug 23.08.2028
        masks["__WALL_MASK__"] = masks.loc[:, "geometry"]
        # masks.to_csv("/tmp/3.csv", index=False, sep=";")
        masks.geometry = masks.apply(
            lambda row: DoubleProjectionOfWallsLib.__double_projection_of_LineString(
                prj, row.__VIEWPOINT_GEOM__, row.geometry, size=size, npts=npts, circle=circle),
            axis=1)
        # masks.to_csv("/tmp/4.csv", index=False, sep=";")

        masks = DoubleProjectionOfWallsLib.__foo(
            reverse_prj, size, masks, rayLength)
        # masks.to_csv("/tmp/5.csv", index=False, sep=";")

        # POST-PROCESSING
        # masks.drop(columns=["__VIEWPOINT__"], inplace=True)
        if aggregate:
            masks.__VIEWPOINT_GEOM__ = masks.__VIEWPOINT_GEOM__.apply(
                lambda g: g.wkt)
            masks = masks.dissolve(
                by=["__VIEWPOINT_PK__", "__VIEWPOINT_GEOM__"], as_index=True)
            masks.geometry = masks.geometry.apply(
                lambda geom: geom.buffer(0))
            masks.reset_index(drop=False, inplace=True)
            masks.drop(
                columns=["__MASK_ID__", "__WALL_MASK__", "__DEPTH__"], inplace=True)

            if ("isoaire" == projectionName.lower()):
                tmp = pi * size**2
                masks["svf"] = masks.geometry.apply(
                    lambda geom: geom.area / tmp)
        else:
            masks = masks.explode(ignore_index=True)
            masks.rename(columns={"__DEPTH__": "depth"}, inplace=True)
            masks.depth = masks.depth.apply(
                lambda v: horizon if (float("inf") == v) else v)

        if encode:
            if "__REPRESENTATIVE_POINT__" in masks:
                masks.__REPRESENTATIVE_POINT__ = masks.__REPRESENTATIVE_POINT__.apply(
                    lambda g: g.wkt)
            if "__WALL_MASK__" in masks:
                masks.__WALL_MASK__ = masks.__WALL_MASK__.apply(
                    lambda g: g.wkt)

        return masks

    def test(ofile=None):
        import matplotlib.pyplot as plt
        from geopandas import clip
        from matplotlib_scalebar.scalebar import ScaleBar
        from shapely.geometry import box
        from t4gpd.commons.proj.DoubleProjectionOfPointsLib import DoubleProjectionOfPointsLib
        from t4gpd.demos.GeoDataFrameDemosC import GeoDataFrameDemosC
        from t4gpd.morph.STGrid import STGrid

        iris = GeoDataFrameDemosC.irisTastavin()
        buildings = GeoDataFrameDemosC.irisTastavinBuildings()
        # buildings.ID = buildings.ID.apply(lambda v: v[-6:-1])
        streetlights = GeoDataFrameDemosC.irisTastavinStreetlights()

        streetlights.geometry = streetlights.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(geom, 12))

        dx = 150
        grid = STGrid(buildings, dx=dx, dy=None, indoor=False, intoPoint=True,
                      encode=True, withDist=False).execute()  # < 15 sec
        sensors = clip(grid, iris, keep_geom_type=True)
        # sensors = sensors[sensors.gid == 13]

        size = 4
        # projectionName = "Isoaire"
        # projectionName="Orthogonal"
        projectionName = "Stereographic"
        pp = DoubleProjectionOfPointsLib.points(
            sensors, streetlights, h0=0,
            size=size, projectionName=projectionName, encode=True)
        pmasks = DoubleProjectionOfWallsLib.walls(
            sensors, buildings, maskidFieldname="ID", elevationFieldname="HAUTEUR",
            horizon=100.0, h0=0.0, size=size, projectionName=projectionName, npts=5,
            aggregate=False, encode=True)

        if not ofile is None:
            iris.to_file(ofile, layer="iris")
            buildings.to_file(ofile, layer="buildings")
            streetlights.to_file(ofile, layer="streetlights")
            sensors.to_file(ofile, layer="sensors")
            pp.to_file(ofile, layer="pp")
            pmasks.to_file(ofile, layer="pmasks")

        # minx, miny, maxx, maxy = box(
        #     *sensors[sensors.gid == 6].total_bounds).buffer(6.0).bounds
        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.35 * 8.26))
        ax.set_title(
            f"Montpellier (34), IRIS Tastavin ({projectionName})", size=28)
        iris.boundary.plot(ax=ax, color="red", linestyle="dotted")
        buildings.plot(ax=ax, color="grey")
        sensors.plot(ax=ax, color="black", marker="P")
        sensors.buffer(size).boundary.plot(
            ax=ax, color="black", linewidth=0.3, linestyle=":")
        pmasks.plot(ax=ax, column="depth", cmap="Spectral",
                    edgecolor="black", alpha=0.75, legend="True")
        # pp.plot(ax=ax, column="depth", cmap="Spectral",
        #         marker="+", legend="True")
        ax.axis("off")
        # ax.axis([minx, maxx, miny, maxy])
        scalebar = ScaleBar(dx=1.0, units="m", length_fraction=None, box_alpha=0.85,
                            width_fraction=0.005, location="lower right", frameon=True)
        ax.add_artist(scalebar)
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return pp, pmasks


# pp, pmasks = DoubleProjectionOfWallsLib.test("/tmp/DoubleProjectionOfWallsLib.gpkg")
