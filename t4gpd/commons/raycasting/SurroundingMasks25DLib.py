'''
Created on 22 aug. 2024

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
from geopandas import GeoDataFrame
from shapely import MultiLineString, Point, get_coordinates, get_parts
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.SphericalCartesianCoordinates import SphericalCartesianCoordinates
from t4gpd.commons.raycasting.PrepareMasksLib import PrepareMasksLib


class SurroundingMasks25DLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def __c2s(viewpoint, mask):
        a, b = get_coordinates(mask, include_z=True)
        ar, alon, alat = SphericalCartesianCoordinates.fromCartesianToSphericalCoordinates(
            a[0] - viewpoint.x, a[1] - viewpoint.y, a[2] - viewpoint.z)
        br, blon, blat = SphericalCartesianCoordinates.fromCartesianToSphericalCoordinates(
            b[0] - viewpoint.x, b[1] - viewpoint.y, b[2] - viewpoint.z)
        assert (alat >= 0), "'alat' must be positive or zero"
        assert (blat >= 0), "'blat' must be positive or zero"
        alon, alat = AngleLib.toDegrees(
            alon), AngleLib.toDegrees(alat)  # DEBUG
        blon, blat = AngleLib.toDegrees(
            blon), AngleLib.toDegrees(blat)  # DEBUG
        # print(f"{alon=:.1f} --- {blon=:.1f}")  # DEBUG
        return ar, alon, alat, br, blon, blat

    @staticmethod
    def __isHiddenBy(viewpoint, curr, other):
        # Returns True if "other" is hidden by "curr" when observing from "viewpoint"
        cr1, clon1, clat1 = curr["__r1__"], curr["__lon1__"], curr["__lat1__"]
        cr2, clon2, clat2 = curr["__r2__"], curr["__lon2__"], curr["__lat2__"]
        or1, olon1, olat1 = other["__r1__"], other["__lon1__"], other["__lat1__"]
        or2, olon2, olat2 = other["__r2__"], other["__lon2__"], other["__lat2__"]

        return ((clon1 >= olon1 >= olon2 >= clon2) and
                (min(clat1, clat2) >= max(olat1, olat2)) and
                (max(cr1, cr2) < min(or1, or2)))

    @ staticmethod
    def removeHidden25DMasks(vp_and_masks):
        if not isinstance(vp_and_masks, GeoDataFrame):
            raise IllegalArgumentTypeException(vp_and_masks, "GeoDataFrame")
        vp_and_masks2 = vp_and_masks.explode(ignore_index=True)

        vp_and_masks2 = vp_and_masks2.to_dict(orient="index")
        for key in vp_and_masks2.keys():
            viewpoint = vp_and_masks2[key]["__VIEWPOINT_GEOM__"]
            mask = vp_and_masks2[key]["geometry"]
            tmp = SurroundingMasks25DLib.__c2s(viewpoint, mask)
            vp_and_masks2[key]["__r1__"] = tmp[0]
            vp_and_masks2[key]["__lon1__"] = tmp[1]
            vp_and_masks2[key]["__lat1__"] = tmp[2]
            vp_and_masks2[key]["__r2__"] = tmp[3]
            vp_and_masks2[key]["__lon2__"] = tmp[4]
            vp_and_masks2[key]["__lat2__"] = tmp[5]

        before = len(vp_and_masks2)  # DEBUG

        # Remove completely hidden edges (phase 1)
        hiddenEdgeIds = set()
        for i, curr in vp_and_masks2.items():
            if (not i in hiddenEdgeIds):
                for j, other in vp_and_masks2.items():
                    if (not j in hiddenEdgeIds) and (i != j):
                        if SurroundingMasks25DLib.__isHiddenBy(viewpoint, curr, other):
                            hiddenEdgeIds.add(j)

        for i in sorted(hiddenEdgeIds, reverse=True):
            del (vp_and_masks2[i])
        print(f"{before} --> {len(vp_and_masks2)}")  # DEBUG

        vp_and_masks2 = GeoDataFrame(
            vp_and_masks2.values(), crs=vp_and_masks.crs)
        vp_and_masks2.drop(columns=["__r1__", "__lon1__", "__lat1__",
                                    "__r2__", "__lon2__", "__lat2__"],
                           inplace=True)
        return vp_and_masks2

    @ staticmethod
    def test(ofile=None):
        import matplotlib.pyplot as plt
        from matplotlib_scalebar.scalebar import ScaleBar
        from shapely import box
        from shapely.wkt import loads
        from t4gpd.demos.GeoDataFrameDemosC import GeoDataFrameDemosC

        buildings = GeoDataFrameDemosC.irisTastavinBuildings()
        viewpoints = GeoDataFrame([{
            "gid": 123,
            "geometry": loads("Point (770402.89999999979045242 6277956.6500000013038516 0)")
        }], crs=buildings.crs)

        vp_and_masks1 = PrepareMasksLib.removeNonVisible25DMasks(
            viewpoints, buildings, "HAUTEUR", horizon=100.0, h0=0.0,
            encode=True
        )
        vp_and_masks1.__VIEWPOINT_GEOM__ = vp_and_masks1.__VIEWPOINT_GEOM__.apply(
            lambda v: loads(v))
        vp_and_masks2 = SurroundingMasks25DLib.removeHidden25DMasks(
            vp_and_masks1)

        # MAPPING
        minx, miny, maxx, maxy = box(
            *viewpoints.total_bounds).buffer(30.0).bounds
        minx, miny, maxx, maxy = vp_and_masks1.total_bounds

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.35 * 8.26))
        viewpoints.plot(ax=ax, color="green", marker="P")
        buildings.plot(ax=ax, color="lightgrey")
        vp_and_masks1.plot(ax=ax, color="red", linewidth=5)
        vp_and_masks2.plot(ax=ax, color="blue", linewidth=2)
        ax.axis("off")
        ax.axis([minx, maxx, miny, maxy])
        scalebar = ScaleBar(dx=1.0, units="m", length_fraction=None, box_alpha=0.85,
                            width_fraction=0.005, location="lower right", frameon=True)
        ax.add_artist(scalebar)
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        if not ofile is None:
            buildings.to_file(ofile, layer="buildings")
            viewpoints.to_file(ofile, layer="viewpoints")
            vp_and_masks1.to_file(ofile, layer="vp_and_masks1")
            vp_and_masks2.to_file(ofile, layer="vp_and_masks2")

        return vp_and_masks1, vp_and_masks2


# vp_and_masks1, vp_and_masks2 = SurroundingMasks25DLib.test("/tmp/SurroundingMasks25DLib.gpkg")
