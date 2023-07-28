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
import re
import warnings
from zoneinfo import ZoneInfo

from pandas import read_csv
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.io.AbstractReader import AbstractReader


class SensirionReader(AbstractReader):
    '''
    classdocs

    https://sensirion.com/products/catalog/SHT40/
    '''
    FIELD_NAMES = ['local_datetime', 'Tair', 'RH'] 

    RE1 = re.compile(r'^# EdfVersion=(\d\.\d)$')
    RE2 = re.compile(r'^# SensorFamily=(\w*).*$')
    RE3 = re.compile(r'^# SensorId=(.*)$')

    def __init__(self, inputFile, tzinfo="Europe/Paris"):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning
        self.inputFile = inputFile
        self.tzinfo = ZoneInfo(tzinfo)

    def __getEdfVersionAndSensorSpecs(self):
        with SensirionReader.opener(self.inputFile) as f:
            for nline, line in enumerate(f, start=1):
                line = line.strip()
                if (1 == nline):
                    version = float(self.RE1.search(line).group(1))
                elif (6 == nline):
                    sensorFamily = self.RE2.search(line).group(1)
                elif (7 == nline):
                    sensorId = self.RE3.search(line).group(1)
                    sensorId = sensorId.replace(':', '')
                    return version, sensorFamily, sensorId

    def run(self):
        version, sensorFamily, sensorId = self.__getEdfVersionAndSensorSpecs()

        if (4.0 != version):
            warnings.warn('EdfVersion is expected to be equal to 4.0!')

        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
        df = read_csv(SensirionReader.opener(self.inputFile), header=None,
                      names=self.FIELD_NAMES, parse_dates=['local_datetime'],
                      sep='\s+', skiprows=10, usecols=range(1, 4))
        # df.Epoch_UTC = df.Epoch_UTC.apply(lambda v: datetime.fromtimestamp(v))
        df.rename(columns={'local_datetime': 'timestamp'}, inplace=True)
        df['sensorFamily'] = sensorFamily
        df['sensorId'] = sensorId
        df['station'] = f'{sensorFamily}-{sensorId}'

        df.timestamp = df.timestamp.apply(lambda dt: dt.replace(tzinfo=self.tzinfo))
        if not df.timestamp.is_monotonic_increasing:
            msg = f"Timestamps in {self.inputFile} are not monotonically increasing"
            warnings.warn(msg)

        return df

'''
inputFile = '/home/tleduc/prj/nm-ilots-frais/terrain/220711/Sensirion_MyAmbience_SHT40_Gadget_0F0E_2022-07-11T18-49-50.435746.edf'
df = SensirionReader(inputFile).run()
print(df.head(5))
'''
