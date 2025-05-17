"""
Created on 16 Apr. 2025

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
from numpy import cos, linspace, pi, rad2deg, sin
from pandas import isna
from shapely import LineString, LinearRing, Point, Polygon
from shapely.affinity import rotate, scale, translate
from shapely.ops import substring
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.proj.DoubleProjectionLib import DoubleProjectionLib


class STBodyMaskMap25D(GeoProcess):
    """
    classdocs
    """

    CIRCLE = LinearRing(
        zip(cos(linspace(0, 2 * pi, 90)), sin(linspace(0, 2 * pi, 90)))
    ).normalize()
    DEFAULT_ANGLE_FIELDNAME = "walking_direction"

    def __init__(
        self,
        viewpoints,
        angleFieldname=DEFAULT_ANGLE_FIELDNAME,
        h0=1.18,  # E-SCOOTER: 1.18 m; PEDESTRIAN: 1.15 m
        dist=0.30,  # E-SCOOTER: 0.30 m; PEDESTRIAN: 0.27 m
        shoulder_height=1.57,  # E-SCOOTER: 1.57 m ; PEDESTRIAN: 1.45 m
        shoulder_width=0.45,  # 0.45 m
        neck_head_height=0.25,  # 0.25 m
        size=4.0,
        epsilon=1e-2,
        projectionName="Stereographic",
    ):
        """
        Constructor
        """
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpoints, "viewpoints GeoDataFrame")
        self.viewpoints = viewpoints
        self.angleFieldname = angleFieldname
        proj = DoubleProjectionLib.projection_switch(projectionName)

        self.bodymask, self.cover_ratio = STBodyMaskMap25D._build_initial_body_mask(
            size,
            proj,
            h0,
            dist,
            shoulder_height,
            shoulder_width,
            neck_head_height,
            epsilon=epsilon,
        )

    @staticmethod
    def _build_initial_body_mask(
        size,
        proj,
        h0,
        dist,
        shoulder_height,
        shoulder_width,
        neck_head_height,
        epsilon,
        npts=40,
    ):
        def __project(origin, circle, pts, size, proj):
            pp = [GeomLib.removeZCoordinate(proj(origin, p, size)) for p in pts]
            d0, d1 = circle.project(pp[-1], normalized=True), circle.project(
                pp[0], normalized=True
            )
            partOfCircle = substring(
                circle, start_dist=d0, end_dist=d1, normalized=True
            )
            bodymask = Polygon(pp + list(partOfCircle.coords)[1:-1])
            return bodymask

        # BODY MASK IN CARTESIAN COORDS
        p0 = Point(dist, -0.5 * shoulder_width, h0)
        p1 = Point(dist, p0.y, shoulder_height)
        p2 = Point(dist, -0.5 * (shoulder_width - neck_head_height), p1.z)
        p3 = Point(dist, p2.y, shoulder_height + neck_head_height)
        p4 = Point(dist, -p3.y, p3.z)
        p5 = Point(dist, -p2.y, p2.z)
        p6 = Point(dist, -p1.y, p1.z)
        p7 = Point(dist, -p0.y, p0.z)

        pts = [p0, p1, p2, p3, p3, p4, p5, p6, p7]

        yzlr = LineString([(p.y, p.z) for p in pts])
        # print(xzlr)  # DEBUG
        yzpts = [
            yzlr.interpolate(dist, normalized=True)
            for dist in linspace(0, 1, npts, endpoint=True)
        ]
        pts = [Point(dist, p.x, p.y) for p in yzpts]

        # PROJECT BODY MASK
        origin = Point(0, 0, h0)
        circle = scale(STBodyMaskMap25D.CIRCLE, xfact=size, yfact=size, origin=origin)
        bodymaskIsoArea = __project(
            origin, circle, pts, size, DoubleProjectionLib.isoaire_projection
        )
        cover_ratio = bodymaskIsoArea.area / (pi * size**2)
        bodymask = __project(origin, circle, pts, size, proj)

        if 0 < epsilon:
            return bodymask.union(circle.buffer(epsilon, quad_segs=-1)), cover_ratio
        return bodymask, cover_ratio

    @staticmethod
    def _walking_direction(sensors, angleFieldname):
        def __get_angle(prev, curr, next):
            if isna(prev):
                return AngleLib.normAzimuth(GeomLib.vector_to(curr, next))
            elif isna(next):
                return AngleLib.normAzimuth(GeomLib.vector_to(prev, curr))
            return AngleLib.normAzimuth(GeomLib.vector_to(prev, next))

        sensors = sensors.copy(deep=True)
        sensors["curr_position"] = sensors.geometry.apply(lambda g: g.coords[0])
        sensors["prev_position"] = sensors.curr_position.shift(1)
        sensors["next_position"] = sensors.curr_position.shift(-1)
        sensors[angleFieldname] = sensors.apply(
            lambda row: __get_angle(
                row.prev_position, row.curr_position, row.next_position
            ),
            axis=1,
        )
        sensors[angleFieldname] = rad2deg(sensors[angleFieldname])
        sensors.drop(
            columns=["prev_position", "curr_position", "next_position"], inplace=True
        )
        return sensors

    def run(self):
        if self.angleFieldname is None:
            self.angleFieldname = STBodyMaskMap25D.DEFAULT_ANGLE_FIELDNAME
            bodymasks = STBodyMaskMap25D._walking_direction(
                self.viewpoints, self.angleFieldname
            )
        elif not self.angleFieldname in self.viewpoints:
            bodymasks = STBodyMaskMap25D._walking_direction(
                self.viewpoints, self.angleFieldname
            )
        else:
            bodymasks = self.viewpoints.copy(deep=True)

        bodymasks.geometry = bodymasks.apply(
            lambda row: translate(
                rotate(
                    self.bodymask,
                    angle=180 + row[self.angleFieldname],
                    origin=(0, 0),
                    use_radians=False,
                ),
                xoff=row.geometry.x,
                yoff=row.geometry.y,
            ),
            axis=1,
        )
        bodymasks["body_cover_ratio"] = self.cover_ratio
        return bodymasks

    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos6 import GeoDataFrameDemos6
        from t4gpd.morph.STPointsDensifier import STPointsDensifier

        buildings = GeoDataFrameDemos6.nizanDistrictInNantesBuildings()
        path = GeoDataFrameDemos6.nizanDistrictInNantesPath1()

        sensors = STPointsDensifier(path, distance=15).run()
        sensors = sensors.loc[:, ["geometry"]]
        sensors.insert(0, "gid", range(len(sensors)))

        bodymasks = STBodyMaskMap25D(sensors, size=1, epsilon=1e-2).run()

        # PLOTTING
        minx, miny, maxx, maxy = path.buffer(5).total_bounds

        fig, ax = plt.subplots(figsize=(1.8 * 8.26, 0.6 * 8.26))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="darkgrey")
        path.plot(ax=ax, color="grey", linestyle="-.", linewidth=1)
        bodymasks.plot(ax=ax, color="red")
        sensors.plot(ax=ax, color="red", marker="P")
        ax.axis("off")
        ax.axis([minx, maxx, miny, maxy])
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return bodymasks


# bodymasks = STBodyMaskMap25D.test()
# print(bodymasks)
