'''
Created on 27 sep. 2024

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
from numpy import radians
from pandas import DataFrame, concat
from shapely import Point
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.proj.AEProjectionLib import AEProjectionLib
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class STSatelliteOnSiteProjection(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, sensors, gid="gid", timestamp="timeUTC",
                 proj="Stereographic", size=1):
        '''
        Constructor
        '''
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(
                sensors, "GeoDataFrame")
        self.sensors = sensors
        self.gid, self.timestamp = gid, timestamp
        self.prj = AEProjectionLib.projection_switch(proj)
        self.size = size

    @staticmethod
    def __get_version(sensors):
        for version in [1, 2]:
            if any([f"{s}_az" in sensors for s in SatelliteLib.get_satellite_names(version)]):
                return version
        raise Exception("Unknown version of input file!")

    def __prj_aux(self, row, version):
        result = []
        for sat in SatelliteLib.get_satellite_names(version):
            az, el = row[f"{sat}_az"], row[f"{sat}_el"]
            if (az is None) or (el is None):
                result.append(None)
            else:
                az = AngleLib.northCW2eastCCW(az, degree=True)
                az, el = radians(az), radians(el)
                pp = Point(self.prj(row.geometry, az, el, self.size))
                sr = row[f"{sat}_sr"]
                pp = GeomLib.forceZCoordinateToZ0(pp, z0=sr)
                result.append(pp)
        return result

    def __prj(self, version):
        left = self.sensors.loc[:, [self.gid, self.timestamp, "geometry"]]
        left.reset_index(drop=True, inplace=True)

        right = self.sensors.apply(
            lambda row: self.__prj_aux(row, version),
            axis=1)
        right = right.to_frame(name="satellites")
        right = DataFrame(right.satellites.to_list(),
                          columns=SatelliteLib.get_satellite_names(version))

        df = concat([left, right], axis=1)
        df.dropna(axis=1, how="all", inplace=True)
        return df

    @ staticmethod
    def radar(sat, gid, constellations=["GPS", "Galileo", "GLONASS"], size=1, ofile=None):
        def __label_radar(geom):
            from shapely import get_num_points
            if 2 == get_num_points(geom):
                return 1
            return 52

        def __color_satellite(satName):
            match satName[0]:
                case "R":
                    return "red"
                case "E":
                    return "blue"
                case "G":
                    return "green"
            raise Exception("Unreachable instruction!")

        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from numpy import linspace
        from shapely import LineString, get_point
        from shapely.affinity import rotate, translate
        from shapely.wkt import loads

        df = sat.loc[sat[sat.gid == gid].index]
        df.reset_index(inplace=True)

        vp = loads(df.loc[0, "viewpoint"])

        xaxis = LineString(
            [translate(vp, xoff=-size), translate(vp, xoff=size)])
        axes = GeoDataFrame([{
            "geometry": rotate(xaxis, angle=angle, origin=vp, use_radians=False),
            "label1": f"{270-angle}°",
            "label2": f"{AngleLib.northCW2eastCCW(angle, degree=True)}°"
        } for angle in range(0, 180, 30)])
        circles = GeoDataFrame([{
            "geometry": vp.buffer(size*buffdist/90).boundary,
            "label1": "",
            "label2": int(90 - buffdist)
        } for buffdist in linspace(15, 90, 6)])
        radar = concat([axes, circles])
        radar.reset_index(inplace=True)

        my_cmap = ListedColormap(["red", "green", "blue"])
        fig, ax = plt.subplots(figsize=(8.26, 8.26))
        radar.plot(ax=ax, color="grey", linestyle="dotted", linewidth=0.3)
        radar.apply(lambda x: ax.annotate(
            text=x.label1, xy=get_point(x.geometry, 0).coords[0],
            color="grey", size=10, ha="center", va="center"), axis=1)
        radar.apply(lambda x: ax.annotate(
            text=x.label2, xy=get_point(
                x.geometry, __label_radar(x.geometry)).coords[0],
            color="grey", size=10, ha="center"), axis=1)
        df.plot(ax=ax, marker="o", column="constellation", cmap=my_cmap)
        df.apply(lambda x: ax.annotate(
            text=x.satellite, xy=x.geometry.coords[0][:2],
            color=__color_satellite(x.satellite), size=12, ha="left"), axis=1)
        ax.axis("off")
        if ofile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(ofile, bbox_inches="tight")
        plt.close(fig)

        return df, radar

    def run(self):
        version = STSatelliteOnSiteProjection.__get_version(self.sensors)

        df = self.__prj(version)
        df = df.melt(id_vars=[self.gid, self.timestamp, "geometry"])
        df["viewpoint"] = df.geometry.apply(lambda g: g.wkt)
        df.drop(columns=["geometry"], inplace=True)
        df.rename(columns={"variable": "satName",
                           "value": "geometry"}, inplace=True)
        if version == 1:
            df["satellite"] = df.satName.apply(
                lambda v: SatelliteLib.get_satellite_name(int(v[4:])))
        elif version == 2:
            df["satellite"] = df.satName
        df["constellation"] = df.satellite.apply(
            lambda v: SatelliteLib.constellation(v))
        df = df.loc[df[df.geometry.apply(lambda g: g.is_valid)].index]
        df = df.set_crs(self.sensors.crs, allow_override=True)

        return df


"""
# %run t4gpd/resilientgaia/STSatelliteOnSiteProjection.py

from t4gpd.resilientgaia.STECEF2AERSatelliteReader import STECEF2AERSatelliteReader

ifile = "/home/tleduc/prj/anr_resilientgaia_2024-2028/dev/data/20240917_parcours_timestamp.csv"
aersat = STECEF2AERSatelliteReader(ifile, timestampFieldName="timeUTC").run()
aersat["gid"] = range(len(aersat))
# aersat.timeUTC = aersat.timeUTC.dt.tz_localize("UTC")
aersat.timeUTC = aersat.timeUTC.dt.tz_convert("UTC")

gids = [959]
aersat = aersat.loc[aersat[aersat.gid.isin(gids)].index]

prjsat = STSatelliteOnSiteProjection(aersat, gid="gid",
                                     timestamp="timeUTC", proj="Stereographic", size=1).run()

STSatelliteOnSiteProjection.radar(prjsat, gids[0])
"""

"""
from io import StringIO
from pytz import timezone
from t4gpd.resilientgaia.STECEF2AERSatelliteReader import STECEF2AERSatelliteReader

sio = StringIO('''time,lat,lon,alt,timeUTC,satcoordX_0,satcoordY_0,satcoordZ_0,az_0,el_0,satcoordX_1,satcoordY_1,satcoordZ_1,az_1,el_1,satcoordX_2,satcoordY_2,satcoordZ_2,az_2,el_2,satcoordX_3,satcoordY_3,satcoordZ_3,az_3,el_3,satcoordX_4,satcoordY_4,satcoordZ_4,az_4,el_4,satcoordX_5,satcoordY_5,satcoordZ_5,az_5,el_5,satcoordX_6,satcoordY_6,satcoordZ_6,az_6,el_6,satcoordX_7,satcoordY_7,satcoordZ_7,az_7,el_7,satcoordX_8,satcoordY_8,satcoordZ_8,az_8,el_8,satcoordX_9,satcoordY_9,satcoordZ_9,az_9,el_9,satcoordX_10,satcoordY_10,satcoordZ_10,az_10,el_10,satcoordX_11,satcoordY_11,satcoordZ_11,az_11,el_11,satcoordX_12,satcoordY_12,satcoordZ_12,az_12,el_12,satcoordX_13,satcoordY_13,satcoordZ_13,az_13,el_13,satcoordX_14,satcoordY_14,satcoordZ_14,az_14,el_14,satcoordX_15,satcoordY_15,satcoordZ_15,az_15,el_15,satcoordX_16,satcoordY_16,satcoordZ_16,az_16,el_16,satcoordX_17,satcoordY_17,satcoordZ_17,az_17,el_17,satcoordX_18,satcoordY_18,satcoordZ_18,az_18,el_18,satcoordX_19,satcoordY_19,satcoordZ_19,az_19,el_19,satcoordX_20,satcoordY_20,satcoordZ_20,az_20,el_20,satcoordX_21,satcoordY_21,satcoordZ_21,az_21,el_21,satcoordX_22,satcoordY_22,satcoordZ_22,az_22,el_22,satcoordX_23,satcoordY_23,satcoordZ_23,az_23,el_23,satcoordX_24,satcoordY_24,satcoordZ_24,az_24,el_24,satcoordX_25,satcoordY_25,satcoordZ_25,az_25,el_25,satcoordX_26,satcoordY_26,satcoordZ_26,az_26,el_26,satcoordX_27,satcoordY_27,satcoordZ_27,az_27,el_27,satcoordX_28,satcoordY_28,satcoordZ_28,az_28,el_28,satcoordX_29,satcoordY_29,satcoordZ_29,az_29,el_29,satcoordX_30,satcoordY_30,satcoordZ_30,az_30,el_30,satcoordX_31,satcoordY_31,satcoordZ_31,az_31,el_31,satcoordX_32,satcoordY_32,satcoordZ_32,az_32,el_32,satcoordX_33,satcoordY_33,satcoordZ_33,az_33,el_33,satcoordX_34,satcoordY_34,satcoordZ_34,az_34,el_34,satcoordX_35,satcoordY_35,satcoordZ_35,az_35,el_35,satcoordX_36,satcoordY_36,satcoordZ_36,az_36,el_36,satcoordX_37,satcoordY_37,satcoordZ_37,az_37,el_37,satcoordX_38,satcoordY_38,satcoordZ_38,az_38,el_38,satcoordX_39,satcoordY_39,satcoordZ_39,az_39,el_39,satcoordX_40,satcoordY_40,satcoordZ_40,az_40,el_40,satcoordX_41,satcoordY_41,satcoordZ_41,az_41,el_41,satcoordX_42,satcoordY_42,satcoordZ_42,az_42,el_42,satcoordX_43,satcoordY_43,satcoordZ_43,az_43,el_43,satcoordX_44,satcoordY_44,satcoordZ_44,az_44,el_44,satcoordX_45,satcoordY_45,satcoordZ_45,az_45,el_45,satcoordX_46,satcoordY_46,satcoordZ_46,az_46,el_46,satcoordX_47,satcoordY_47,satcoordZ_47,az_47,el_47,satcoordX_48,satcoordY_48,satcoordZ_48,az_48,el_48,satcoordX_49,satcoordY_49,satcoordZ_49,az_49,el_49,satcoordX_50,satcoordY_50,satcoordZ_50,az_50,el_50,satcoordX_51,satcoordY_51,satcoordZ_51,az_51,el_51,satcoordX_52,satcoordY_52,satcoordZ_52,az_52,el_52,satcoordX_53,satcoordY_53,satcoordZ_53,az_53,el_53,satcoordX_54,satcoordY_54,satcoordZ_54,az_54,el_54,satcoordX_55,satcoordY_55,satcoordZ_55,az_55,el_55,satcoordX_56,satcoordY_56,satcoordZ_56,az_56,el_56,satcoordX_57,satcoordY_57,satcoordZ_57,az_57,el_57,satcoordX_58,satcoordY_58,satcoordZ_58,az_58,el_58,satcoordX_59,satcoordY_59,satcoordZ_59,az_59,el_59,satcoordX_60,satcoordY_60,satcoordZ_60,az_60,el_60,satcoordX_61,satcoordY_61,satcoordZ_61,az_61,el_61,satcoordX_62,satcoordY_62,satcoordZ_62,az_62,el_62,satcoordX_63,satcoordY_63,satcoordZ_63,az_63,el_63,satcoordX_64,satcoordY_64,satcoordZ_64,az_64,el_64,satcoordX_65,satcoordY_65,satcoordZ_65,az_65,el_65,satcoordX_66,satcoordY_66,satcoordZ_66,az_66,el_66,satcoordX_67,satcoordY_67,satcoordZ_67,az_67,el_67,satcoordX_68,satcoordY_68,satcoordZ_68,az_68,el_68,satcoordX_69,satcoordY_69,satcoordZ_69,az_69,el_69,satcoordX_70,satcoordY_70,satcoordZ_70,az_70,el_70,satcoordX_71,satcoordY_71,satcoordZ_71,az_71,el_71,satcoordX_72,satcoordY_72,satcoordZ_72,az_72,el_72,satcoordX_73,satcoordY_73,satcoordZ_73,az_73,el_73,satcoordX_74,satcoordY_74,satcoordZ_74,az_74,el_74,satcoordX_75,satcoordY_75,satcoordZ_75,az_75,el_75,satcoordX_76,satcoordY_76,satcoordZ_76,az_76,el_76,satcoordX_77,satcoordY_77,satcoordZ_77,az_77,el_77,satcoordX_78,satcoordY_78,satcoordZ_78,az_78,el_78,satcoordX_79,satcoordY_79,satcoordZ_79,az_79,el_79,satcoordX_80,satcoordY_80,satcoordZ_80,az_80,el_80,satcoordX_81,satcoordY_81,satcoordZ_81,az_81,el_81,satcoordX_82,satcoordY_82,satcoordZ_82,az_82,el_82,satcoordX_83,satcoordY_83,satcoordZ_83,az_83,el_83,satcoordX_84,satcoordY_84,satcoordZ_84,az_84,el_84,satcoordX_85,satcoordY_85,satcoordZ_85,az_85,el_85,satcoordX_86,satcoordY_86,satcoordZ_86,az_86,el_86,satcoordX_87,satcoordY_87,satcoordZ_87,az_87,el_87,satcoordX_88,satcoordY_88,satcoordZ_88,az_88,el_88,satcoordX_89,satcoordY_89,satcoordZ_89,az_89,el_89,satcoordX_90,satcoordY_90,satcoordZ_90,az_90,el_90,satcoordX_91,satcoordY_91,satcoordZ_91,az_91,el_91,satcoordX_92,satcoordY_92,satcoordZ_92,az_92,el_92,satcoordX_93,satcoordY_93,satcoordZ_93,az_93,el_93
224029.994,47.156021439357964,-1.6401549081283249,31.000074934214354,1726582411.994,,,,,,,,,,,,,,,,,,,,,15064118.054378018,-8547444.096584536,19972116.833414152,286.3658540549132,65.64976296482513,,,,,,6682831.629822373,14340237.088736437,21826961.101783622,54.7471253525317,38.006318797197785,,,,,,7489897.474184224,24531920.149456598,6677239.535051605,90.95583036367016,7.239628716971342,,,,,,23302373.041234124,-12300917.407568313,-3009605.625167373,210.98942480825107,18.38180961891682,,,,,,13190582.313029401,-13710358.893409336,18203858.85223725,280.3951115187741,50.11433025870277,,,,,,4551913.878679423,-22160994.58511746,13261896.87142708,283.38024621662896,16.91174153862073,,,,,,,,,,,-6685543.510484115,-13429837.820143318,21928089.96935452,325.14531714579965,12.835239671465368,,,,,,23019923.30890138,-3288116.212899786,12761584.259981131,197.6859777460624,65.17783848926577,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,16320546.92160034,6624602.473295777,20099665.882965315,75.24718699526187,69.23636104710911,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,8321535.084623868,-7479541.322189849,22960797.855092797,322.340291347399,53.939789827257286,,,,,,24908619.146831106,3238661.344358151,4713259.028405649,165.20965091889138,42.049390968614844,,,,,,,,,,,,,,,,,,,,,,,,,,-6536440.84614155,10368823.380351827,22391306.896225214,26.677244089328507,13.413247648867673,12955986.062111938,10041836.043313142,19570701.228262823,68.76425274054806,56.06140124471126,,,,,,,,,,,,,,,,,,,,,,,,,,11327766.548701035,-21507110.47656375,7767716.053455964,260.7454330134794,19.143318473076686,-305016.8454522538,-15334688.261437649,20375002.484596994,311.9350110098034,22.792774533211496,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,13966719.463131452,-15917143.497609103,20677206.807224974,282.75636616603447,49.464831938118955,14421474.5500898,16596251.543444192,19796966.46180697,79.13927289958716,45.51804590809695,,,,,,,,,,,16452378.884862239,6907038.604441991,23614087.148127194,60.539766392533146,68.93903411796862,,,,,,,,,,,,,,,,,,,,,,,,,,-8597132.990503501,-13478202.071352521,24917994.830560684,329.1674539516677,13.28917380390503,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,18867070.988831773,19568047.78507548,11726888.2420156,105.09494193766257,35.180520418526825,,,,,,,,,,,11582891.49294767,-20548561.3361476,17867296.950458802,279.13827145605353,36.24790320538411,,,,,,25132623.439180017,-15630251.08877455,379724.4934849506,218.9045106253043,25.459652262098096
''')
sat = STECEF2AERSatelliteReader(sio, lat="lat", lon="lon",
                                alt="alt", sep=",", decimal=".",
                                iepsg="epsg:4326", oepsg="epsg:2154",
                                timestampFieldName="timeUTC",
                                tzinfo=timezone("Europe/Paris")).run()
sat["gid"] = range(len(sat))
prjsat = STSatelliteOnSiteProjection(sat, gid="gid",
                                     timestamp="timeUTC", 
                                     proj="Stereographic", size=1).run()
STSatelliteOnSiteProjection.radar(prjsat, 0)
"""

"""
from io import StringIO
from pytz import timezone
from t4gpd.resilientgaia.STECEF2AERSatelliteReader import STECEF2AERSatelliteReader

sio = StringIO('''time,timeUTC,ref_lat,ref_lon,ref_alt,satcoordX_G01,satcoordY_G01,satcoordZ_G01,az_G01,el_G01,satcoordX_G02,satcoordY_G02,satcoordZ_G02,az_G02,el_G02,satcoordX_G03,satcoordY_G03,satcoordZ_G03,az_G03,el_G03,satcoordX_G04,satcoordY_G04,satcoordZ_G04,az_G04,el_G04,satcoordX_G05,satcoordY_G05,satcoordZ_G05,az_G05,el_G05,satcoordX_G06,satcoordY_G06,satcoordZ_G06,az_G06,el_G06,satcoordX_G07,satcoordY_G07,satcoordZ_G07,az_G07,el_G07,satcoordX_G08,satcoordY_G08,satcoordZ_G08,az_G08,el_G08,satcoordX_G09,satcoordY_G09,satcoordZ_G09,az_G09,el_G09,satcoordX_G10,satcoordY_G10,satcoordZ_G10,az_G10,el_G10,satcoordX_G11,satcoordY_G11,satcoordZ_G11,az_G11,el_G11,satcoordX_G12,satcoordY_G12,satcoordZ_G12,az_G12,el_G12,satcoordX_G13,satcoordY_G13,satcoordZ_G13,az_G13,el_G13,satcoordX_G14,satcoordY_G14,satcoordZ_G14,az_G14,el_G14,satcoordX_G15,satcoordY_G15,satcoordZ_G15,az_G15,el_G15,satcoordX_G16,satcoordY_G16,satcoordZ_G16,az_G16,el_G16,satcoordX_G17,satcoordY_G17,satcoordZ_G17,az_G17,el_G17,satcoordX_G18,satcoordY_G18,satcoordZ_G18,az_G18,el_G18,satcoordX_G19,satcoordY_G19,satcoordZ_G19,az_G19,el_G19,satcoordX_G20,satcoordY_G20,satcoordZ_G20,az_G20,el_G20,satcoordX_G21,satcoordY_G21,satcoordZ_G21,az_G21,el_G21,satcoordX_G22,satcoordY_G22,satcoordZ_G22,az_G22,el_G22,satcoordX_G23,satcoordY_G23,satcoordZ_G23,az_G23,el_G23,satcoordX_G24,satcoordY_G24,satcoordZ_G24,az_G24,el_G24,satcoordX_G25,satcoordY_G25,satcoordZ_G25,az_G25,el_G25,satcoordX_G26,satcoordY_G26,satcoordZ_G26,az_G26,el_G26,satcoordX_G27,satcoordY_G27,satcoordZ_G27,az_G27,el_G27,satcoordX_G28,satcoordY_G28,satcoordZ_G28,az_G28,el_G28,satcoordX_G29,satcoordY_G29,satcoordZ_G29,az_G29,el_G29,satcoordX_G30,satcoordY_G30,satcoordZ_G30,az_G30,el_G30,satcoordX_G31,satcoordY_G31,satcoordZ_G31,az_G31,el_G31,satcoordX_G32,satcoordY_G32,satcoordZ_G32,az_G32,el_G32,satcoordX_R01,satcoordY_R01,satcoordZ_R01,az_R01,el_R01,satcoordX_R02,satcoordY_R02,satcoordZ_R02,az_R02,el_R02,satcoordX_R03,satcoordY_R03,satcoordZ_R03,az_R03,el_R03,satcoordX_R04,satcoordY_R04,satcoordZ_R04,az_R04,el_R04,satcoordX_R05,satcoordY_R05,satcoordZ_R05,az_R05,el_R05,satcoordX_R06,satcoordY_R06,satcoordZ_R06,az_R06,el_R06,satcoordX_R07,satcoordY_R07,satcoordZ_R07,az_R07,el_R07,satcoordX_R08,satcoordY_R08,satcoordZ_R08,az_R08,el_R08,satcoordX_R09,satcoordY_R09,satcoordZ_R09,az_R09,el_R09,satcoordX_R10,satcoordY_R10,satcoordZ_R10,az_R10,el_R10,satcoordX_R11,satcoordY_R11,satcoordZ_R11,az_R11,el_R11,satcoordX_R12,satcoordY_R12,satcoordZ_R12,az_R12,el_R12,satcoordX_R13,satcoordY_R13,satcoordZ_R13,az_R13,el_R13,satcoordX_R14,satcoordY_R14,satcoordZ_R14,az_R14,el_R14,satcoordX_R15,satcoordY_R15,satcoordZ_R15,az_R15,el_R15,satcoordX_R16,satcoordY_R16,satcoordZ_R16,az_R16,el_R16,satcoordX_R17,satcoordY_R17,satcoordZ_R17,az_R17,el_R17,satcoordX_R18,satcoordY_R18,satcoordZ_R18,az_R18,el_R18,satcoordX_R19,satcoordY_R19,satcoordZ_R19,az_R19,el_R19,satcoordX_R20,satcoordY_R20,satcoordZ_R20,az_R20,el_R20,satcoordX_R21,satcoordY_R21,satcoordZ_R21,az_R21,el_R21,satcoordX_R22,satcoordY_R22,satcoordZ_R22,az_R22,el_R22,satcoordX_R23,satcoordY_R23,satcoordZ_R23,az_R23,el_R23,satcoordX_R24,satcoordY_R24,satcoordZ_R24,az_R24,el_R24,satcoordX_R25,satcoordY_R25,satcoordZ_R25,az_R25,el_R25,satcoordX_R26,satcoordY_R26,satcoordZ_R26,az_R26,el_R26,satcoordX_E01,satcoordY_E01,satcoordZ_E01,az_E01,el_E01,satcoordX_E02,satcoordY_E02,satcoordZ_E02,az_E02,el_E02,satcoordX_E03,satcoordY_E03,satcoordZ_E03,az_E03,el_E03,satcoordX_E04,satcoordY_E04,satcoordZ_E04,az_E04,el_E04,satcoordX_E05,satcoordY_E05,satcoordZ_E05,az_E05,el_E05,satcoordX_E06,satcoordY_E06,satcoordZ_E06,az_E06,el_E06,satcoordX_E07,satcoordY_E07,satcoordZ_E07,az_E07,el_E07,satcoordX_E08,satcoordY_E08,satcoordZ_E08,az_E08,el_E08,satcoordX_E09,satcoordY_E09,satcoordZ_E09,az_E09,el_E09,satcoordX_E10,satcoordY_E10,satcoordZ_E10,az_E10,el_E10,satcoordX_E11,satcoordY_E11,satcoordZ_E11,az_E11,el_E11,satcoordX_E12,satcoordY_E12,satcoordZ_E12,az_E12,el_E12,satcoordX_E13,satcoordY_E13,satcoordZ_E13,az_E13,el_E13,satcoordX_E14,satcoordY_E14,satcoordZ_E14,az_E14,el_E14,satcoordX_E15,satcoordY_E15,satcoordZ_E15,az_E15,el_E15,satcoordX_E16,satcoordY_E16,satcoordZ_E16,az_E16,el_E16,satcoordX_E17,satcoordY_E17,satcoordZ_E17,az_E17,el_E17,satcoordX_E18,satcoordY_E18,satcoordZ_E18,az_E18,el_E18,satcoordX_E19,satcoordY_E19,satcoordZ_E19,az_E19,el_E19,satcoordX_E20,satcoordY_E20,satcoordZ_E20,az_E20,el_E20,satcoordX_E21,satcoordY_E21,satcoordZ_E21,az_E21,el_E21,satcoordX_E22,satcoordY_E22,satcoordZ_E22,az_E22,el_E22,satcoordX_E23,satcoordY_E23,satcoordZ_E23,az_E23,el_E23,satcoordX_E24,satcoordY_E24,satcoordZ_E24,az_E24,el_E24,satcoordX_E25,satcoordY_E25,satcoordZ_E25,az_E25,el_E25,satcoordX_E26,satcoordY_E26,satcoordZ_E26,az_E26,el_E26,satcoordX_E27,satcoordY_E27,satcoordZ_E27,az_E27,el_E27,satcoordX_E28,satcoordY_E28,satcoordZ_E28,az_E28,el_E28,satcoordX_E29,satcoordY_E29,satcoordZ_E29,az_E29,el_E29,satcoordX_E30,satcoordY_E30,satcoordZ_E30,az_E30,el_E30,satcoordX_E31,satcoordY_E31,satcoordZ_E31,az_E31,el_E31,satcoordX_E32,satcoordY_E32,satcoordZ_E32,az_E32,el_E32,satcoordX_E33,satcoordY_E33,satcoordZ_E33,az_E33,el_E33,satcoordX_E34,satcoordY_E34,satcoordZ_E34,az_E34,el_E34,satcoordX_E35,satcoordY_E35,satcoordZ_E35,az_E35,el_E35,satcoordX_E36,satcoordY_E36,satcoordZ_E36,az_E36,el_E36
398299.204,2024-12-19 14:38:01.203999996+00:00,47.216084432360255,-1.538973191880585,55.997586204341815,,,,,,,,,,,,,,,,,,,,,,,,,,-2227212.4620834417,16742807.598885749,20539460.611057084,46.30066297202466,16.630476715028735,,,,,,,,,,,,,,,,,,,,,,,,,,11975748.38221218,10621903.469048709,20916150.208446637,62.67850741370623,53.9580586950774,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,22108869.86851677,14832291.567426257,2406395.150343817,132.78473701553142,25.762633223864384,15914842.040842991,-4368635.161163021,20400195.64016853,298.2374446069727,77.07839848074514,,,,,,,,,,,3894072.14708332,-16009567.96594236,20817701.62019516,304.65085330111015,31.50903425223217,,,,,,,,,,,,,,,,15462754.402424883,-15638997.119474957,14970413.0004323,264.50929775407957,45.217548306575594,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,17565099.200180758,-17146580.667781487,6870609.225265824,242.8813500686587,30.235354837929343,4722201.286953771,-15173120.266131535,19998852.276201557,303.1980403891194,33.270849246782234,11281145.766162423,-1297492.63024479,22854681.617173515,352.18537647953065,67.99477802325949,6559363.763464042,-16573099.892344808,18194859.538077895,293.8340984893441,33.2381196452567,,,,,,,,,,,,,,,,,,,,,,,,,,9727574.554533878,17642290.372280337,15626785.856009416,77.86995365375326,31.879280302859353,-9864490.970289944,6982233.616854309,22472306.513072617,16.505963045076676,7.95100668136394,6698491.985305129,13312757.492739769,20710032.181273077,55.022730672986306,38.5946862634935,18637981.25385573,14155784.928438967,10157747.069830958,113.83944293781312,40.09327362267713,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,13982696.952389136,10416939.635421772,23912241.03203553,60.07440294931995,58.71620371851876,,,,,,,,,,,,,,,,,,,,,16398686.617544496,-16503546.56279894,18303918.435337137,270.3486121496012,49.04685786060523,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,16110924.774558876,12717250.140704386,18638573.082599934,85.16430409764398,53.79199055244472,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,12022897.209769368,-26684200.366121043,4369877.778365387,256.436985834176,11.450380236186454,,,,,,-6263135.301563082,-16031291.38706986,24075484.399237867,321.90084148040904,15.630274352808543,18512918.85960415,-11710512.280547714,19884302.52123325,268.54101251560803,61.91242880622294,,,,,,,,,,,,,,,,,,,,,,,,,,12539981.218808074,24526684.15463637,10834915.101471787,93.07639446855468,21.196005104845316
''')
sat = STECEF2AERSatelliteReader(sio, lat="ref_lat", lon="ref_lon",
                                alt="ref_alt", sep=",", decimal=".",
                                iepsg="epsg:4326", oepsg="epsg:2154",
                                timestampFieldName="timeUTC",
                                tzinfo=timezone("Europe/Paris")).run()
sat["gid"] = range(len(sat))
prjsat = STSatelliteOnSiteProjection(sat, gid="gid",
                                     timestamp="timeUTC", 
                                     proj="Stereographic", size=1).run()
"""
