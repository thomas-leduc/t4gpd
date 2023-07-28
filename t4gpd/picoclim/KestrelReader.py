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
import warnings
from zoneinfo import ZoneInfo

from pandas import read_csv
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.io.AbstractReader import AbstractReader


class KestrelReader(AbstractReader):
    '''
    classdocs

    https://kestrelinstruments.com/kestrel-5400-heat-stress-tracker
    '''

    def __init__(self, inputFile, tzinfo="Europe/Paris"):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning
        self.inputFile = inputFile
        self.tzinfo = ZoneInfo(tzinfo)

    def __getVersion(self):
        V1 = "FORMATTED DATE-TIME,Direction – True,Wind Speed,Crosswind Speed,Headwind Speed,Temperature,Globe Temperature,Wind Chill,Relative Humidity,Heat Stress Index,Dew Point,Psychro Wet Bulb Temperature,Station Pressure,Barometric Pressure,Altitude,Density Altitude,NA Wet Bulb Temperature,WBGT"
        V2 = "FORMATTED DATE_TIME,Temperature,Wet Bulb Temp,Globe Temperature,Relative Humidity,Barometric Pressure,Altitude,Station Pressure,Wind Speed,Heat Index,Dew Point,Density Altitude,Crosswind,Headwind,Compass Magnetic Direction,NWB Temp,Compass True Direction,Thermal Work Limit,Wet Bulb Globe Temperature,Wind Chill"
        with KestrelReader.opener(self.inputFile) as f:
            for nline, line in enumerate(f.readlines(), start=1):
                if (4 == nline):
                    if line.startswith(V1):
                        return 1
                    elif line.startswith(V2):
                        return 2
                    raise NotImplementedError(f'\n\n\t*** KestrelReader:: unknown file format version! ***')

    def __readV1(self):
        FIELD_NAMES = [
            "timestamp", "WindDirection", "WindSpeed", "CrosswindSpeed", "HeadwindSpeed",
            "Tair", "GlobeTemperature", "WindChill", "RH", "HeatStressIdx", "DewPoint",
            "PsychroWetBulbTemp", "StationPressure", "BarometricPressure", "Altitude",
            "DensityAltitude", "NAWetBulbTemperature", "WBGT", "TWL", "DirectionMag"] 

        df = read_csv(KestrelReader.opener(self.inputFile), decimal=",",
                      header=None, names=FIELD_NAMES, na_values="***", sep=",",
                      skiprows=5, parse_dates=[0], usecols=range(20))

        dfUnits = read_csv(KestrelReader.opener(self.inputFile), header=None,
                           names=FIELD_NAMES, nrows=1, sep=",", skiprows=4,
                           usecols=range(20))

        if (("km/h" == dfUnits.WindSpeed.squeeze().lower()) or 
            ("km/h" == dfUnits.CrosswindSpeed.squeeze().lower()) or 
            ("km/h" == dfUnits.HeadwindSpeed.squeeze().lower())):
            warnings.warn("Speed in km/h")
            # CONVERT km/h INTO m/s
            for fieldname in ["WindSpeed", "CrosswindSpeed", "HeadwindSpeed"]:
                if ("km/h" == dfUnits[fieldname].squeeze().lower()):
                    df[fieldname] /= 3.6

        df["sensorFamily"] = "Kestrel-5400"

        return df

    def __readV2(self):
        FIELD_NAMES = [
            "timestamp", "Tair", "WetBulbTemperature", "GlobeTemperature", "RH",
            "BarometricPressure", "Altitude", "StationPressure", "WindSpeed", "HeatStressIdx",
            "DewPoint", "DensityAltitude", "CrosswindSpeed", "HeadwindSpeed", "CompassMD",
            "NAWetBulbTemperature", "WindDirection", "TWL", "WBGT", "WindChill", "DataType"] 

        df = read_csv(KestrelReader.opener(self.inputFile), decimal=".",
                      header=None, names=FIELD_NAMES, na_values="--", sep=",",
                      skiprows=5, parse_dates=[0], usecols=range(21))

        dfUnits = read_csv(KestrelReader.opener(self.inputFile), header=None,
                           names=FIELD_NAMES, nrows=1, sep=",", skiprows=4,
                           usecols=range(21))

        if (("km/h" == dfUnits.WindSpeed.squeeze().lower()) or 
            ("km/h" == dfUnits.CrosswindSpeed.squeeze().lower()) or 
            ("km/h" == dfUnits.HeadwindSpeed.squeeze().lower())):
            warnings.warn("Speed in km/h")
            # CONVERT km/h INTO m/s
            for fieldname in ["WindSpeed", "CrosswindSpeed", "HeadwindSpeed"]:
                if ("km/h" == dfUnits[fieldname].squeeze().lower()):
                    df[fieldname] /= 3.6

        df["sensorFamily"] = "Kestrel-5400"

        return df

    def run(self):
        version = self.__getVersion()
        if (1 == version):
            warnings.warn("KestrelReader (v1)")
            df = self.__readV1()
        elif (2 == version):
            df = self.__readV2()
        else:
            raise Exception("Unreachable instruction!")

        df.timestamp = df.timestamp.apply(lambda dt: dt.replace(tzinfo=self.tzinfo))
        if not df.timestamp.is_monotonic_increasing:
            msg = f"Timestamps in {self.inputFile} are not monotonically increasing"
            warnings.warn(msg)

        return df

"""
inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/05-Quai-de-plantes-Nantes/20200518/Kestrel/export_HEAT2414248_2020_5_18_16_44_43.csv"
inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/06-Carriere-misery-Nantes/20200720/Kestrel/export_HEAT2414248_2020_7_20_16_32_54.csv"
df = KestrelReader(inputFile).run()
print(df.head(5))

inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/08-La-defense-Paris/20210904/Kestrel/HEAT_-_2414248_9_4_21_18_31_40.csv"
inputFile = "/home/tleduc/prj/nm-ilots-frais/terrain/220713/HEAT_-_2414248_7_13_22_18_36_20.csv"
inputFile = "/home/tleduc/prj/nm-ilots-frais/terrain/220711/HEAT_-_2414248_7_11_22_18_55_00.csv"
df = KestrelReader(inputFile).run()
print(df.head(5))
"""
