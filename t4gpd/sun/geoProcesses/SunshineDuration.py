'''
Created on 3 mars 2021

@author: tleduc

Copyright 2020 Thomas Leduc

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
from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.sun.geoProcesses.AbstractSunshineDuration import AbstractSunshineDuration


class SunshineDuration(AbstractSunshineDuration):
    '''
    classdocs
    '''

    def __init__(self, masksGdf, maskElevationFieldname, datetimes, model='pysolar'):
        '''
        Constructor
        '''
        if not isinstance(masksGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(masksGdf, 'GeoDataFrame')
        self.masksGdf = masksGdf
        self.masksSIdx = masksGdf.sindex

        if maskElevationFieldname not in masksGdf:
            raise Exception('%s is not a relevant field name!' % (maskElevationFieldname))
        self.maskElevationFieldname = maskElevationFieldname
        maxElevation = max(self.masksGdf[self.maskElevationFieldname])  #===========

        self.sunModel = SunLib(masksGdf, model)
        self.sunPositions = self._getAllSunPositions(datetimes, maxElevation)
        self.nSunPositions = len(self.sunPositions)

    def runWithArgs(self, row):
        viewpoint = row.geometry.centroid

        nbHits = 0
        for (sunAlti, radDir, rayLen) in self.sunPositions:
            if self._beingInTheSun(viewpoint, radDir, rayLen, sunAlti):
                nbHits += 1

        return {
            'sun_hits': nbHits,
            'sun_ratio': float(nbHits) / self.nSunPositions
            }
