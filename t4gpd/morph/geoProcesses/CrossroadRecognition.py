'''
Created on 22 juin 2020

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
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess

from t4gpd.commons.crossroads_identification.CrossroadRecognitionLib import CrossroadRecognitionLib


class CrossroadRecognition(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, method, patternsGdf, patternIdFieldName='gid', nRays=64, maxRayLength=None):
        '''
        Constructor
        '''
        if not isinstance(patternsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(patternsGdf, 'GeoDataFrame')

        self.recognEngine = CrossroadRecognitionLib(method=method, nRays=nRays, maxRayLength=maxRayLength)
        self.patternSignatures = self.recognEngine.signatures(patternsGdf, patternIdFieldName, isAPatternLayer=True)

    def runWithArgs(self, row):
        geom = row.geometry

        raylens = GeomLib.fromMultiLineStringToLengths(geom)
        shapeSignature = self.recognEngine.signature(raylens)
        return self.recognEngine.nearestPattern(shapeSignature, self.patternSignatures)
