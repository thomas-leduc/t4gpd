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
from shapely import Point
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from numpy import arctan2, asarray, cos, linspace, pi, sin
from shapely import Polygon
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCasting4Lib import RayCasting4Lib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.morph.STPointsDensifier import STPointsDensifier


class STSkyMap25D(GeoProcess):
    '''
    classdocs
    '''
    PIDIV2 = 0.5 * pi

    def __init__(self, buildings, viewpoints, nRays=64, rayLength=100.0,
                 elevationFieldname="HAUTEUR", h0=0.0, size=4.0, epsilon=1e-2,
                 projectionName="Stereographic", withIndices=False):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(
                buildings, "buildings GeoDataFrame")
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(
                viewpoints, "viewpoints GeoDataFrame")

        if not GeoDataFrameLib.shareTheSameCrs(buildings, viewpoints):
            raise Exception(
                "Illegal argument: buildings and viewpoints must share shames CRS!")

        self.buildings = buildings
        # CLEAN GEOMETRIES
        self.buildings.geometry = self.buildings.geometry.apply(
            lambda g: g.buffer(0))

        self.nRays = nRays
        self.rays = RayCasting4Lib.get25DPanopticRaysGeoDataFrame(
            viewpoints, rayLength, nRays, h0)

        self.elevationFieldname = elevationFieldname
        self.size = size
        self.epsilon = epsilon
        if not projectionName in ["Stereographic"]:
            raise IllegalArgumentTypeException(
                projectionName, "spherical projection as 'Stereographic'")
        self.proj = self.__stereographic

        self.withIndices = withIndices

    def __stereographic(self, lat, lon):
        radius = (self.size * cos(lat)) / (1.0 + sin(lat))
        return (radius * cos(lon), radius * sin(lon))

    def __buildSkyMap(self, viewpoint, heights, widths, ray_ids, lons):
        lats = [arctan2(h, w) for h, w in zip(heights, widths)]
        if (self.nRays != len(ray_ids)):
            ray_ids = {ray_id: lats[i] for i, ray_id in enumerate(ray_ids)}
            lats = [
                ray_ids[i] if i in ray_ids else self.PIDIV2 for i in range(self.nRays)]

        pnodes = [self.proj(lats[i], lons[i])
                  for i in range(len(lats))]
        pnodes = [(viewpoint.x + pnode[0], viewpoint.y + pnode[1])
                  for pnode in pnodes]
        return Polygon(viewpoint.buffer(self.size + self.epsilon).exterior.coords, [pnodes])

    def run(self):
        smapRaysField = RayCasting4Lib.multipleRayCast25D(
            self.buildings, self.rays, self.elevationFieldname, h0=0.0)

        if self.withIndices:
            smapRaysField = RayCasting4Lib.addIndicesToIsovRaysField25D(
                smapRaysField)

        smapRaysField["__RAY_LEN__"] = smapRaysField.geometry.apply(
            lambda geom: asarray([ray.length for ray in geom.geoms]))
        smapRaysField["__RAY_DELTA_ALT__"] = smapRaysField.geometry.apply(
            lambda geom: asarray([max(ray.coords[-1][2]-ray.coords[0][2], 0) for ray in geom.geoms]))

        if (0 < len(smapRaysField)):
            lons = linspace(0, 2*pi, self.nRays, endpoint=False)
            smapRaysField.geometry = smapRaysField.apply(lambda row: self.__buildSkyMap(
                row.viewpoint, row.__RAY_DELTA_ALT__, row.__RAY_LEN__, row.__RAY_ID__, lons), axis=1)

        smapRaysField.drop(
            columns=["__RAY_LEN__", "__RAY_DELTA_ALT__"], inplace=True)

        return smapRaysField


"""
buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
paths = GeoDataFrameDemos.districtRoyaleInNantesPaths()
paths = paths.loc[paths[paths.gid == 1].index]
sensors = STPointsDensifier(paths, distance=10.0, pathidFieldname=None,
                            adjustableDist=True, removeDuplicate=True).run()
sensors.reset_index(names=["id"], inplace=True)
# sensors = sensors[sensors.id == 1]

# sensors = sensors.loc[sensors[sensors.gid.isin([86, 100, 117])].index, [
#     "gid", "geometry"]]

# buildings = GeoDataFrame([{"id": x, "geometry": Polygon(
#     [(-x, x, h), (x, x, h), (x, x+1, h), (-x, x+1, h)]), "H": h} for x, h in [(4, 4), (8, 8.1), (12, 12.1)]])
# sensors = GeoDataFrame([
#     {"gid": y, "geometry": Point([0, y, 0])} for y in [0, 10, 15]
# ])

nRays, rayLength = 64, 100.0
smapRaysField = STSkyMap25D(buildings, sensors, nRays, rayLength, elevationFieldname="HAUTEUR",
                            size=4.0, epsilon=1e-1, projectionName="Stereographic", withIndices=True).run()

_, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
buildings.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.3)
sensors.plot(ax=ax, color="red", marker="+")
sensors.apply(lambda x: ax.annotate(
    text=x["id"], xy=x.geometry.coords[0][0:2],
    color="red", size=12, ha="left", va="top"), axis=1)
smapRaysField.plot(ax=ax, column="svf", legend=True, cmap="viridis")
plt.axis("off")
plt.tight_layout()
plt.show()
"""
