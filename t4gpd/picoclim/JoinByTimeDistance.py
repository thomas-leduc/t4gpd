'''
Created on 12 oct. 2022

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
from datetime import timedelta
import string

from numpy.random import choice
from pandas import DataFrame, merge_asof
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class JoinByTimeDistance(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, dfImu, dfMob, left_on='timestamp', right_on='timestamp',
                 tolerance=timedelta(minutes=1)):
        '''
        Constructor
        '''
        if not isinstance(dfImu, DataFrame):
            raise IllegalArgumentTypeException(dfImu, 'DataFrame')
        self.dfImu = dfImu

        if not isinstance(dfMob, DataFrame):
            raise IllegalArgumentTypeException(dfMob, 'DataFrame')
        self.dfMob = dfMob

        if not left_on in dfImu:
            raise IllegalArgumentTypeException(left_on, 'is not a valid field name')
        self.left_on = left_on

        if not right_on in dfMob:
            raise IllegalArgumentTypeException(right_on, 'is not a valid field name')
        self.right_on = right_on

        if not isinstance(tolerance, timedelta):
            raise IllegalArgumentTypeException(tolerance, 'timedelta')
        self.tolerance = tolerance

        assert dfImu[left_on].is_monotonic_increasing, f'dfImu.{left_on} is not monotonic increasing!'
        assert dfMob[right_on].is_monotonic_increasing, f'dfMob.{right_on} is not monotonic increasing!'

    def __getRndFieldName(self):
        return ''.join(choice(list(string.ascii_letters), size=10))

    def run(self):
        tmpFieldName = self.__getRndFieldName()
        self.dfMob.rename(columns={self.right_on: tmpFieldName}, inplace=True)

        # ~ https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.merge_asof.html
        gdf = merge_asof(self.dfImu, self.dfMob, left_on=self.left_on,
                         right_on=tmpFieldName, direction='nearest',
                         tolerance=self.tolerance)

        self.dfMob.rename(columns={tmpFieldName: self.right_on}, inplace=True)

        gdf['timedelta_in_s'] = list(zip(gdf[self.left_on], gdf[tmpFieldName]))
        gdf.timedelta_in_s = gdf.timedelta_in_s.apply(lambda t: (t[0] - t[1]).total_seconds()) 

        gdf.drop(columns=[tmpFieldName], inplace=True)
        return gdf

'''
from t4gpd.picoclim.MetrologicalCampaignReader import MetrologicalCampaignReader
from t4gpd.picoclim.SnapImuOnTrackUsingWaypoints import SnapImuOnTrackUsingWaypoints

# dirName = '/home/tleduc/prj/nm-ilots-frais/terrain/220711'
dirName = '/home/tleduc/prj/nm-ilots-frais/terrain/220713'

static, tracks, waypoints, dfImu, dfMob, dfStat1, dfStat2, dfMeteoFr = \
    MetrologicalCampaignReader(dirName).run()
dfImu = dfImu.to_crs(tracks.crs)
imu = SnapImuOnTrackUsingWaypoints(dfImu, tracks, waypoints).run()

dfImuMob = JoinByTimeDistance(imu, dfMob, left_on='timestamp', right_on='timestamp').run()
'''
