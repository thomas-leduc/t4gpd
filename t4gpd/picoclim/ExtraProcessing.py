'''
Created on 25 nov. 2022

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
from geopandas import GeoDataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.PySolarSunLib import PySolarSunLib


class ExtraProcessing(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, dfImuMob, inplace=False):
        '''
        Constructor
        '''
        if not isinstance(dfImuMob, GeoDataFrame):
            raise IllegalArgumentTypeException(dfImuMob, "GeoDataFrame")
        if inplace:
            self.dfImuMob = dfImuMob
        else:
            self.dfImuMob = dfImuMob.copy(deep=True)
        self.crs = dfImuMob.crs

        self.sunLib = PySolarSunLib(dfImuMob)

        assert dfImuMob.timestamp.is_monotonic_increasing, f"dfImu.timestamp is not monotonic increasing!"

    def run(self):
        self.dfImuMob.to_crs("epsg:4326", inplace=True)
        self.dfImuMob["lat_cor"] = self.dfImuMob.geometry.apply(lambda geom: geom.y)
        self.dfImuMob["lon_cor"] = self.dfImuMob.geometry.apply(lambda geom: geom.x)
        self.dfImuMob.to_crs(self.crs, inplace=True)

        self.dfImuMob["epoch"] = self.dfImuMob.timestamp.apply(
            lambda dt: dt.timestamp())
            # lambda dt: int(dt.strftime("%s")))
        self.dfImuMob.epoch = self.dfImuMob.epoch.astype(int)

        self.dfImuMob["sun_alti"], self.dfImuMob["sun_azim"] = self.dfImuMob.apply(
            lambda row: self.sunLib.getSolarAnglesInDegrees(row.timestamp.to_pydatetime()),
            axis=1, result_type="expand").to_numpy().transpose()

        return self.dfImuMob
