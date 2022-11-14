'''
Created on 15 sept. 2022

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
from t4gpd.commons.GeoProcess import GeoProcess
from pandas import read_csv
from _warnings import warn


class CampbellSciReader(GeoProcess):
    '''
    classdocs
    '''
    FIELD_NAMES = [
        'timestamp', 'RECORD', 'BattV_Min', 'PTemp_C_Avg', 'CDM1BattV_Min', 'CDM1PTempC1',
        'CDM1PTempC2', 'CDM1PTempC3', 'CDM1PTempC4', 'AirTC_Avg', 'AirTC_Min', 'AirTC_Max',
        'RH_Avg', 'RH_Min', 'RH_Max', 'WindDir', 'WS_ms_Avg', 'WS_ms', 'WS_ms_Min',
        'WS_ms_Max', 'WS_ms_S_WVT', 'WindDir_D1_WVT', 'WSDiag', 'SmplsF_Tot', 'Diag1F_Tot',
        'Diag2F_Tot', 'Diag4F_Tot', 'Diag8F_Tot', 'Diag9F_Tot', 'Diag10F_Tot', 'NNDF_Tot',
        'CSEF_Tot', 'SR01Up_1_Avg', 'SR01Dn_1_Avg', 'IR01Up_1_Avg', 'IR01Dn_1_Avg',
        'NR01TC_1_Avg', 'NR01TK_1_Avg', 'NetRs_1_Avg', 'NetRl_1_Avg', 'Albedo_1_Avg',
        'UpTot_1_Avg', 'DnTot_1_Avg', 'NetTot_1_Avg', 'IR01UpCo_1_Avg', 'IR01DnCo_1_Avg',
        'SR01Up_2_Avg', 'SR01Dn_2_Avg', 'IR01Up_2_Avg', 'IR01Dn_2_Avg', 'NR01TC_2_Avg',
        'NR01TK_2_Avg', 'NetRs_2_Avg', 'NetRl_2_Avg', 'Albedo_2_Avg', 'UpTot_2_Avg',
        'DnTot_2_Avg', 'NetTot_2_Avg', 'IR01UpCo_2_Avg', 'IR01DnCo_2_Avg', 'SR01Up_3_Avg',
        'SR01Dn_3_Avg', 'IR01Up_3_Avg', 'IR01Dn_3_Avg', 'NR01TC_3_Avg', 'NR01TK_3_Avg',
        'NetRs_3_Avg', 'NetRl_3_Avg', 'Albedo_3_Avg', 'UpTot_3_Avg', 'DnTot_3_Avg',
        'NetTot_3_Avg', 'IR01UpCo_3_Avg', 'IR01DnCo_3_Avg', 'Temp_C_Avg(1)',
        'Temp_C_Max(1)', 'Temp_C_Min(1)', 'Temp_C(1)', 'Temp_C_Std(1)', 'Temp_C_Avg(2)',
        'Temp_C_Max(2)', 'Temp_C_Min(2)', 'Temp_C(2)', 'Temp_C_Std(2)']

    FIELDS_TO_BE_DROPPED = [
        "RECORD", "BattV_Min", "PTemp_C_Avg", "CDM1BattV_Min", "CDM1PTempC1",
        "CDM1PTempC2", "CDM1PTempC3", "CDM1PTempC4", "AirTC_Min", "AirTC_Max", "RH_Min",
        "RH_Max", "WS_ms", "WS_ms_Min", "WS_ms_Max", "WS_ms_S_WVT", "WindDir_D1_WVT",
        "WSDiag", "SmplsF_Tot", "Diag1F_Tot", "Diag2F_Tot", "Diag4F_Tot", "Diag8F_Tot",
        "Diag9F_Tot", "Diag10F_Tot", "NNDF_Tot", "CSEF_Tot", "IR01Up_1_Avg", "IR01Dn_1_Avg",
        "NR01TC_1_Avg", "NR01TK_1_Avg", "NetRs_1_Avg", "NetRl_1_Avg", "UpTot_1_Avg",
        "DnTot_1_Avg", "NetTot_1_Avg", "IR01Up_2_Avg", "IR01Dn_2_Avg", "NR01TC_2_Avg",
        "NR01TK_2_Avg", "NetRs_2_Avg", "NetRl_2_Avg", "UpTot_2_Avg", "DnTot_2_Avg",
        "NetTot_2_Avg", "IR01Up_3_Avg", "IR01Dn_3_Avg", "NR01TC_3_Avg", "NR01TK_3_Avg",
        "NetRs_3_Avg", "NetRl_3_Avg", "UpTot_3_Avg", "DnTot_3_Avg", "NetTot_3_Avg",
        "Temp_C_Max(1)", "Temp_C_Min(1)", "Temp_C(1)", "Temp_C_Std(1)", "Temp_C_Max(2)",
        "Temp_C_Min(2)", "Temp_C(2)", "Temp_C_Std(2)"]

    def __init__(self, inputFile):
        '''
        Constructor
        '''
        self.inputFile = inputFile

    def run(self):
        # https://www.campbellsci.com/cr1000x
        df = read_csv(self.inputFile, header=None, names=self.FIELD_NAMES,
                      na_values='NAN', parse_dates=[0], sep=',', skiprows=4)

        dfUnits = read_csv(self.inputFile, header=None, names=self.FIELD_NAMES,
                           nrows=1, sep=',', skiprows=2)

        for fieldname in ['WS_ms_Avg', 'WS_ms', 'WS_ms_Min', 'WS_ms_Max', 'WS_ms_S_WVT']:
            if ('meters/second' != dfUnits[fieldname].squeeze().lower()):
                warn(f'"{fieldname}" is expected to be in m/s!')

        df['sensorFamily'] = 'cr1000x'
        df.drop(columns=self.FIELDS_TO_BE_DROPPED, inplace=True)

        return df

'''
inputFile = '/home/tleduc/prj/nm-ilots-frais/terrain/220711/CR1000XSeries_TwoSec.dat'
df = CampbellSciReader(inputFile).run()
print(df.head(5))
'''
