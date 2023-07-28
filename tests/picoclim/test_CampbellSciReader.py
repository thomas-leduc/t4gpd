'''
Created on 29 avr. 2023

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
from io import StringIO
import unittest

from pandas import DataFrame
from t4gpd.picoclim.CampbellSciReader import CampbellSciReader


class CampbellSciReaderTest(unittest.TestCase):

    def setUp(self):
        self.V1 = StringIO(""""TOA5","CR1000XSeries","CR1000X","11356","CR1000X.Std.03.02","CPU:Programme_CS_V2_2sec.CR1X","33184","TwoSec"
"TIMESTAMP","RECORD","BattV_Min","PTemp_C_Avg","CDM1BattV_Min","CDM1PTempC1","CDM1PTempC2","CDM1PTempC3","CDM1PTempC4","AirTC_Avg","AirTC_Min","AirTC_Max","RH_Avg","RH_Min","RH_Max","WindDir","WS_ms_Avg","WS_ms","WS_ms_Min","WS_ms_Max","WS_ms_S_WVT","WindDir_D1_WVT","WSDiag","SmplsF_Tot","Diag1F_Tot","Diag2F_Tot","Diag4F_Tot","Diag8F_Tot","Diag9F_Tot","Diag10F_Tot","NNDF_Tot","CSEF_Tot","SR01Up_1_Avg","SR01Dn_1_Avg","IR01Up_1_Avg","IR01Dn_1_Avg","NR01TC_1_Avg","NR01TK_1_Avg","NetRs_1_Avg","NetRl_1_Avg","Albedo_1_Avg","UpTot_1_Avg","DnTot_1_Avg","NetTot_1_Avg","IR01UpCo_1_Avg","IR01DnCo_1_Avg","SR01Up_2_Avg","SR01Dn_2_Avg","IR01Up_2_Avg","IR01Dn_2_Avg","NR01TC_2_Avg","NR01TK_2_Avg","NetRs_2_Avg","NetRl_2_Avg","Albedo_2_Avg","UpTot_2_Avg","DnTot_2_Avg","NetTot_2_Avg","IR01UpCo_2_Avg","IR01DnCo_2_Avg","SR01Up_3_Avg","SR01Dn_3_Avg","IR01Up_3_Avg","IR01Dn_3_Avg","NR01TC_3_Avg","NR01TK_3_Avg","NetRs_3_Avg","NetRl_3_Avg","Albedo_3_Avg","UpTot_3_Avg","DnTot_3_Avg","NetTot_3_Avg","IR01UpCo_3_Avg","IR01DnCo_3_Avg"
"TS","RN","Volts","Deg C","Volts","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","%","%","%","degrees","meters/second","meters/second","meters/second","meters/second","meters/second","Deg","unitless","","","","","","","","","","W/m^2","W/m^2","W/m^2","W/m^2","Deg C","K","W/m^2","W/m^2","unitless","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","Deg C","K","W/m^2","W/m^2","unitless","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","Deg C","K","W/m^2","W/m^2","unitless","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2"
"","","Min","Avg","Min","Smp","Smp","Smp","Smp","Avg","Min","Max","Avg","Min","Max","Smp","Avg","Smp","Min","Max","WVc","WVc","Smp","Tot","Tot","Tot","Tot","Tot","Tot","Tot","Tot","Tot","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg"
"2020-05-18 11:14:30",1,12.61,24.48,12.64,24.34,24.19,24.18,24.08,19.57,19.57,19.57,34.93,34.93,34.93,30,0.61,0.61,0.61,0.61,0.61,30,0,1,0,0,0,0,0,0,0,0,739.8,117.2,-119.5,44.33,24.14,297.3,622.7,-163.8,0.158,620.3,161.5,458.9,323.4,487.2,653.7,97.7,-25.03,-6.177,23.94,297.1,555.9,-18.85,0.15,628.6,91.6,537.1,416.7,435.6,450.8,93.5,-15.94,-25.27,23.6,296.7,357.3,9.33,0.207,434.9,68.21,366.7,423.7,414.4
"2020-05-18 11:14:32",2,12.61,24.48,12.64,24.34,24.19,24.17,24.08,19.47,19.47,19.47,34.78,34.78,34.78,40,0.83,0.83,0.83,0.83,0.83,40,0,1,0,0,0,0,0,0,0,0,739.9,117,-119.2,44.53,24.15,297.3,622.9,-163.7,0.158,620.7,161.6,459.2,323.8,487.5,653.8,97.6,-24.36,-6.39,23.94,297.1,556.2,-17.97,0.149,629.4,91.2,538.2,417.4,435.3,450.9,93.6,-15.85,-25.3,23.61,296.8,357.3,9.45,0.208,435,68.26,366.7,423.9,414.4
"2020-05-18 11:14:34",3,12.61,24.48,12.64,24.34,24.19,24.17,24.08,19.47,19.47,19.47,34.73,34.73,34.73,33,1.2,1.2,1.2,1.2,1.2,33,0,1,0,0,0,0,0,0,0,0,740,117,-119.1,44.44,24.15,297.3,623,-163.5,0.158,621,161.4,459.5,323.9,487.4,653.9,97.8,-24.1,-6.369,23.94,297.1,556.2,-17.73,0.15,629.8,91.4,538.4,417.6,435.4,450.7,93.8,-16,-25.42,23.61,296.8,356.9,9.42,0.208,434.7,68.38,366.4,423.7,414.3
"2020-05-18 11:14:36",4,12.61,24.48,12.63,24.34,24.2,24.17,24.09,19.47,19.47,19.47,34.67,34.67,34.67,41,1.11,1.11,1.11,1.11,1.11,41,0,1,0,0,0,0,0,0,0,0,739.9,116.8,-119.1,44.24,24.15,297.3,623.1,-163.4,0.158,620.8,161.1,459.8,323.8,487.2,653.9,97.7,-24.06,-6.524,23.94,297.1,556.2,-17.54,0.149,629.9,91.2,538.7,417.6,435.2,450.5,93.9,-16.3,-25.53,23.61,296.8,356.7,9.23,0.208,434.2,68.35,365.9,423.4,414.2
"2020-05-18 11:14:38",5,12.61,24.47,12.63,24.34,24.2,24.17,24.09,19.49,19.49,19.49,34.76,34.76,34.76,63,0.98,0.98,0.98,0.98,0.98,63,0,1,0,0,0,0,0,0,0,0,739.2,115.4,-117.7,44,24.15,297.3,623.8,-161.7,0.156,621.5,159.4,462.1,325.3,487,653.5,97.5,-23.98,-6.501,23.94,297.1,555.9,-17.48,0.149,629.5,91,538.5,417.7,435.2,450.2,93.8,-16.36,-25.75,23.61,296.8,356.4,9.39,0.208,433.9,68.06,365.8,423.4,414
"2020-05-18 11:14:40",6,12.61,24.47,12.63,24.34,24.2,24.17,24.09,19.55,19.55,19.55,34.54,34.54,34.54,44,1.08,1.08,1.08,1.08,1.08,44,0,1,0,0,0,0,0,0,0,0,739,115,-117.3,43.85,24.15,297.3,624,-161.2,0.156,621.7,158.8,462.9,325.7,486.8,653.5,97.4,-24.06,-6.402,23.94,297.1,556,-17.66,0.149,629.4,91,538.4,417.6,435.3,449.9,93.7,-16.24,-25.78,23.62,296.8,356.3,9.54,0.208,433.7,67.89,365.8,423.6,414
""")
        self.V2 = StringIO(""""TOA5","CR1000XSeries","CR1000X","11356","CR1000X.Std.03.02","CPU:Programme_CS_2sec_thermocouple.CR1X","44339","TwoSec"
"TIMESTAMP","RECORD","BattV_Min","PTemp_C_Avg","CDM1BattV_Min","CDM1PTempC1","CDM1PTempC2","CDM1PTempC3","CDM1PTempC4","AirTC_Avg","AirTC_Min","AirTC_Max","RH_Avg","RH_Min","RH_Max","WindDir","WS_ms_Avg","WS_ms","WS_ms_Min","WS_ms_Max","WS_ms_S_WVT","WindDir_D1_WVT","WSDiag","SmplsF_Tot","Diag1F_Tot","Diag2F_Tot","Diag4F_Tot","Diag8F_Tot","Diag9F_Tot","Diag10F_Tot","NNDF_Tot","CSEF_Tot","SR01Up_1_Avg","SR01Dn_1_Avg","IR01Up_1_Avg","IR01Dn_1_Avg","NR01TC_1_Avg","NR01TK_1_Avg","NetRs_1_Avg","NetRl_1_Avg","Albedo_1_Avg","UpTot_1_Avg","DnTot_1_Avg","NetTot_1_Avg","IR01UpCo_1_Avg","IR01DnCo_1_Avg","SR01Up_2_Avg","SR01Dn_2_Avg","IR01Up_2_Avg","IR01Dn_2_Avg","NR01TC_2_Avg","NR01TK_2_Avg","NetRs_2_Avg","NetRl_2_Avg","Albedo_2_Avg","UpTot_2_Avg","DnTot_2_Avg","NetTot_2_Avg","IR01UpCo_2_Avg","IR01DnCo_2_Avg","SR01Up_3_Avg","SR01Dn_3_Avg","IR01Up_3_Avg","IR01Dn_3_Avg","NR01TC_3_Avg","NR01TK_3_Avg","NetRs_3_Avg","NetRl_3_Avg","Albedo_3_Avg","UpTot_3_Avg","DnTot_3_Avg","NetTot_3_Avg","IR01UpCo_3_Avg","IR01DnCo_3_Avg","Temp_C_Avg(1)","Temp_C_Max(1)","Temp_C_Min(1)","Temp_C(1)","Temp_C_Std(1)","Temp_C_Avg(2)","Temp_C_Max(2)","Temp_C_Min(2)","Temp_C(2)","Temp_C_Std(2)"
"TS","RN","Volts","Deg C","Volts","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","%","%","%","degrees","meters/second","meters/second","meters/second","meters/second","meters/second","Deg","unitless","","","","","","","","","","W/m^2","W/m^2","W/m^2","W/m^2","Deg C","K","W/m^2","W/m^2","unitless","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","Deg C","K","W/m^2","W/m^2","unitless","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","Deg C","K","W/m^2","W/m^2","unitless","W/m^2","W/m^2","W/m^2","W/m^2","W/m^2","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C","Deg C"
"","","Min","Avg","Min","Smp","Smp","Smp","Smp","Avg","Min","Max","Avg","Min","Max","Smp","Avg","Smp","Min","Max","WVc","WVc","Smp","Tot","Tot","Tot","Tot","Tot","Tot","Tot","Tot","Tot","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Avg","Max","Min","Smp","Std","Avg","Max","Min","Smp","Std"
"2022-06-17 17:16:32",3682,12.55,35.75,12.58,35.72,35.79,35.72,35.79,32.3,32.3,32.3,33.52,33.52,33.52,179,0.16,0.16,0.16,0.16,0.16,179,0,1,0,0,0,0,0,0,0,0,-1.145,-1.008,-5.051,-7.938,33.9,307,-0.137,2.886,0.88,-6.196,-8.95,2.749,498.9,496,-1.041,-0.318,-5.14,-6.157,33.88,307,-0.723,1.017,0.306,-6.181,-6.476,0.295,498.7,497.7,-0.814,-1.643,-4.317,-6.406,33.98,307.1,0.829,2.089,2.019,-5.131,-8.05,2.918,500.2,498.1,32.53,32.53,32.53,32.53,0,32.61,32.61,32.61,32.61,0
"2022-06-17 17:16:34",3683,12.55,35.75,12.58,35.72,35.79,35.72,35.79,32.29,32.29,32.29,33.52,33.52,33.52,"NAN",0.04,0.04,0.04,0.04,0.04,0,0,1,0,0,0,0,0,0,0,0,-1.126,-1.017,-5.024,-7.903,33.9,307.1,-0.109,2.878,0.903,-6.15,-8.92,2.769,499,496.1,-1.056,-0.339,-5.07,-6.166,33.88,307,-0.717,1.096,0.321,-6.126,-6.505,0.379,498.8,497.7,-0.825,-1.656,-4.337,-6.389,33.98,307.1,0.831,2.051,2.007,-5.162,-8.04,2.882,500.2,498.1,32.49,32.49,32.49,32.49,0,32.61,32.61,32.61,32.61,0
"2022-06-17 17:16:36",3684,12.55,35.75,12.58,35.72,35.79,35.71,35.79,32.29,32.29,32.29,33.53,33.53,33.53,84,0.74,0.74,0.74,0.74,0.74,84,0,1,0,0,0,0,0,0,0,0,-1.102,-1.007,-5.005,-7.86,33.9,307,-0.095,2.855,0.914,-6.107,-8.87,2.76,499,496.1,-0.977,-0.281,-4.973,-6.129,33.88,307,-0.696,1.157,0.288,-5.95,-6.41,0.461,498.9,497.7,-0.794,-1.617,-4.301,-6.341,33.98,307.1,0.823,2.039,2.036,-5.095,-7.958,2.862,500.2,498.2,32.57,32.57,32.57,32.57,0,32.63,32.63,32.63,32.63,0
"2022-06-17 17:16:38",3685,12.55,35.74,12.58,35.72,35.79,35.71,35.79,32.29,32.29,32.29,33.53,33.53,33.53,195,0.46,0.46,0.46,0.46,0.46,195,0,1,0,0,0,0,0,0,0,0,-1.049,-0.981,-4.959,-7.791,33.9,307.1,-0.068,2.832,0.935,-6.008,-8.77,2.764,499.1,496.2,-0.96,-0.257,-5.051,-6.097,33.88,307,-0.703,1.046,0.268,-6.011,-6.354,0.343,498.8,497.8,-0.786,-1.601,-4.298,-6.325,33.98,307.1,0.815,2.028,2.037,-5.083,-7.926,2.842,500.2,498.2,32.54,32.54,32.54,32.54,0,32.61,32.61,32.61,32.61,0
"2022-06-17 17:16:40",3686,12.55,35.74,12.58,35.72,35.79,35.71,35.79,32.29,32.29,32.29,33.53,33.53,33.53,128,0.08,0.08,0.08,0.08,0.08,128,0,1,0,0,0,0,0,0,0,0,-1.044,-0.982,-4.957,-7.821,33.9,307,-0.062,2.864,0.94,-6.001,-8.8,2.802,499,496.2,-0.97,-0.279,-5.135,-6.118,33.88,307,-0.691,0.983,0.288,-6.105,-6.398,0.292,498.7,497.8,-0.802,-1.622,-4.302,-6.35,33.97,307.1,0.82,2.048,2.022,-5.104,-7.972,2.868,500.2,498.1,32.58,32.58,32.58,32.58,0,32.64,32.64,32.64,32.64,0
"2022-06-17 17:16:42",3687,12.55,35.74,12.57,35.72,35.79,35.71,35.79,32.53,32.53,32.53,33.7,33.7,33.7,195,0.09,0.09,0.09,0.09,0.09,195,0,1,0,0,0,0,0,0,0,0,-1.084,-0.984,-4.964,-7.881,33.89,307,-0.1,2.916,0.908,-6.048,-8.86,2.816,499,496.1,-1.001,-0.302,-5.146,-6.137,33.88,307,-0.699,0.99,0.301,-6.147,-6.438,0.291,498.7,497.7,-0.79,-1.631,-4.291,-6.347,33.98,307.1,0.841,2.056,2.066,-5.08,-7.977,2.897,500.2,498.2,32.56,32.56,32.56,32.56,0,32.59,32.59,32.59,32.59,0
""")

    def tearDown(self):
        pass

    def testRunV1(self):
        df = CampbellSciReader(self.V1).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(len(CampbellSciReader.EXPECTED_FIELDS), len(df.columns), "Count columns")
        self.assertEqual(6, len(df), "Count rows")
        self.assertTrue(df.timestamp.is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamp.is_unique, "The timestamps are strictly increasing")

    def testRunV2(self):
        df = CampbellSciReader(self.V2).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(len(CampbellSciReader.EXPECTED_FIELDS), len(df.columns), "Count columns")
        self.assertEqual(6, len(df), "Count rows")
        self.assertTrue(df.timestamp.is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamp.is_unique, "The timestamps are strictly increasing")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
