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
from t4gpd.commons.DataFrameLib import DataFrameLib
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
        if not DataFrameLib.isAPrimaryKey(viewpoints, "gid"):
            raise Exception(
                "viewpoints must have a 'gid' field name (with unique values)!")

        if not GeoDataFrameLib.shareTheSameCrs(buildings, viewpoints):
            raise Exception(
                "Illegal argument: buildings and viewpoints are expected to share the same crs!")

        self.viewpoints = viewpoints
        self.viewpoints.geometry = self.viewpoints.geometry.apply(
            lambda geom: GeomLib.forceZCoordinateToZ0(
                geom, z0=GeomLib3D.centroid(geom).z if geom.has_z else h0))

        self.buildings = buildings
        self.elevationFieldname = elevationFieldname

        # CHECK IF buildings IS NOT EMPTY
        if (0 < len(self.buildings)):
            # CHECK IF ANY elevationFieldname VALUE IS NULL OR NaN
            if (any(self.buildings[self.elevationFieldname].isna()) or
                    any(self.buildings[self.elevationFieldname].isnull())):
                raise Exception(
                    "There is at least one NaN value in the elevation column of the buildings dataframe!")

            # CLEAN GEOMETRIES
            self.buildings.geometry = self.buildings.geometry.apply(
                lambda g: g.buffer(0))
            self.buildings.geometry = self.buildings.apply(
                lambda row: GeomLib.forceZCoordinateToZ0(
                    row.geometry, row[self.elevationFieldname]),
                axis=1
            )

        self.nRays = nRays
        self.rayLength = rayLength
        self.rays = RayCasting25DLib.get25DPanopticRaysGeoDataFrame(
            self.viewpoints, rayLength, nRays, h0)

        self.size = size
        self.epsilon = epsilon
        projectionName = projectionName.lower()
        if (projectionName in ["equiareal", "isoaire"]):
            self.proj = self.__isoaire
        elif ("orthogonal" == projectionName):
            self.proj = self.__orthogonal
        elif ("polar" == projectionName):
            self.proj = self.__polar
        elif ("stereographic" == projectionName):
            self.proj = self.__stereographic
        else:
            raise IllegalArgumentTypeException(
                projectionName, "spherical projection as 'Stereographic', 'Orthogonal', 'Isoaire', 'Polar'")

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

    def __polar(self, lat, lon):
        radius = (self.size * (pi - 2 * lat)) / pi
        return (radius * cos(lon), radius * sin(lon))

    def __stereographic(self, lat, lon):
        radius = 1.0 / (1.0 + sin(lat))
        radius *= (self.size * cos(lat))
        return (radius * cos(lon), radius * sin(lon))

    def __angles(self, heights, widths):
        return [arctan2(h, w) for h, w in zip(heights, widths)]

    def __buildSkyMap(self, viewpoint, lats, lons):
        try:
            viewpoint = viewpoint.centroid
            pnodes = [self.proj(lat, lon) for lat, lon in zip(lats, lons)]
            pnodes = [(viewpoint.x + pp[0], viewpoint.y + pp[1]) for pp in pnodes]
            return Polygon(viewpoint.buffer(self.size + self.epsilon).exterior.coords, [pnodes])
        except Exception as e:
            print(f"__buildSkyMap: {e}")
            return Polygon()

    def run(self):
        smapRaysField = RayCasting25DLib.multipleRayCast25D(
            self.viewpoints, self.buildings, self.rays, self.nRays,
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

buildings = GeoDataFrameDemos.regularGridOfPlots(2, 2, dw=5.0)
buildings["HAUTEUR"] = 5.0
sensors = GeoDataFrame([{"gid": 1, "geometry": Point([0, 0])}],
                       crs=buildings.crs)

fig, axes = plt.subplots(ncols=2, nrows=2, figsize=(1.2 * 8.26, 1.2 * 8.26))

for i, projection in enumerate(["Stereographic", "Isoaire", "Orthogonal", "Polar"]):
    skymaps = STSkyMap25D(buildings, sensors, projectionName=projection,
                          withIndices=True).run()
    ax = axes[i//2, i%2]

    minx, miny, maxx, maxy = skymaps.total_bounds
    ax.set_title(projection, fontsize=20)
    buildings.plot(ax=ax, color="grey")
    sensors.plot(ax=ax, color="red")
    skymaps.plot(ax=ax, color="blue")
    # ax.axis([minx, maxx, miny, maxy])
    ax.axis("off")

fig.tight_layout()
plt.savefig("prj.pdf", bbox_inches="tight")
plt.show()
"""

"""
import matplotlib.pyplot as plt
from shapely import Point
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

buildings = GeoDataFrameDemos.districtRoyaleInNantesBuildings()
buildings.fillna({"HAUTEUR": 3.33}, inplace=True)

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

'''
from io import StringIO

_sio = StringIO("""gid,row,column,dist_to_ctr,dalle_id,geometry
0,0,0,44.89237128934325,488,"POLYGON ((354596.15 6688442.25, 354596.15 6688444.25, 354594.15 6688444.25, 354594.15 6688442.25, 354596.15 6688442.25))"
""")
sensors = GeoDataFrameLib.read_csv(_sio, sep=",")

_sio = StringIO("""ID,NATURE,USAGE1,USAGE2,LEGER,ETAT,DATE_CREAT,DATE_MAJ,DATE_APP,DATE_CONF,SOURCE,ID_SOURCE,ACQU_PLANI,PREC_PLANI,ACQU_ALTI,PREC_ALTI,NB_LOGTS,NB_ETAGES,MAT_MURS,MAT_TOITS,HAUTEUR,Z_MIN_SOL,Z_MIN_TOIT,Z_MAX_TOIT,Z_MAX_SOL,ORIGIN_BAT,APP_FF,geometry
BATIMENT0000000302923133,Indifférenciée,Indifférencié,,Non,En service,2012-06-19 18:43:00,2018-09-18 13:36:26,,,,,BDParcellaire recalée,3.0,Corrélation,1.0,,,,,6.2,6.0,12.2,16.0,6.2,Cadastre,,"POLYGON Z ((354657.1 6688439.9 12.2, 354664.3 6688441.8 12.2, 354668.8 6688424 12.2, 354661.7 6688422.2 12.2, 354657.1 6688439.9 12.2))"
BATIMENT0000000302923132,"Industriel, agricole ou commercial",Commercial et services,,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,2011-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,0.0,1.0,,,13.4,6.0,19.5,24.2,6.5,Cadastre,C 0.4,"POLYGON Z ((354685.5 6688242.4 19.5, 354678.8 6688271.8 19.5, 354645 6688417.2 19.5, 354691.9 6688429.2 19.5, 354695.3 6688414.5 19.5, 354701.4 6688415.9 19.5, 354702.9 6688409.7 19.5, 354704.3 6688410 19.5, 354705.9 6688403.4 19.5, 354707.6 6688403.8 19.5, 354710 6688393.9 19.5, 354713.3 6688394.7 19.5, 354714.8 6688388.6 19.5, 354716.3 6688388.9 19.5, 354717.8 6688382.7 19.5, 354719.3 6688383 19.5, 354720.8 6688376.8 19.5, 354722.2 6688377.1 19.5, 354723.8 6688370.6 19.5, 354725.3 6688370.9 19.5, 354727 6688364.2 19.5, 354717.8 6688361.9 19.5, 354742.7 6688255.8 19.5, 354685.5 6688242.4 19.5))"
BATIMENT0000000302923159,Indifférenciée,Indifférencié,,Non,En service,2012-06-19 18:43:00,2018-09-18 13:36:27,,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,,,,,11.7,6.0,17.7,24.3,6.6,Cadastre,,"POLYGON Z ((354543.4 6688344.2 17.7, 354534.3 6688360.8 17.7, 354617.6 6688407.1 17.7, 354626.8 6688390.2 17.7, 354543.4 6688344.2 17.7))"
BATIMENT0000002335125943,Indifférenciée,Indifférencié,,Non,En service,2023-10-16 08:40:22,,,,DGFiP,,BDParcellaire,5.0,Pas de Z,9999.0,,,,,,,,,,Cadastre,,"POLYGON Z ((354627.8 6688496.5 -1000, 354637.3 6688498.8 -1000, 354643.7 6688473.3 -1000, 354634.2 6688470.9 -1000, 354627.8 6688496.5 -1000))"
BATIMENT0000002335125944,Indifférenciée,Indifférencié,,Oui,En service,2023-10-16 08:40:22,,,,DGFiP,,BDParcellaire,5.0,Pas de Z,9999.0,,,,,,,,,,Cadastre,,"POLYGON Z ((354626.4 6688497.1 -1000, 354627.8 6688496.5 -1000, 354634.2 6688470.9 -1000, 354643.7 6688473.3 -1000, 354645 6688472.7 -1000, 354633.2 6688469.6 -1000, 354626.4 6688497.1 -1000))"
BATIMENT0000002335125945,Indifférenciée,Indifférencié,,Oui,En service,2023-10-16 08:40:22,,,,DGFiP,,BDParcellaire,5.0,Pas de Z,9999.0,,,,,,,,,,Cadastre,,"POLYGON Z ((354627.8 6688496.5 -1000, 354626.4 6688497.1 -1000, 354638.2 6688500 -1000, 354645 6688472.7 -1000, 354643.7 6688473.3 -1000, 354637.3 6688498.8 -1000, 354627.8 6688496.5 -1000))"
BATIMENT0000000302923157,"Industriel, agricole ou commercial",Industriel,,Non,En service,2012-06-19 18:43:00,2018-09-18 13:36:27,,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,,,,,6.6,6.0,12.6,13.8,6.8,Cadastre,,"POLYGON Z ((354697.2 6688468.6 12.6, 354679.9 6688499.1 12.6, 354699.5 6688510.2 12.6, 354712.5 6688486.8 12.6, 354716.3 6688479.6 12.6, 354717.1 6688478.4 12.6, 354712.7 6688475.8 12.6, 354708.8 6688473.3 12.6, 354707.9 6688474.7 12.6, 354697.2 6688468.6 12.6))"
BATIMENT0000000302923139,"Industriel, agricole ou commercial",Commercial et services,,Oui,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,,,,,BDParcellaire recalée,3.0,Corrélation,1.0,0.0,1.0,,,7.9,6.3,14.2,16.6,6.6,Cadastre,B 1.0,"POLYGON Z ((354676.8 6688507.4 14.2, 354669.8 6688519.7 14.2, 354677.9 6688524.4 14.2, 354683.4 6688527.7 14.2, 354685.2 6688528.7 14.2, 354689.3 6688531 14.2, 354712.5 6688543.7 14.2, 354719.9 6688530.4 14.2, 354689.1 6688514 14.2, 354676.8 6688507.4 14.2))"
BATIMENT0000000302923135,Indifférenciée,Résidentiel,Commercial et services,Non,En service,2012-06-19 18:43:00,2023-01-31 17:40:48,1900-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,5.0,4.0,10,20,10.5,6.2,16.7,20.0,6.5,Cadastre,A 1.0,"POLYGON Z ((354677.9 6688524.4 16.7, 354669.8 6688519.7 16.7, 354664.6 6688529 16.7, 354676.4 6688535.4 16.7, 354680.2 6688528.6 16.7, 354676.5 6688526.6 16.7, 354677.9 6688524.4 16.7))"
BATIMENT0000000302923137,"Industriel, agricole ou commercial",Industriel,,Oui,En service,2012-06-19 18:43:00,2023-01-31 17:40:49,,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,,,,,4.9,6.0,10.9,15.4,6.6,Cadastre,,"POLYGON Z ((354680.5 6688537.6 10.9, 354684.6 6688539.7 10.9, 354686.6 6688535.9 10.9, 354689.3 6688531 10.9, 354685.2 6688528.7 10.9, 354683.4 6688527.7 10.9, 354678.8 6688536.8 10.9, 354680.5 6688537.6 10.9))"
BATIMENT0000000302923136,Indifférenciée,Commercial et services,Résidentiel,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,1900-01-01,,,,BDParcellaire recalée,3.0,Interpolation bâti BDTopo,2.5,6.0,3.0,,,7.3,6.2,13.5,18.3,6.6,Cadastre,A 1.0,"POLYGON Z ((354664.6 6688529 13.5, 354659.1 6688538.6 13.5, 354660.4 6688542 13.5, 354671.5 6688548 13.5, 354678 6688536.3 13.5, 354676.4 6688535.4 13.5, 354664.6 6688529 13.5))"
BATIMENT0000000302923134,Indifférenciée,Résidentiel,Commercial et services,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,1880-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,19.0,5.0,20,20,12.2,6.3,18.5,22.0,6.5,Cadastre,A 1.0,"POLYGON Z ((354684.6 6688539.7 18.5, 354680.5 6688537.6 18.5, 354678.8 6688536.8 18.5, 354678 6688536.3 18.5, 354671.5 6688548 18.5, 354683.8 6688554.7 18.5, 354689.5 6688545.1 18.5, 354683.3 6688542.2 18.5, 354684.6 6688539.7 18.5))"
BATIMENT0000000302923570,"Industriel, agricole ou commercial",Commercial et services,,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,2007-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,0.0,1.0,,,9.0,6.4,15.5,18.5,6.6,Cadastre,C 0.4,"POLYGON Z ((354686.6 6688535.9 15.5, 354692.5 6688539.2 15.5, 354690.5 6688542.8 15.5, 354707.6 6688552.4 15.5, 354712.5 6688543.7 15.5, 354689.3 6688531 15.5, 354686.6 6688535.9 15.5))"
BATIMENT0000000302923571,Indifférenciée,Résidentiel,Commercial et services,Non,En service,2012-06-19 18:43:00,2019-03-15 08:35:34,2007-01-01,,,,BDParcellaire recalée,3.0,Corrélation,1.0,8.0,4.0,00,00,9.4,6.3,15.8,21.1,6.6,Cadastre,C 0.5,"POLYGON Z ((354683.8 6688554.7 15.8, 354692.6 6688559.5 15.8, 354698.9 6688562.9 15.8, 354701.9 6688562.4 15.8, 354707.6 6688552.4 15.8, 354690.5 6688542.8 15.8, 354689.5 6688545.1 15.8, 354683.8 6688554.7 15.8))"
""")
masks = GeoDataFrameLib.read_csv(_sio, sep=",")

masks.fillna({"HAUTEUR": 3.33}, inplace=True)
result = STSkyMap25D(masks, sensors, nRays=64, rayLength=100,
                     elevationFieldname="HAUTEUR", h0=0.0, size=1.0,
                     withIndices=True, withAngles=True, encode=True,
                     threshold=1e-7).run()
print(sensors.columns)
print(result.columns)
'''
