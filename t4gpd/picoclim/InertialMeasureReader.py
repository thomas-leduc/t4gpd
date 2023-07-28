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
from copy import deepcopy
from os.path import basename
import warnings
from zoneinfo import ZoneInfo

from dateutil.parser import parse
from geopandas import GeoDataFrame
from numpy.random import choice
from pandas import read_csv
from shapely.geometry import Point
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.io.AbstractReader import AbstractReader


class InertialMeasureReader(AbstractReader):
    '''
    classdocs

    https://inertialelements.com/osmium-mimu22bl.html
    '''
    FIELDS = {
        "timestamp": str, "step_count": int, "X": float, "Y": float, "Z": float,
        "Distance": float, "degree": float, "latitude": float, "longitude": float,
        "GpsAccuracy": float, "indoor_outdoor_flag": str, "TagName": float
    }

    def __init__(self, inputFile, outputCrs=None, tzinfo="Europe/Paris"):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning
        self.inputFile = inputFile
        self.outputCrs = outputCrs
        self.tzinfo = ZoneInfo(tzinfo)

    @staticmethod
    def getVersion(inputFile):
        VERSIONS = [
            "     time_stamp",
            "\"TIME.STAMP\"",
            " TIME STAMP",
            "     TIME STAMP",
            "timestamp"            
            ]
        with InertialMeasureReader.opener(inputFile) as f:
            line = next(f)
            for i, version in enumerate(VERSIONS, start=0):
                if line.startswith(version):
                    return i
            raise NotImplementedError(f'\n\n\t*** InertialMeasureReader:: unknown file format version! ***')

    def __extract_YYYYMMDD_from_filename(self):
        yyyymmdd = basename(self.inputFile)[9:17]
        year, month, day = yyyymmdd[0:4], yyyymmdd[4:6], yyyymmdd[6:8]
        return year, month, day

    def __getRndSubtrackId(self):
        return "".join(choice([str(i) for i in range(10)], size=10))

    def __readV01(self):
        df = read_csv(self.inputFile, decimal=",", header=None, sep="\s+",
                      names=list(self.FIELDS.keys()),
                      skip_blank_lines=True, skiprows=2)
        for fieldname, fieldtype in self.FIELDS.items():
            if str(fieldtype) == "<class 'int'>":
                df[fieldname] = df[fieldname].astype(int)
            elif str(fieldtype) == "<class 'float'>":
                df[fieldname] = df[fieldname].astype(float)
        return df

    def __readV23(self):
        df = read_csv(self.inputFile, decimal=",", header=None, sep="\s+",
                      names=list(self.FIELDS.keys()), dtype=self.FIELDS,
                      skip_blank_lines=True, skiprows=2)
        return df

    def __readV4(self):
        FIELDS = deepcopy(self.FIELDS)
        FIELDS["Distance"] = str

        df = read_csv(self.inputFile, decimal=",", header=None, sep="\s+",
                      names=list(self.FIELDS.keys()), dtype=FIELDS,
                      skip_blank_lines=True, skiprows=1)
        return df

    def run(self):
        version = self.getVersion(self.inputFile)
        # warnings.warn(f"InertialMeasureReader ({version})")
        if (version in [0, 1]):
            df = self.__readV01()
        elif (version in [2, 3]):
            df = self.__readV23()
        elif (4 == version):
            df = self.__readV4()

        year, month, day = self.__extract_YYYYMMDD_from_filename()
        df.timestamp = df.timestamp.apply(lambda t: parse(f"{year}-{month}-{day}T{t}"))

        df.timestamp = df.timestamp.apply(lambda dt: dt.replace(tzinfo=self.tzinfo))
        if not df.timestamp.is_monotonic_increasing:
            msg = f"Timestamps in {self.inputFile} are not monotonically increasing"
            warnings.warn(msg)

        df["subtrack"] = self.__getRndSubtrackId()

        df["geometry"] = df.apply(lambda row: Point(row.longitude, row.latitude), axis=1)
        df = GeoDataFrame(df, geometry="geometry", crs="epsg:4326")

        if self.outputCrs is None:
            return df
        return df.to_crs(self.outputCrs)

"""
inputFile = "/home/tleduc/prj/nm-ilots-frais/terrain/220711/LOG_FILE_20220711_172000.txt"
df = InertialMeasureReader(inputFile, outputCrs="epsg:2154").run()
print(df.head(3))

inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/05-Quai-de-plantes-Nantes/20200526/localisation/LOG_FILE_20200526_120307.txt"
df = InertialMeasureReader(inputFile, outputCrs="epsg:2154").run()
print(df.head(3))

inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/06-Carriere-misery-Nantes/20200722/localisation/LOG_FILE_20200722_141610.txt"
df = InertialMeasureReader(inputFile, outputCrs="epsg:2154").run()
print(df.head(3))

inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/08-La-defense-Paris/20210721/localisation/LOG_FILE_20210721_182401.txt"
df = InertialMeasureReader(inputFile, outputCrs="epsg:2154").run()
print(df.head(3))
"""
