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
from shapely.geometry.multilinestring import MultiLineString
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from t4gpd.commons.crossroads_identification.FFTMethod import FFTMethod
from t4gpd.commons.crossroads_identification.FWTMethod import FWTMethod
from t4gpd.commons.crossroads_identification.MeanAngularityMethod import MeanAngularityMethod
from t4gpd.commons.crossroads_identification.MeanVectorMethod import MeanVectorMethod


class CrossroadRecognitionLib(object):
    '''
    classdocs
    '''

    # def __init__(self, identificationMethod, nRays, maxRayLength=None):
    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        method = kwargs['method'] if ('method' in kwargs) else None 

        if method in ['meth1', 'MeanVector']:
            self.method = MeanVectorMethod()

        elif method in ['meth2', 'FFT', 'Fourier']:
            self.method = FFTMethod()

        elif method in ['meth3', 'MeanAngularity']:
            if ('maxRayLength' in kwargs):
                maxRayLength = kwargs['maxRayLength']
            else:
                raise Exception('Set the value of "maxRayLength"!')
            maxThresholdRatio = kwargs['maxThresholdRatio'] if ('maxThresholdRatio' in kwargs) else 0.9
            self.method = MeanAngularityMethod(maxRayLength, maxThresholdRatio)

        elif method in ['meth4', 'FWT', 'Wavelet']:
            if ('nRays' in kwargs):
                nRays = kwargs['nRays']
            else:
                raise Exception('Set the value of "nRays"!')
            wavelet = kwargs['wavelet'] if ('wavelet' in kwargs) else 'Haar'
            nOutputRays = kwargs['nOutputRays'] if ('nOutputRays' in kwargs) else 8
            self.method = FWTMethod(None, wavelet, nRays, nOutputRays)

        else:
            raise Exception('Illegal argument: %s is not a valid method!' % method)

    def attrName(self):
        return self.method.attrName()

    def nearestPattern(self, shapeSignature, patternSignatures):
        return self.method.nearestPattern(shapeSignature, patternSignatures)

    def signatures(self, inputGdf, idFieldName, isAPatternLayer):
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        if idFieldName not in inputGdf:
            raise Exception('%s is not a relevant field name!' % (idFieldName))

        signatures = dict()
        for _, row in inputGdf.iterrows():
            if not isinstance(row.geometry, MultiLineString):
                raise Exception('Must be a GeoDataFrame of MultiLineString!')
            geom = row.geometry
            gid = row[idFieldName]
            raylens = GeomLib.fromMultiLineStringToLengths(geom)
            signatures[gid] = self.method.signature(raylens, isAPatternLayer) 
        return signatures

    def signature(self, raylens, isAPatternLayer=False):
        return self.method.signature(raylens, isAPatternLayer)
        
