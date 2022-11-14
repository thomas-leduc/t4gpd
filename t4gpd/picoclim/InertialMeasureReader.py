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
from os.path import basename

from dateutil.parser import parse
from geopandas import GeoDataFrame
from numpy.random import choice
from pandas import read_csv
from shapely.geometry import Point
from t4gpd.commons.GeoProcess import GeoProcess


class InertialMeasureReader(GeoProcess):
    '''
    classdocs
    '''
    FIELD_NAMES = [
        'timestamp', 'step_count', 'X', 'Y', 'Z', 'Distance', 'degree',
        'latitude', 'longitude', 'GpsAccuracy', 'indoor_outdoor_flag', 'TagName'
    ]

    def __init__(self, inputFile, outputCrs=None):
        '''
        Constructor
        '''
        self.inputFile = inputFile
        self.outputCrs = outputCrs

    def __extract_YYYYMMDD_from_filename(self):
        yyyymmdd = basename(self.inputFile)[9:17]
        year, month, day = yyyymmdd[0:4], yyyymmdd[4:6], yyyymmdd[6:8]
        return year, month, day

    def __getRndSubtrackId(self):
        return ''.join(choice([str(i) for i in range(10)], size=10))

    def run(self):
        df = read_csv(self.inputFile, decimal=',', header=None,
                      names=self.FIELD_NAMES, sep='\s+',
                      skip_blank_lines=True, skiprows=2)

        year, month, day = self.__extract_YYYYMMDD_from_filename()
        df.timestamp = df.timestamp.apply(lambda t: parse(f'{year}-{month}-{day}T{t}'))

        df['subtrack'] = self.__getRndSubtrackId()

        df['geometry'] = list(zip(df.longitude, df.latitude))
        df.geometry = df.geometry.apply(lambda t: Point(t))
        df = GeoDataFrame(df, crs='epsg:4326')

        if self.outputCrs is None:
            return df
        return df.to_crs(self.outputCrs)

'''
inputFile = '/home/tleduc/prj/nm-ilots-frais/terrain/220711/LOG_FILE_20220711_172000.txt'
df = InertialMeasureReader(inputFile, outputCrs='epsg:2154').run()
print(df.head(5))
'''
