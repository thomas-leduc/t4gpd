'''
Created on 3 dec. 2024

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
import warnings
from zoneinfo import ZoneInfo

from pandas import read_csv
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.io.AbstractReader import AbstractReader


class PicopattReader(AbstractReader):
    '''
    classdocs
    '''
    COLUMNS = ["project_id", "track_id", "section_duration",
               "section_speed", "section_warning", "section_weather",
               "lon_rtk", "lat_rtk"]

    def __init__(self, inputFile, tzinfo="Europe/Paris", ocrs="epsg:2154"):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning
        self.inputFile = inputFile
        self.tzinfo = ZoneInfo(tzinfo)
        self.ocrs = ocrs

    def __get_version(self):
        df = read_csv(PicopattReader.opener(self.inputFile), sep=";", nrows=0)

        if ((37 == len(df.columns)) and
                all([column in df for column in PicopattReader.COLUMNS])):
            return 1.0
        elif ((38 == len(df.columns)) and
                all([column in df for column in PicopattReader.COLUMNS]) and
                ("gnss_accuracy" in df)):
            return 2.0
        raise Exception("File format not as expected!")

    def __fillna(self, df):
        from pandas import DataFrame, isna

        for column in ["project_id", "track_id"]:
            df[column] = df[column].ffill()

        rows, ref = [], {}
        for _, row in df.iterrows():
            sid = row.section_id
            sduration = row.section_duration
            sspeed = row.section_speed
            swarning = row.section_warning
            sweather = row.section_weather

            if isna([sduration, sspeed, swarning, sweather]).all():
                if sid in ref:
                    row.section_duration = ref[sid]["section_duration"]
                    row.section_speed = ref[sid]["section_speed"]
                    row.section_warning = ref[sid]["section_warning"]
                    row.section_weather = ref[sid]["section_weather"]
                else:
                    raise Exception("Unreachable instruction!")
            else:
                ref[sid] = {
                    "section_duration": sduration,
                    "section_speed": sspeed,
                    "section_warning": swarning,
                    "section_weather": sweather
                }
            rows.append(row)
        return DataFrame(rows)

    def __geodataframe(self, df):
        from geopandas import GeoDataFrame
        from shapely import Point

        df["geometry"] = df.apply(
            lambda row: Point(row.lon_rtk, row.lat_rtk), axis=1)
        gdf = GeoDataFrame(df, geometry="geometry", crs="epsg:4326")
        return gdf.to_crs(self.ocrs)

    def run(self):
        version = self.__get_version()

        if (version not in [1.0, 2.0]):
            warnings.warn(
                "Picopatt file format is expected to be equal to 1.0 or 2.0!")

        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
        df = read_csv(PicopattReader.opener(self.inputFile),
                      parse_dates=["timestamp"], sep=";")
        # df.timestamp = df.timestamp.apply(lambda dt: dt.replace(tzinfo=self.tzinfo))
        # df.timestamp = df.timestamp.dt.tz_localize(self.tzinfo).dt.tz_convert("UTC")
        df.timestamp = df.timestamp.dt.tz_localize(self.tzinfo)
        df = self.__fillna(df)
        gdf = self.__geodataframe(df)

        if not gdf.point_id.is_monotonic_increasing:
            msg = f"point_id in {self.inputFile} are not monotonically increasing"
            warnings.warn(msg)

        if not gdf.timestamp.is_monotonic_increasing:
            msg = f"Timestamps in {self.inputFile} are not monotonically increasing"
            warnings.warn(msg)

        return gdf


"""
inputFile = "/media/tleduc/disk_20241128/uclimweb/data/picopatt_montpellier/picopatt_montpellier*antigone*20240710*1412.csv"
df = PicopattReader(inputFile).run()
df.to_csv("/tmp/1.csv", sep=";", index=False)
print(df.head(3))

inputFile = "/media/tleduc/disk_20241128/uclimweb/data/picopatt_nantes/picopatt_nantes*loire*20240919*1829.csv"
df = PicopattReader(inputFile).run()
df.to_csv("/tmp/2.csv", sep=";", index=False)
print(df.head(3))
"""
