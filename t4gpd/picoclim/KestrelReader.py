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
from _warnings import warn

from pandas import read_csv
from t4gpd.commons.GeoProcess import GeoProcess


class KestrelReader(GeoProcess):
    '''
    classdocs
    '''
    FIELD_NAMES = [
        'timestamp', 'Tair', 'WetBulbTemperature', 'GlobeTemperature', 'RH',
        'BarometricPressure', 'Altitude', 'StationPressure', 'WindSpeed', 'HeatStressIdx',
        'DewPoint', 'DensityAltitude', 'CrosswindSpeed', 'HeadwindSpeed', 'CompassMD',
        'NAWetBulbTemperature', 'WindDirection', 'TWL', 'WBGT', 'WindChill', 'DataType'] 
    
    def __init__(self, inputFile):
        '''
        Constructor
        '''
        self.inputFile = inputFile

    def run(self):
        # https://kestrelinstruments.com/kestrel-5400-heat-stress-tracker
        df = read_csv(self.inputFile, decimal='.', header=None,
                      names=self.FIELD_NAMES, na_values='--', sep=',',
                      skiprows=5, parse_dates=[0], usecols=range(21))

        dfUnits = read_csv(self.inputFile, header=None, names=self.FIELD_NAMES,
                           nrows=1, sep=',', skiprows=4, usecols=range(21))

        if (('km/h' == dfUnits.WindSpeed.squeeze().lower()) or 
            ('km/h' == dfUnits.CrosswindSpeed.squeeze().lower()) or 
            ('km/h' == dfUnits.HeadwindSpeed.squeeze()).lower()):
            warn('Speed in km/h')
            # CONVERT km/h INTO m/s
            for fieldname in ['WindSpeed', 'CrosswindSpeed', 'HeadwindSpeed']:
                if ('km/h' == dfUnits[fieldname].squeeze().lower()):
                    df[fieldname] /= 3.6

        df['sensorFamily'] = 'Kestrel-5400'

        return df

'''
# inputFile = '/home/tleduc/prj/nm-ilots-frais/terrain/220713/HEAT_-_2414248_7_13_22_18_36_20.csv'
inputFile = '/home/tleduc/prj/nm-ilots-frais/terrain/220711/HEAT_-_2414248_7_11_22_18_55_00.csv'
df = KestrelReader(inputFile).run()
print(df.head(5))
'''
