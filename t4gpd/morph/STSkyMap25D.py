'''
Created on 24 jul. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from numpy import arctan2, asarray, cos, linspace, pi, sin
from shapely import Polygon
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCasting4Lib import RayCasting4Lib


class STSkyMap25D(GeoProcess):
    '''
    classdocs
    '''
    PIDIV2 = 0.5 * pi

    def __init__(self, buildings, viewpoints, nRays=64, rayLength=100.0,
                 elevationFieldname="HAUTEUR", h0=0.0, size=4.0, epsilon=1e-2,
                 projectionName="Stereographic", withIndices=False, withAngles=False,
                 encode=False):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(
                buildings, "buildings GeoDataFrame")
        if not elevationFieldname in buildings:
            raise Exception(
                f"{elevationFieldname} is not a relevant field name!")
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(
                viewpoints, "viewpoints GeoDataFrame")

        if not GeoDataFrameLib.shareTheSameCrs(buildings, viewpoints):
            raise Exception(
                "Illegal argument: buildings and viewpoints must share shames CRS!")

        self.buildings = buildings
        self.elevationFieldname = elevationFieldname
        # CLEAN GEOMETRIES
        self.buildings.geometry = self.buildings.geometry.apply(
            lambda g: g.buffer(0))
        self.buildings.geometry = self.buildings.apply(
            lambda row: row.geometry if row.geometry.has_z else GeomLib.forceZCoordinateToZ0(
                row.geometry, row[self.elevationFieldname]),
            axis=1
        )

        self.nRays = nRays
        self.rayLength = rayLength
        self.rays = RayCasting4Lib.get25DPanopticRaysGeoDataFrame(
            viewpoints, rayLength, nRays, h0)

        self.size = size
        self.epsilon = epsilon
        if not projectionName in ["Stereographic"]:
            raise IllegalArgumentTypeException(
                projectionName, "spherical projection as 'Stereographic'")
        self.proj = self.__stereographic

        self.withIndices = withIndices
        self.withAngles = withAngles
        self.encode = encode

    def __stereographic(self, lat, lon):
        radius = (self.size * cos(lat)) / (1.0 + sin(lat))
        return (radius * cos(lon), radius * sin(lon))

    def __angles(self, heights, widths, ray_ids):
        lats = [arctan2(h, w) for h, w in zip(heights, widths)]
        if (self.nRays != len(ray_ids)):
            ray_ids = {ray_id: lats[i] for i, ray_id in enumerate(ray_ids)}
            lats = [
                ray_ids[i] if i in ray_ids else self.PIDIV2 for i in range(self.nRays)]
        return lats

    def __buildSkyMap(self, viewpoint, lats, lons):
        viewpoint = viewpoint.centroid
        pnodes = [self.proj(lats[i], lons[i])
                  for i in range(len(lats))]
        pnodes = [(viewpoint.x + pnode[0], viewpoint.y + pnode[1])
                  for pnode in pnodes]
        return Polygon(viewpoint.buffer(self.size + self.epsilon).exterior.coords, [pnodes])

    def run(self):
        smapRaysField = RayCasting4Lib.multipleRayCast25D(
            self.buildings, self.rays, self.nRays, self.rayLength, self.elevationFieldname, self.withIndices, h0=0.0)

        if (0 < len(smapRaysField)):
            lons = linspace(0, 2*pi, self.nRays, endpoint=False)
            smapRaysField["angles"] = smapRaysField.apply(
                lambda row: self.__angles(
                    row.__RAY_DELTA_ALT__, row.__RAY_LEN__, row.__RAY_ID__),
                axis=1
            )
            smapRaysField.geometry = smapRaysField.apply(lambda row: self.__buildSkyMap(
                row.viewpoint, row.angles, lons), axis=1)
            smapRaysField.angles = smapRaysField.angles.apply(
                lambda v: (asarray(v) * 180)/pi)

        fields = ["__RAY_ID__"]
        for field in ["__RAY_LEN__", "__RAY_ALT__", "__RAY_DELTA_ALT__"]:
            if field in smapRaysField.columns:
                fields.append(field)

        if not self.withAngles:
            fields += ["angles"]

        smapRaysField.drop(columns=fields, inplace=True)

        if self.encode:
            smapRaysField.viewpoint = smapRaysField.viewpoint.apply(
                lambda vp: vp.wkt)
            if "angles" in smapRaysField:
                smapRaysField.angles = smapRaysField.angles.apply(
                    lambda a: ArrayCoding.encode(a))

        return smapRaysField


"""
import matplotlib.pyplot as plt
from shapely import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
pts = [ Point((355119.8, 6689339.2)), Point((355143.0, 6689359.4)),
	Point((355113.4, 6689397.9)) ]
sensors = GeoDataFrame([{"gid": i, "geometry": p} for i, p in enumerate(pts)],
	crs=buildings.crs)
# sensors.geometry = sensors.geometry.apply(lambda g: g.buffer(5))

skymaps = STSkyMap25D(buildings, sensors, withIndices=True).run()

print(skymaps)
fig, ax = plt.subplots(figsize=(8.26, 8.26))
buildings.plot(ax=ax, color="grey")
sensors.plot(ax=ax, color="red")
skymaps.plot(ax=ax, color="blue")
plt.show()
"""
