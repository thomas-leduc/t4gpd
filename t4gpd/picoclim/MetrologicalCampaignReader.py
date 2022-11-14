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
from glob import glob
from os.path import basename, exists
from sys import stderr

from geopandas import GeoDataFrame
from pandas import concat
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.picoclim.CampbellSciReader import CampbellSciReader
from t4gpd.picoclim.InertialMeasureReader import InertialMeasureReader
from t4gpd.picoclim.KestrelReader import KestrelReader
from t4gpd.picoclim.MeteoFranceReader import MeteoFranceReader
from t4gpd.picoclim.SensirionReader import SensirionReader
from t4gpd.picoclim.TracksWaypointsReader import TracksWaypointsReader


class MetrologicalCampaignReader(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, dirName, dirNameMeteoFr=None):
        '''
        Constructor
        '''
        if not exists(dirName):
            raise IllegalArgumentTypeException(dirName, 'valid directory name')
        self.dirName = dirName

        if not ((dirNameMeteoFr is None) or exists(dirNameMeteoFr)):
            raise IllegalArgumentTypeException(dirNameMeteoFr, 'valid directory name')
        self.dirNameMeteoFr = dirNameMeteoFr

    def __loader(self, filenameFilter, Reader):
        dfs = []
        for filename in glob(filenameFilter):
            print(f'*** {basename(filename)}', file=stderr)
            df = Reader(filename).run()
            dfs.append(df)
        return None if (0 == len(dfs)) else concat(dfs, ignore_index=True)

    def run(self):
        filename = f'{self.dirName}/sig.gpkg'
        print(f'*** {basename(filename)}', file=stderr)
        static, tracks, waypoints = TracksWaypointsReader(filename).run()

        filenameFilter = f'{self.dirName}/LOG_FILE_????????_*.txt'
        dfImu = self.__loader(filenameFilter, InertialMeasureReader)
        dfImu.sort_values(by='timestamp', inplace=True, ignore_index=True)

        filenameFilter = f'{self.dirName}/CR1000XSeries_TwoSec.dat'
        dfMob = self.__loader(filenameFilter, CampbellSciReader)
        if dfMob is not None:
            dfMob.sort_values(by='timestamp', inplace=True, ignore_index=True)

        filenameFilter = f'{self.dirName}/*HEAT*.csv'
        dfStat1 = self.__loader(filenameFilter, KestrelReader)
        if dfStat1 is not None:
            dfStat1.sort_values(by='timestamp', inplace=True, ignore_index=True)

        filenameFilter = f'{self.dirName}/Sensirion_*.edf'
        dfStat2 = self.__loader(filenameFilter, SensirionReader)
        if dfStat2 is not None:
            dfStat2.sort_values(by='timestamp', inplace=True, ignore_index=True)
            if static is not None:
                dfStat2 = dfStat2.merge(static, on='station')
                dfStat2 = GeoDataFrame(dfStat2, crs=static.crs)

        filenameFilter = f'{self.dirNameMeteoFr}/meteo-france-*.txt'
        dfMeteoFr = self.__loader(filenameFilter, MeteoFranceReader)
        if dfMeteoFr is not None:
            dfMeteoFr.sort_values(by='timestamp', inplace=True, ignore_index=True)

        return static, tracks, waypoints, dfImu, dfMob, dfStat1, dfStat2, dfMeteoFr

'''
dirName1 = '/home/tleduc/prj/nm-ilots-frais/terrain/220711'
# dirName1 = '/home/tleduc/prj/nm-ilots-frais/terrain/220713'
dirName2 = '/home/tleduc/prj/nm-ilots-frais/information'

static, tracks, waypoints, dfImu, dfMob, dfStat1, dfStat2, dfMeteoFr = \
    MetrologicalCampaignReader(dirName1, dirName2).run()
'''
