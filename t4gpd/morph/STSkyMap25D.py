'''
Created on 24 jul. 2023

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
from numpy import arctan2, asarray, cos, full, linspace, pi, sqrt, sin
from shapely import Polygon
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.raycasting.RayCasting25DLib import RayCasting25DLib


class STSkyMap25D(GeoProcess):
    '''
    classdocs
    '''
    PIDIV2 = 0.5 * pi

    def __init__(self, buildings, viewpoints, nRays=64, rayLength=100.0,
                 elevationFieldname="HAUTEUR", h0=0.0, size=4.0, epsilon=1e-2,
                 projectionName="Stereographic", withIndices=False, withAngles=False,
                 encode=False, threshold=1e-6):
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
        if not "gid" in viewpoints:
            raise Exception(
                "viewpoints must have a 'gid' field name (with unique values)!")

        if not GeoDataFrameLib.shareTheSameCrs(buildings, viewpoints):
            raise Exception(
                "Illegal argument: buildings and viewpoints must share shames CRS!")

        self.viewpoints = viewpoints
        self.viewpoints.geometry = self.viewpoints.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(
                geom, z0=GeomLib3D.centroid(geom).z if geom.has_z else h0))

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
        self.rays = RayCasting25DLib.get25DPanopticRaysGeoDataFrame(
            self.viewpoints, rayLength, nRays, h0)

        self.size = size
        self.epsilon = epsilon
        if not projectionName in ["Isoaire", "Orthogonal", "Stereographic"]:
            raise IllegalArgumentTypeException(
                projectionName, "spherical projection as 'Stereographic', 'Orthogonal', 'Isoaire'")
        if ("Isoaire" == projectionName):
            self.proj = self.__isoaire
        elif ("Orthogonal" == projectionName):
            self.proj = self.__orthogonal
        elif ("Stereographic" == projectionName):
            self.proj = self.__stereographic

        self.withIndices = withIndices
        self.withAngles = withAngles
        self.encode = encode
        self.threshold = threshold

    def __isoaire(self, lat, lon):
        radius = sqrt((1 - sin(lat)) / ((cos(lat)*cos(lon))
                      ** 2 + (cos(lat)*sin(lon))**2))
        radius *= (self.size * cos(lat))
        return (radius * cos(lon), radius * sin(lon))

    def __orthogonal(self, lat, lon):
        radius = (self.size * cos(lat))
        return (radius * cos(lon), radius * sin(lon))

    def __stereographic(self, lat, lon):
        radius = 1.0 / (1.0 + sin(lat))
        radius *= (self.size * cos(lat))
        return (radius * cos(lon), radius * sin(lon))

    def __angles(self, heights, widths):
        return [arctan2(h, w) for h, w in zip(heights, widths)]

    def __buildSkyMap(self, viewpoint, lats, lons):
        viewpoint = viewpoint.centroid
        pnodes = [self.proj(lat, lon) for lat, lon in zip(lats, lons)]
        pnodes = [(viewpoint.x + pp[0], viewpoint.y + pp[1]) for pp in pnodes]
        return Polygon(viewpoint.buffer(self.size + self.epsilon).exterior.coords, [pnodes])

    def run(self):
        smapRaysField = RayCasting25DLib.multipleRayCast25D(
            self.viewpoints, self.buildings, self.rays, self.nRays, self.rayLength,
            self.elevationFieldname, self.withIndices, h0=0.0, threshold=self.threshold)
        # smapRaysField.to_csv("/tmp/7.csv") # DEBUG

        if (0 < len(smapRaysField)):
            smapRaysField["angles"] = smapRaysField.apply(
                lambda row: self.__angles(
                    row.__RAY_DELTA_ALT__, row.__RAY_LEN__),
                axis=1
            )
            # smapRaysField.to_csv("/tmp/8.csv") # DEBUG
            lons = linspace(0, 2*pi, self.nRays, endpoint=False)
            smapRaysField.geometry = smapRaysField.apply(lambda row: self.__buildSkyMap(
                row.viewpoint, row.angles, lons), axis=1)
            smapRaysField.angles = smapRaysField.angles.apply(
                lambda v: (180/pi) * asarray(v))
            # smapRaysField.to_csv("/tmp/9.csv") # DEBUG

        fields = ["__RAY_ID__"]
        for field in ["__RAY_LEN__", "__RAY_ALT__", "__RAY_DELTA_ALT__", "__HAUTEUR_VP__"]:
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

projectionName = "Stereographic"
projectionName = "Isoaire"
# projectionName = "Orthogonal"
skymaps = STSkyMap25D(buildings, sensors, projectionName=projectionName,
                      withIndices=True).run()

print(skymaps)
minx, miny, maxx, maxy = skymaps.total_bounds
fig, ax = plt.subplots(figsize=(8.26, 8.26))
ax.set_title(projectionName, fontsize=20)
buildings.plot(ax=ax, color="grey")
sensors.plot(ax=ax, color="red")
skymaps.plot(ax=ax, color="blue")
ax.axis([minx, maxx, miny, maxy])
ax.axis("off")
fig.tight_layout()
plt.show()
"""

"""
from shapely import Point

h = 10.0
masks = GeoDataFrame([{
    "gid": 1,
    "geometry": Polygon([(0, 0), (0, 10), (10, 10), (10, 9), (1, 9), (1, 0), (0, 0)]),
    "HAUTEUR": h
}])
sensors = GeoDataFrame([
    {"gid": 1, "geometry": Point([1.1, 8.9])},
])
result = STSkyMap25D(masks, sensors,
                     nRays=64, rayLength=100.0,
                     elevationFieldname="HAUTEUR",
                     h0=0.0, size=2.0, epsilon=1e-2,
                     projectionName="Stereographic",
                     withIndices=True,
                     withAngles=False).run()
print(result[['gid', 'viewpoint', 'w_mean', 'w_std', 'h_mean', 'h_over_w',
       'svf']])
"""

"""
from io import StringIO
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.demos.NantesBDT import NantesBDT
from t4gpd.morph.STBBox import STBBox

_sio = StringIO('''gid;geometry
150755;"POLYGON ((355050.15 6689030.25, 355050.15 6689032.25, 355048.15 6689032.25, 355048.15 6689030.25, 355050.15 6689030.25))"
''')
sensors = GeoDataFrameLib.read_csv(_sio)
# buildings = NantesBDT.buildings(STBBox(sensors, 10).run())
buildings = NantesBDT.buildings(STBBox(sensors, 200).run())
buildings = buildings.loc[buildings[buildings.ID.isin(
    ["BATIMENT0000000302927659", "BATIMENT0000000302930463",
     "BATIMENT0000000302930192"])].index]
sensors.to_file("/tmp/sensors.shp")
buildings.to_file("/tmp/buildings.shp")
skymaps = STSkyMap25D(buildings, sensors, nRays=32, rayLength=200,
                      elevationFieldname="HAUTEUR", h0=0.0, size=7.0,
                      withIndices=True, withAngles=True, encode=True,
                      threshold=1e-7).run()
# skymaps.to_file("/tmp/skymaps.shp")
"""

"""
from io import StringIO
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.demos.NantesBDT import NantesBDT

_sio = StringIO('''gid;geometry
86751;"POLYGON ((355042.15 6688780.25, 355042.15 6688782.25, 355040.15 6688782.25, 355040.15 6688780.25, 355042.15 6688780.25))"
''')
sensors = GeoDataFrameLib.read_csv(_sio)
buildings = NantesBDT.buildings()
buildings = buildings.loc[buildings[buildings.ID == "BATIMENT0000000302923050"].index]
sensors.to_file("/tmp/sensors.shp")
buildings.to_file("/tmp/buildings.shp")
skymaps = STSkyMap25D(buildings, sensors, nRays=8, rayLength=200,
                      elevationFieldname="HAUTEUR", h0=0.0, size=7.0,
                      withIndices=True, withAngles=True, encode=True,
                      threshold=1e-7).run()
# skymaps.to_file("/tmp/skymaps.shp")
"""
