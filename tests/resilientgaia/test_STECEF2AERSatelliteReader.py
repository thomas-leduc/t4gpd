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
import unittest
from datetime import timedelta
from geopandas import GeoDataFrame
from io import StringIO
from pandas import to_datetime
from pytz import timezone
from shapely import Point
from t4gpd.resilientgaia.STECEF2AERSatelliteReader import STECEF2AERSatelliteReader
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class STECEF2AERSatelliteReaderTest(unittest.TestCase):
    def setUp(self):
        self.sio = StringIO("""
time,lat,lon,alt,timeUTC,satcoordX_0,satcoordY_0,satcoordZ_0,az_0,el_0,satcoordX_1,satcoordY_1,satcoordZ_1,az_1,el_1,satcoordX_2,satcoordY_2,satcoordZ_2,az_2,el_2,satcoordX_3,satcoordY_3,satcoordZ_3,az_3,el_3,satcoordX_4,satcoordY_4,satcoordZ_4,az_4,el_4,satcoordX_5,satcoordY_5,satcoordZ_5,az_5,el_5,satcoordX_6,satcoordY_6,satcoordZ_6,az_6,el_6,satcoordX_7,satcoordY_7,satcoordZ_7,az_7,el_7,satcoordX_8,satcoordY_8,satcoordZ_8,az_8,el_8,satcoordX_9,satcoordY_9,satcoordZ_9,az_9,el_9,satcoordX_10,satcoordY_10,satcoordZ_10,az_10,el_10,satcoordX_11,satcoordY_11,satcoordZ_11,az_11,el_11,satcoordX_12,satcoordY_12,satcoordZ_12,az_12,el_12,satcoordX_13,satcoordY_13,satcoordZ_13,az_13,el_13,satcoordX_14,satcoordY_14,satcoordZ_14,az_14,el_14,satcoordX_15,satcoordY_15,satcoordZ_15,az_15,el_15,satcoordX_16,satcoordY_16,satcoordZ_16,az_16,el_16,satcoordX_17,satcoordY_17,satcoordZ_17,az_17,el_17,satcoordX_18,satcoordY_18,satcoordZ_18,az_18,el_18,satcoordX_19,satcoordY_19,satcoordZ_19,az_19,el_19,satcoordX_20,satcoordY_20,satcoordZ_20,az_20,el_20,satcoordX_21,satcoordY_21,satcoordZ_21,az_21,el_21,satcoordX_22,satcoordY_22,satcoordZ_22,az_22,el_22,satcoordX_23,satcoordY_23,satcoordZ_23,az_23,el_23,satcoordX_24,satcoordY_24,satcoordZ_24,az_24,el_24,satcoordX_25,satcoordY_25,satcoordZ_25,az_25,el_25,satcoordX_26,satcoordY_26,satcoordZ_26,az_26,el_26,satcoordX_27,satcoordY_27,satcoordZ_27,az_27,el_27,satcoordX_28,satcoordY_28,satcoordZ_28,az_28,el_28,satcoordX_29,satcoordY_29,satcoordZ_29,az_29,el_29,satcoordX_30,satcoordY_30,satcoordZ_30,az_30,el_30,satcoordX_31,satcoordY_31,satcoordZ_31,az_31,el_31,satcoordX_32,satcoordY_32,satcoordZ_32,az_32,el_32,satcoordX_33,satcoordY_33,satcoordZ_33,az_33,el_33,satcoordX_34,satcoordY_34,satcoordZ_34,az_34,el_34,satcoordX_35,satcoordY_35,satcoordZ_35,az_35,el_35,satcoordX_36,satcoordY_36,satcoordZ_36,az_36,el_36,satcoordX_37,satcoordY_37,satcoordZ_37,az_37,el_37,satcoordX_38,satcoordY_38,satcoordZ_38,az_38,el_38,satcoordX_39,satcoordY_39,satcoordZ_39,az_39,el_39,satcoordX_40,satcoordY_40,satcoordZ_40,az_40,el_40,satcoordX_41,satcoordY_41,satcoordZ_41,az_41,el_41,satcoordX_42,satcoordY_42,satcoordZ_42,az_42,el_42,satcoordX_43,satcoordY_43,satcoordZ_43,az_43,el_43,satcoordX_44,satcoordY_44,satcoordZ_44,az_44,el_44,satcoordX_45,satcoordY_45,satcoordZ_45,az_45,el_45,satcoordX_46,satcoordY_46,satcoordZ_46,az_46,el_46,satcoordX_47,satcoordY_47,satcoordZ_47,az_47,el_47,satcoordX_48,satcoordY_48,satcoordZ_48,az_48,el_48,satcoordX_49,satcoordY_49,satcoordZ_49,az_49,el_49,satcoordX_50,satcoordY_50,satcoordZ_50,az_50,el_50,satcoordX_51,satcoordY_51,satcoordZ_51,az_51,el_51,satcoordX_52,satcoordY_52,satcoordZ_52,az_52,el_52,satcoordX_53,satcoordY_53,satcoordZ_53,az_53,el_53,satcoordX_54,satcoordY_54,satcoordZ_54,az_54,el_54,satcoordX_55,satcoordY_55,satcoordZ_55,az_55,el_55,satcoordX_56,satcoordY_56,satcoordZ_56,az_56,el_56,satcoordX_57,satcoordY_57,satcoordZ_57,az_57,el_57,satcoordX_58,satcoordY_58,satcoordZ_58,az_58,el_58,satcoordX_59,satcoordY_59,satcoordZ_59,az_59,el_59,satcoordX_60,satcoordY_60,satcoordZ_60,az_60,el_60,satcoordX_61,satcoordY_61,satcoordZ_61,az_61,el_61,satcoordX_62,satcoordY_62,satcoordZ_62,az_62,el_62,satcoordX_63,satcoordY_63,satcoordZ_63,az_63,el_63,satcoordX_64,satcoordY_64,satcoordZ_64,az_64,el_64,satcoordX_65,satcoordY_65,satcoordZ_65,az_65,el_65,satcoordX_66,satcoordY_66,satcoordZ_66,az_66,el_66,satcoordX_67,satcoordY_67,satcoordZ_67,az_67,el_67,satcoordX_68,satcoordY_68,satcoordZ_68,az_68,el_68,satcoordX_69,satcoordY_69,satcoordZ_69,az_69,el_69,satcoordX_70,satcoordY_70,satcoordZ_70,az_70,el_70,satcoordX_71,satcoordY_71,satcoordZ_71,az_71,el_71,satcoordX_72,satcoordY_72,satcoordZ_72,az_72,el_72,satcoordX_73,satcoordY_73,satcoordZ_73,az_73,el_73,satcoordX_74,satcoordY_74,satcoordZ_74,az_74,el_74,satcoordX_75,satcoordY_75,satcoordZ_75,az_75,el_75,satcoordX_76,satcoordY_76,satcoordZ_76,az_76,el_76,satcoordX_77,satcoordY_77,satcoordZ_77,az_77,el_77,satcoordX_78,satcoordY_78,satcoordZ_78,az_78,el_78,satcoordX_79,satcoordY_79,satcoordZ_79,az_79,el_79,satcoordX_80,satcoordY_80,satcoordZ_80,az_80,el_80,satcoordX_81,satcoordY_81,satcoordZ_81,az_81,el_81,satcoordX_82,satcoordY_82,satcoordZ_82,az_82,el_82,satcoordX_83,satcoordY_83,satcoordZ_83,az_83,el_83,satcoordX_84,satcoordY_84,satcoordZ_84,az_84,el_84,satcoordX_85,satcoordY_85,satcoordZ_85,az_85,el_85,satcoordX_86,satcoordY_86,satcoordZ_86,az_86,el_86,satcoordX_87,satcoordY_87,satcoordZ_87,az_87,el_87,satcoordX_88,satcoordY_88,satcoordZ_88,az_88,el_88,satcoordX_89,satcoordY_89,satcoordZ_89,az_89,el_89,satcoordX_90,satcoordY_90,satcoordZ_90,az_90,el_90,satcoordX_91,satcoordY_91,satcoordZ_91,az_91,el_91,satcoordX_92,satcoordY_92,satcoordZ_92,az_92,el_92,satcoordX_93,satcoordY_93,satcoordZ_93,az_93,el_93
224029.994,47.15602143935797,-1.6401549081283249,31.000074934214357,1726582411.994,,,,,,,,,,,,,,,,,,,,,15064118.054378018,-8547444.096584536,19972116.833414152,286.3658540549132,65.64976296482513,,,,,,6682831.629822373,14340237.088736435,21826961.101783626,54.7471253525317,38.006318797197785,,,,,,7489897.474184224,24531920.1494566,6677239.535051605,90.95583036367016,7.239628716971342,,,,,,23302373.041234124,-12300917.407568311,-3009605.625167373,210.98942480825107,18.38180961891682,,,,,,13190582.3130294,-13710358.893409336,18203858.85223725,280.3951115187741,50.11433025870277,,,,,,4551913.878679423,-22160994.58511746,13261896.87142708,283.38024621662896,16.91174153862073,,,,,,,,,,,-6685543.510484115,-13429837.820143318,21928089.96935452,325.14531714579965,12.835239671465368,,,,,,23019923.30890138,-3288116.212899786,12761584.259981131,197.6859777460624,65.17783848926577,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,16320546.92160034,6624602.473295777,20099665.882965315,75.24718699526187,69.23636104710911,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,8321535.084623868,-7479541.322189849,22960797.8550928,322.340291347399,53.939789827257286,,,,,,24908619.146831103,3238661.344358151,4713259.028405649,165.20965091889138,42.04939096861485,,,,,,,,,,,,,,,,,,,,,,,,,,-6536440.84614155,10368823.380351828,22391306.89622521,26.677244089328507,13.413247648867673,12955986.062111938,10041836.043313142,19570701.228262823,68.76425274054806,56.06140124471126,,,,,,,,,,,,,,,,,,,,,,,,,,11327766.548701037,-21507110.47656375,7767716.053455964,260.7454330134794,19.14331847307669,-305016.8454522538,-15334688.261437649,20375002.484596997,311.9350110098034,22.792774533211496,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,13966719.463131452,-15917143.497609103,20677206.80722497,282.75636616603447,49.46483193811896,14421474.5500898,16596251.543444192,19796966.46180697,79.13927289958716,45.51804590809695,,,,,,,,,,,16452378.88486224,6907038.604441991,23614087.148127194,60.539766392533146,68.93903411796862,,,,,,,,,,,,,,,,,,,,,,,,,,-8597132.990503501,-13478202.07135252,24917994.830560684,329.1674539516677,13.28917380390503,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,18867070.988831773,19568047.78507548,11726888.2420156,105.09494193766255,35.180520418526825,,,,,,,,,,,11582891.49294767,-20548561.3361476,17867296.950458802,279.1382714560536,36.24790320538411,,,,,,25132623.439180017,-15630251.08877455,379724.4934849506,218.9045106253043,25.459652262098096
""")
        self.dt959 = to_datetime("2024-09-17 16:13:31+0200")
        self.satNames = ["G05", "G07", "G09", "G11", "G13", "G15", "G18", "G20", "G30", "R07",
                         "R09", "R15", "R16", "R22", "R23", "E05", "E06", "E09", "E15", "E31",
                         "E34", "E36"]

        pass

    def tearDown(self):
        pass

    def testRename_satellites(self):
        actual = STECEF2AERSatelliteReader(self.sio, lat="lat", lon="lon",
                                           alt="alt", sep=",", decimal=".",
                                           iepsg="epsg:4326", oepsg="epsg:2154",
                                           timestampFieldName="timeUTC",
                                           tzinfo=timezone("Europe/Paris")).run()
        actual = STECEF2AERSatelliteReader.rename_satellites(actual)
        for i in range(SatelliteLib.NSAT):
            satName = SatelliteLib.get_satellite_name(i)
            self.assertTrue(f"{satName}_az" in actual, "Test column names")
            self.assertTrue(f"{satName}_el" in actual, "Test column names")
            self.assertTrue(f"{satName}_sr" in actual, "Test column names")

        actual.dropna(axis=1, inplace=True)

        for satName in self.satNames:
            self.assertIn(f"{satName}_az", actual, "Test column names")
            self.assertIn(f"{satName}_el", actual, "Test column names")
            self.assertIn(f"{satName}_sr", actual, "Test column names")

    def testRun(self):
        actual = STECEF2AERSatelliteReader(self.sio, lat="lat", lon="lon",
                                           alt="alt", sep=",", decimal=".",
                                           iepsg="epsg:4326", oepsg="epsg:2154",
                                           timestampFieldName="timeUTC",
                                           tzinfo=timezone("Europe/Paris")).run()

        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(len(actual), 1, "Count rows")
        # New columns: geometry, nsat, sat_{i}_{az,el,sr}
        self.assertEqual(len(actual.columns), 475 +
                         94 * 3 + 2, "Count columns")
        self.assertIsInstance(
            actual.loc[0, "geometry"], Point, "Test geometry column")
        self.assertEqual(actual.loc[0, "nsat"], 22, "Test nsat value")
        self.assertTrue(
            (actual.loc[0, "timeUTC"] - self.dt959) < timedelta(seconds=1), "Test timeUTC value")

        for i in range(SatelliteLib.NSAT):
            self.assertTrue(f"sat_{i}_az" in actual, "Test column names")
            self.assertTrue(f"sat_{i}_el" in actual, "Test column names")
            self.assertTrue(f"sat_{i}_sr" in actual, "Test column names")

        actual.dropna(axis=1, inplace=True)
        for i in [4, 6, 8, 10, 12, 14, 17, 19, 29, 38, 40, 46,
                  47, 53, 54, 62, 63, 66, 72, 88, 91, 93]:
            self.assertTrue(f"sat_{i}_az" in actual, "Test column names")
            self.assertTrue(f"sat_{i}_el" in actual, "Test column names")
            self.assertTrue(f"sat_{i}_sr" in actual, "Test column names")


if __name__ == "__main__":
    # import sys; sys.argv = ['', 'Test.testRun']
    unittest.main()
