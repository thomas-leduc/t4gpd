'''
Created on 24 oct. 2022

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
from datetime import datetime

from pandas import read_csv
from t4gpd.commons.GeoProcess import GeoProcess

from t4gpd.commons.DataFrameLib import DataFrameLib


class MeteoFranceReader(GeoProcess):
    '''
    classdocs
    '''
    FIELD_NAMES = ['station', 'timestamp', 'Tair', 'pressure_hpa', 'ws_ms', 'WindDir',
                   'ws_2_ms', 'WindDir_2', 'RH', 'insolation_min', 'global_radiation',
                   'direct_radiation', 'diffuse_radiation', 'nebulosity', 'visibility'] 

    def __init__(self, inputFile):
        '''
        Constructor
        '''
        self.inputFile = inputFile

    @staticmethod
    def interpolate(df, sensorFamily, fieldname, dt):
        _df = df[ df.sensorFamily == sensorFamily ].copy(deep=True)
        return DataFrameLib.interpolate(_df, 'timestamp', fieldname, dt)

    def run(self):
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
        df = read_csv(self.inputFile, decimal=',', names=self.FIELD_NAMES, sep=';',
                      skiprows=1)
        df.timestamp = df.timestamp.apply(lambda t: datetime.strptime(str(t), '%Y%m%d%H'))
        df['sensorFamily'] = df.station.apply(lambda v: f'{v}')
        return df

'''
inputFile = '/home/tleduc/prj/nm-ilots-frais/information/meteo-france-202207-FRNOR.RR22092917362047672.PPDH.KEYuUfd1B1D2x9uv92O31d1.txt'
df = MeteoFranceReader(inputFile).run()
df = df[ df.sensorFamily == 'MF-44020001'].copy(deep=True)
print(df.head(5))
# print(df)
dt = datetime(2022, 7, 10, 1, 15)
print(dt, MeteoFranceReader.interpolate(df, '44020001', 'Tair', dt))
'''
