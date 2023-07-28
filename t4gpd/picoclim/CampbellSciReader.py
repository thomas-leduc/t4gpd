'''
Created on 15 sept. 2022

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
import warnings
from zoneinfo import ZoneInfo

from pandas import read_csv
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.io.AbstractReader import AbstractReader


class CampbellSciReader(AbstractReader):
    '''
    classdocs

    https://www.campbellsci.com/cr1000x
    '''
    EXPECTED_FIELDS = ["timestamp", "AirTC_Avg", "RH_Avg", "WindDir", "WS_ms_Avg",
                       "SR01Up_1_Avg", "SR01Dn_1_Avg", "Albedo_1_Avg", "IR01UpCo_1_Avg",
                       "IR01DnCo_1_Avg", "SR01Up_2_Avg", "SR01Dn_2_Avg", "Albedo_2_Avg",
                       "IR01UpCo_2_Avg", "IR01DnCo_2_Avg", "SR01Up_3_Avg", "SR01Dn_3_Avg",
                       "Albedo_3_Avg", "IR01UpCo_3_Avg", "IR01DnCo_3_Avg", "Temp_C_Avg(1)",
                       "Temp_C_Avg(2)", "sensorFamily"]

    def __init__(self, inputFile, tzinfo="Europe/Paris"):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning_alt
        self.inputFile = inputFile
        self.tzinfo = ZoneInfo(tzinfo)

    def __getVersion(self):
        V1 = '"TOA5","CR1000XSeries","CR1000X","11356","CR1000X.Std.03.02","CPU:Programme_CS_V2_2sec.CR1X"'
        V2 = '"TOA5","CR1000XSeries","CR1000X","11356","CR1000X.Std.03.02","CPU:Programme_CS_2sec_thermocouple.CR1X"'
        with CampbellSciReader.opener(self.inputFile) as f:
            for line in f.readlines():
                if line.startswith(V1):
                    return 1
                elif line.startswith(V2):
                    return 2
                raise NotImplementedError(f'\n\n\t*** CampbellSciReader:: unknown file format version! ***')

    def __readV1(self):
        # df = read_csv(self.inputFile, header=None, names=self.FIELD_NAMES,
        #               na_values="NAN", parse_dates=[0], sep=",", skiprows=4)
        USECOLS = [0, 9, 12, 15, 16, 32, 33, 40, 44, 45, 46, 47, 54, 58,
                   59, 60, 61, 68, 72, 73]
        df = read_csv(CampbellSciReader.opener(self.inputFile), header=0,
                      na_values="NAN", parse_dates=[0], sep=",",
                      skiprows=[0, 2, 3], usecols=USECOLS)

        dfUnits = read_csv(CampbellSciReader.opener(self.inputFile), header=0,
                           nrows=1, sep=",", skiprows=[0], usecols=USECOLS)
        if ("meters/second" != dfUnits["WS_ms_Avg"].squeeze().lower()):
            warnings.warn(f'"WS_ms_Avg" is expected to be in m/s!')

        df["Temp_C_Avg(1)"] = None
        df["Temp_C_Avg(2)"] = None
        return df

    def __readV2(self):
        # df = read_csv(self.inputFile, header=None, names=self.FIELD_NAMES,
        #               na_values="NAN", parse_dates=[0], sep=",", skiprows=4)
        USECOLS = [0, 9, 12, 15, 16, 32, 33, 40, 44, 45, 46, 47, 54, 58,
                   59, 60, 61, 68, 72, 73, 74, 79]
        df = read_csv(CampbellSciReader.opener(self.inputFile), header=0,
                      na_values="NAN", parse_dates=[0], sep=",",
                      skiprows=[0, 2, 3], usecols=USECOLS)

        dfUnits = read_csv(CampbellSciReader.opener(self.inputFile), header=0,
                           nrows=1, sep=",", skiprows=[0], usecols=USECOLS)
        if ("meters/second" != dfUnits["WS_ms_Avg"].squeeze().lower()):
            warnings.warn(f'"WS_ms_Avg" is expected to be in m/s!')
        return df

    def run(self):
        version = self.__getVersion()

        if (1 == version):
            warnings.warn("CampbellSciReader (v1)")
            df = self.__readV1()
        elif (2 == version):
            df = self.__readV2()
        else:
            raise Exception("Unreachable instruction!")

        df["sensorFamily"] = "cr1000x"
        df.rename(columns={"TIMESTAMP": "timestamp"}, inplace=True)

        if (df.duplicated().any()):
            _df = df.drop_duplicates(subset=None, keep="first", ignore_index=True, inplace=False)
            msg = f"There is at least one duplicate in {self.inputFile} (from {len(df)} to {len(_df)} rows)"
            warnings.warn(msg)
            df = _df
        if not df.timestamp.is_monotonic_increasing:
            msg = f"Timestamps in {self.inputFile} are not monotonically increasing"
            warnings.warn(msg)

        df.timestamp = df.timestamp.apply(lambda dt: dt.replace(tzinfo=self.tzinfo)) 

        return df

"""
inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/05-Quai-de-plantes-Nantes/20200518/CS/CR1000XSeries_TwoSec.dat"
df = CampbellSciReader(inputFile).run()
print(df.head(5))

inputFile = "/home/tleduc/prj/nm-ilots-frais/terrain/220711/CR1000XSeries_TwoSec.dat"
df = CampbellSciReader(inputFile).run()
print(df.head(5))

inputFile = "/home/tleduc/prj/prairie-duc/230503/CR1000XSeries_TwoSec.dat"
df = CampbellSciReader(inputFile).run()
print(df.head(5))
"""
