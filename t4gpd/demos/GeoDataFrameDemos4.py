'''
Created on 2 juin 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from io import StringIO
from geopandas import clip
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.demos.AbstractGeoDataFrameDemos import AbstractGeoDataFrameDemos
from t4gpd.demos.NantesBDT import NantesBDT


class GeoDataFrameDemos4(AbstractGeoDataFrameDemos):
    '''
    classdocs
    '''

    @staticmethod
    def bretagneDistrictInNantesRoi():
        _sio = StringIO("""geometry
POLYGON ((355621.6652469886 6689254.702599095, 355621.6652469886 6690054.702599095, 354821.6652469886 6690054.702599095, 354821.6652469886 6689254.702599095, 355621.6652469886 6689254.702599095))
""")
        return GeoDataFrameLib.read_csv(_sio)

    @staticmethod
    def bretagneDistrictInNantesBuildings():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.bretagneDistrictInNantesRoi()
        return NantesBDT.buildings(roi)

    @staticmethod
    def bretagneDistrictInNantesRoads():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.bretagneDistrictInNantesRoi()
        return NantesBDT.roads(roi)

    @staticmethod
    def cathedraleDistrictInNantesRoi():
        _sio = StringIO("""geometry
POLYGON ((356206.6120044511 6689310.160406497, 356206.6120044511 6690187.153400643, 355435.7798654291 6690187.153400643, 355435.7798654291 6689310.160406497, 356206.6120044511 6689310.160406497))
""")
        return GeoDataFrameLib.read_csv(_sio)

    @staticmethod
    def cathedraleDistrictInNantesBuildings():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.cathedraleDistrictInNantesRoi()
        return NantesBDT.buildings(roi)

    @staticmethod
    def cathedraleDistrictInNantesRoads():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.cathedraleDistrictInNantesRoi()
        return NantesBDT.roads(roi)

    @staticmethod
    def comfortPathInNantesRoi():
        _sio = StringIO("""geometry
POLYGON ((355743.641404 6689058.227064, 355743.641404 6689590.284898, 355037.981116 6689590.284898, 355037.981116 6689058.227064, 355743.641404 6689058.227064))
""")
        return GeoDataFrameLib.read_csv(_sio)

    @staticmethod
    def comfortPathInNantesBuildings():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.comfortPathInNantesRoi()
        return NantesBDT.buildings(roi)

    @staticmethod
    def comfortPathInNantesRoads():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.comfortPathInNantesRoi()
        return NantesBDT.roads(roi)

    @staticmethod
    def comfortPathInNantesTrack():
        _sio = StringIO("""gid;geometry
1;LINESTRING (355392.96470584260532632 6689221.3744371235370636, 355412.67132887372281402 6689244.53988672606647015, 355433.09852666116785258 6689255.78011080622673035, 355509.10439810110256076 6689275.44374090060591698, 355490.81650339963380247 6689324.15750889200717211, 355510.3057868488249369 6689336.78874534461647272, 355516.12081579066580161 6689339.13943534158170223, 355555.12937142804730684 6689331.42594018206000328, 355598.87898308114381507 6689341.36065902188420296, 355596.82560778578044847 6689346.87340179178863764, 355591.97690130537375808 6689352.70877896528691053, 355554.56406825740123168 6689396.68252452369779348, 355568.79533843748504296 6689401.76234283577650785, 355643.64140382345067337 6689426.23192811757326126, 355626.02107379987137392 6689471.04311584495007992, 355619.1835743592819199 6689490.28489797003567219, 355596.51908082998124883 6689468.18660745956003666, 355548.96530386694939807 6689445.19262360781431198, 355503.62613612611312419 6689424.17906180489808321, 355505.82558483036700636 6689399.87895506713539362, 355491.82603878510417417 6689398.69437266979366541, 355473.7311866115196608 6689409.93415133375674486, 355458.20811651338590309 6689417.95525676943361759, 355455.99495649326127023 6689428.3657007273286581, 355357.93626119446707889 6689449.15271293930709362, 355371.13083457422908396 6689388.58934582583606243, 355375.57350494508864358 6689369.76685459911823273, 355377.92664316802984104 6689364.25166197493672371, 355367.39326221233932301 6689359.24153527617454529, 355348.53702137572690845 6689350.70210501085966825, 355334.19520349189406261 6689344.32414614781737328, 355279.33167604188201949 6689319.49132502358406782, 355249.94372197875054553 6689306.14160723146051168, 355226.57632894982816651 6689295.84038443118333817, 355188.96458710660226643 6689278.86062657460570335, 355173.42680212174309418 6689285.08317295648157597, 355162.29672422946896404 6689255.99566111341118813, 355158.48683999408967793 6689242.23696675337851048, 355148.74747931980527937 6689212.13882182631641626, 355137.98111592716304585 6689178.65157704427838326, 355143.68804865196580067 6689180.00388703681528568, 355173.19613626052159816 6689159.17779209557920694, 355180.553304047731217 6689166.81197269260883331, 355249.86330052919220179 6689188.67875776905566454, 355259.09168292104732245 6689178.46078986767679453, 355275.34549884573789313 6689158.22706367075443268, 355323.42062583763618022 6689183.11225642077624798, 355353.7870587797369808 6689200.02321627270430326, 355387.35315817449009046 6689218.70356828160583973)
""")
        return GeoDataFrameLib.read_csv(_sio)

    @staticmethod
    def royaleDistrictInNantesRoi():
        _sio = StringIO("""geometry
POLYGON ((355434.58636375755 6689050.073765778, 355434.58636375755 6689576.426100205, 354776.9722446392 6689576.426100205, 354776.9722446392 6689050.073765778, 355434.58636375755 6689050.073765778))
""")
        return GeoDataFrameLib.read_csv(_sio)

    @staticmethod
    def royaleDistrictInNantesBuildings():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.royaleDistrictInNantesRoi()
        return NantesBDT.buildings(roi)

    @staticmethod
    def royaleDistrictInNantesRoads():
        '''
        # SOURCE:
        # https://geoservices.ign.fr/bdtopo
        '''
        roi = GeoDataFrameDemos4.royaleDistrictInNantesRoi()
        return NantesBDT.roads(roi)

    @staticmethod
    def plot():
        import matplotlib.pyplot as plt

        for i, label in enumerate(["Tour Bretagne", "Cathedrale", "Comfort path", "Royale"]):
            # LOAD DATASETS
            if (0 == i):
                roi = GeoDataFrameDemos4.bretagneDistrictInNantesRoi()
                buildings = GeoDataFrameDemos4.bretagneDistrictInNantesBuildings()
                roads = GeoDataFrameDemos4.bretagneDistrictInNantesRoads()
            elif (1 == i):
                roi = GeoDataFrameDemos4.cathedraleDistrictInNantesRoi()
                buildings = GeoDataFrameDemos4.cathedraleDistrictInNantesBuildings()
                roads = GeoDataFrameDemos4.cathedraleDistrictInNantesRoads()
            elif (2 == i):
                roi = GeoDataFrameDemos4.comfortPathInNantesRoi()
                buildings = GeoDataFrameDemos4.comfortPathInNantesBuildings()
                roads = GeoDataFrameDemos4.comfortPathInNantesRoads()
                path = GeoDataFrameDemos4.comfortPathInNantesTrack()
            elif (3 == i):
                roi = GeoDataFrameDemos4.royaleDistrictInNantesRoi()
                buildings = GeoDataFrameDemos4.royaleDistrictInNantesBuildings()
                roads = GeoDataFrameDemos4.royaleDistrictInNantesRoads()

            # MAPPING
            fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
            ax.set_title(f"{label} - {NantesBDT.version()}", size=20)
            roi.boundary.plot(ax=ax, color="red")
            buildings.plot(ax=ax, color="lightgrey")
            roads.plot(ax=ax, color="black", linewidth=0.3)
            if (2 == i):
                path.plot(ax=ax, color="blue")
            ax.axis("off")
            plt.show()
            plt.close(fig)

# GeoDataFrameDemos4.plot()
