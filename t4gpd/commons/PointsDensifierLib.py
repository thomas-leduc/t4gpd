"""
Created on 20 avr. 2021

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

from geopandas import GeoDataFrame
from numpy import (
    arange,
    asarray,
    column_stack,
    concatenate,
    cumsum,
    linspace,
    searchsorted,
    sqrt,
    vstack,
    zeros_like,
)
from numpy.linalg import norm
from shapely import (
    Geometry,
    LineString,
    MultiLineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
    get_coordinates,
    line_interpolate_point,
    multipoints,
)
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PointsDensifierLib(object):
    """
    classdocs
    """

    @staticmethod
    def __densifyByCount(line, npts, blockid, contourid, distToTheSubstrate=None):
        distance = line.length / (npts - 1)
        return PointsDensifierLib.__densifyByDistance(
            line, distance, blockid, contourid, distToTheSubstrate
        )

    @staticmethod
    def __densifyByDistance(
        line, distance, blockid, contourid, adjustableDist=True, distToTheSubstrate=None
    ):
        if not isinstance(line, LineString):
            raise IllegalArgumentTypeException(line, "LineString")

        if adjustableDist:
            _d = line.length
            if _d > distance:
                distance = _d / round(_d / distance)

        listOfCoords = line.coords

        result, nodeid, remainingDist = list(), 0, 0.0
        for i in range(1, len(listOfCoords)):
            a, b = listOfCoords[i - 1], listOfCoords[i]
            speedv = [b[0] - a[0], b[1] - a[1]]
            norm = sqrt(speedv[0] * speedv[0] + speedv[1] * speedv[1])
            if 0.0 < norm:
                speedv = [speedv[0] / norm, speedv[1] / norm]
                normalv = [speedv[1], -speedv[0], 0]

                k = remainingDist
                while k <= norm:
                    samplePoint = Point([a[0] + k * speedv[0], a[1] + k * speedv[1]])

                    if distToTheSubstrate is not None:
                        samplePoint = Point(
                            [
                                samplePoint.x + distToTheSubstrate * normalv[0],
                                samplePoint.y + distToTheSubstrate * normalv[1],
                            ]
                        )

                    result.append(
                        {
                            "node_id": ArrayCoding.encode([blockid, contourid, nodeid]),
                            "motion_dir": ArrayCoding.encode(speedv),
                            "normal_vec": ArrayCoding.encode(normalv),
                            "geometry": samplePoint,
                        }
                    )
                    k += distance
                    nodeid += 1

                remainingDist = k - norm
        return result

    @staticmethod
    def __densifyByCurvilinearAbscissa(
        line, curvAbsc, blockid, contourid, distToTheSubstrate=None
    ):
        if not isinstance(line, LineString):
            raise IllegalArgumentTypeException(line, "LineString")

        listOfCoords = line.coords
        result, nodeid = list(), 0
        for i in range(1, len(listOfCoords)):
            a, b = listOfCoords[i - 1], listOfCoords[i]
            speedv = [b[0] - a[0], b[1] - a[1]]
            norm = sqrt(speedv[0] * speedv[0] + speedv[1] * speedv[1])
            if 0.0 < norm:
                speedv = [speedv[0] / norm, speedv[1] / norm]
                normalv = [speedv[1], -speedv[0], 0]

                ls = LineString([a, b])
                for _curvAbsc in curvAbsc:
                    samplePoint = ls.interpolate(_curvAbsc, normalized=True)

                    if distToTheSubstrate is not None:
                        samplePoint = Point(
                            [
                                samplePoint.x + distToTheSubstrate * normalv[0],
                                samplePoint.y + distToTheSubstrate * normalv[1],
                            ]
                        )

                    result.append(
                        {
                            "node_id": ArrayCoding.encode([blockid, contourid, nodeid]),
                            "motion_dir": ArrayCoding.encode(speedv),
                            "normal_vec": ArrayCoding.encode(normalv),
                            "geometry": samplePoint,
                        }
                    )
                    nodeid += 1

        return result

    @staticmethod
    def densifyByCount(geom, npts, blockid, contourid=0, distToTheSubstrate=None):
        if isinstance(geom, LineString):
            result = PointsDensifierLib.__densifyByCount(
                geom, npts, blockid, contourid, distToTheSubstrate
            )

        elif isinstance(geom, Polygon):
            result = PointsDensifierLib.__densifyByCount(
                geom.exterior, npts, blockid, contourid, distToTheSubstrate
            )
            for g in geom.interiors:
                contourid += 1
                result += PointsDensifierLib.__densifyByCount(
                    g, npts, blockid, contourid, distToTheSubstrate
                )

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                result += PointsDensifierLib.__densifyByCount(
                    g, npts, blockid, contourid, distToTheSubstrate
                )
                contourid += 1

        else:
            result = []

        return result

    @staticmethod
    def densifyByDistance(
        geom,
        distance,
        blockid,
        contourid=0,
        adjustableDist=True,
        distToTheSubstrate=None,
    ):
        if isinstance(geom, LineString):
            result = PointsDensifierLib.__densifyByDistance(
                geom, distance, blockid, contourid, adjustableDist, distToTheSubstrate
            )

        elif isinstance(geom, Polygon):
            result = PointsDensifierLib.__densifyByDistance(
                geom.exterior,
                distance,
                blockid,
                contourid,
                adjustableDist,
                distToTheSubstrate,
            )
            for g in geom.interiors:
                contourid += 1
                result += PointsDensifierLib.__densifyByDistance(
                    g, distance, blockid, contourid, adjustableDist, distToTheSubstrate
                )

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                result += PointsDensifierLib.densifyByDistance(
                    g, distance, blockid, contourid, adjustableDist, distToTheSubstrate
                )
                contourid += 1

        else:
            result = []

        return result

    @staticmethod
    def densifyByCurvilinearAbscissa(
        geom, curvAbsc, blockid, contourid=0, distToTheSubstrate=None
    ):
        if isinstance(geom, LineString):
            result = PointsDensifierLib.__densifyByCurvilinearAbscissa(
                geom, curvAbsc, blockid, contourid, distToTheSubstrate
            )

        elif isinstance(geom, Polygon):
            result = PointsDensifierLib.__densifyByCurvilinearAbscissa(
                geom.exterior, curvAbsc, blockid, contourid, distToTheSubstrate
            )
            for g in geom.interiors:
                contourid += 1
                result += PointsDensifierLib.__densifyByCurvilinearAbscissa(
                    g, curvAbsc, blockid, contourid, distToTheSubstrate
                )

        elif isinstance(geom, MultiLineString) or isinstance(geom, MultiPolygon):
            result = list()
            for g in geom.geoms:
                result += PointsDensifierLib.densifyByCurvilinearAbscissa(
                    g, curvAbsc, blockid, contourid, distToTheSubstrate
                )
                contourid += 1

        else:
            result = []

        return result

    @staticmethod
    def __densify_linestring_aux(
        geom: LineString, distance: float, adjustableDist: bool
    ) -> MultiPoint:
        npts = round(geom.length / distance) + 1
        if adjustableDist:
            endpoint = True
            if geom.is_closed:
                npts -= 1
                endpoint = False
            curv_absc = linspace(0, 1, num=npts, endpoint=endpoint)
            # print(geom.length, linspace(0, geom.length, num=npts, endpoint=endpoint))

        else:
            curv_absc = arange(0, geom.length, step=distance) / geom.length
            # print(geom.length, arange(0, geom.length, step=distance))

        return multipoints(
            line_interpolate_point(
                geom,
                curv_absc,
                normalized=True,
            )
        )

    @staticmethod
    def _linestring_preprocessing(geom: LineString) -> list:
        coords = asarray(geom.coords)
        motion_dir = coords[1:] - coords[:-1]
        seg_lengths = norm(motion_dir, ord=2, axis=1)
        acc_lengths = concatenate(([0.0], cumsum(seg_lengths)))

        unit_motion_dir = zeros_like(motion_dir)
        mask = seg_lengths > 0
        unit_motion_dir[mask] = motion_dir[mask] / seg_lengths[mask, None]
        unit_motion_dir = vstack((unit_motion_dir, unit_motion_dir[-1]))

        normal_vec = column_stack((unit_motion_dir[:, 1], -unit_motion_dir[:, 0]))
        return acc_lengths, unit_motion_dir, normal_vec

    @staticmethod
    def _densify_linestring(
        geom: LineString,
        distance: float,
        adjustableDist: bool,
        distToTheSubstrate: float,
    ) -> MultiPoint:

        if distToTheSubstrate is None:
            return PointsDensifierLib.__densify_linestring_aux(
                geom, distance, adjustableDist
            )

        acc_lengths, motion_dir, normal_vec = (
            PointsDensifierLib._linestring_preprocessing(geom)
        )

        npts = round(geom.length / distance) + 1
        if adjustableDist:
            endpoint = True
            if geom.is_closed:
                npts -= 1
                endpoint = False
            curv_absc = linspace(0, geom.length, num=npts, endpoint=endpoint)
            curv_absc_unit = linspace(0, 1, num=npts, endpoint=endpoint)

        else:
            curv_absc = arange(0, geom.length, step=distance)
            curv_absc_unit = curv_absc / geom.length

        indices = searchsorted(acc_lengths, curv_absc, side="right") - 1

        ppts = line_interpolate_point(
            geom,
            curv_absc_unit,
            normalized=True,
        )

        pts = [
            [
                ppt.x + distToTheSubstrate * normal_vec[idx, 0],
                ppt.y + distToTheSubstrate * normal_vec[idx, 1],
            ]
            for ppt, idx in zip(ppts, indices)
        ]
        return multipoints(pts)

    @staticmethod
    def densify_geometry(
        geom: Geometry,
        distance: float,
        adjustableDist: bool = True,
        distToTheSubstrate: float = None,
    ) -> MultiPoint:
        if geom.is_empty:
            return MultiPoint()
        
        if isinstance(geom, LineString):
            return PointsDensifierLib._densify_linestring(
                geom, distance, adjustableDist, distToTheSubstrate
            )
        elif isinstance(geom, Polygon):
            result = vstack(
                [
                    get_coordinates(
                        PointsDensifierLib._densify_linestring(
                            geom.exterior,
                            distance,
                            adjustableDist,
                            distToTheSubstrate,
                        )
                    )
                ]
                + [
                    get_coordinates(
                        PointsDensifierLib._densify_linestring(
                            g, distance, adjustableDist, distToTheSubstrate
                        )
                    )
                    for g in geom.interiors
                ]
            )
            return multipoints(result)
        elif isinstance(geom, (MultiLineString, MultiPolygon)):
            return multipoints(
                vstack(
                    [
                        get_coordinates(
                            PointsDensifierLib.densify_geometry(
                                g, distance, adjustableDist, distToTheSubstrate
                            )
                        )
                        for g in geom.geoms
                    ]
                )
            )
        else:
            raise IllegalArgumentTypeException(
                geom, "[Multi]LineString or [Multi]Polygon"
            )

    @staticmethod
    def densify(
        gdf: GeoDataFrame,
        distance: float,
        adjustableDist: bool = True,
        distToTheSubstrate: float = None,
        copy: bool = True,
    ) -> GeoDataFrame:
        if copy:
            gdf = gdf.copy(deep=True)

        gdf["geometry"] = gdf["geometry"].apply(
            lambda geom: PointsDensifierLib.densify_geometry(
                geom, distance, adjustableDist, distToTheSubstrate
            )
        )

        return gdf

    @staticmethod
    def test(distToTheSubstrate=None):
        from matplotlib import pyplot as plt
        from shapely import GeometryCollection, box

        path = GeoDataFrame(
            {
                "geometry": [
                    LineString([(0, 0), (10, 0), (10, 10)]),
                    box(2, 2, 7, 7).difference(box(3, 3, 6, 6)),
                    MultiLineString(
                        [
                            LineString([(20, 0), (30, 0), (30, 10)]),
                            LineString([(20, 20), (30, 20), (30, 30)]),
                        ]
                    ),
                    MultiPolygon([
                        box(0, 20, 4, 30).difference(box(2, 22, 3, 28)),
                        box(5, 20, 10, 30).difference(box(7, 22, 8, 28)),
                    ]),
                    MultiPoint(),
                    MultiLineString(),
                    MultiPolygon(),
                    GeometryCollection(),
                ]
            },
            crs="epsg:2154",
        )
        sensors = PointsDensifierLib.densify(
            path, 3.0, adjustableDist=True, distToTheSubstrate=distToTheSubstrate
        )
        fig, ax = plt.subplots(figsize=(10, 10))
        path.plot(ax=ax)
        sensors.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return sensors


# sensors = PointsDensifierLib.test(distToTheSubstrate=None)
# sensors = PointsDensifierLib.test(distToTheSubstrate=0.25)
