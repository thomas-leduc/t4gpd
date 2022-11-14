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
from t4gpd.commons.Distances import EuclideanDistance


class AbstractMethod(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        raise NotImplementedError('The class AbstractMethod can not be instanciated!')

    def attrName(self):
        raise NotImplementedError('The method must be implemented!')

    def distance(self, signal, signalRef):
        return EuclideanDistance.compute(signal, signalRef)
        # return np.sum(abs(signal - signalRef)) / np.sum(abs(signalRef))
        # return np.sum((signal - signalRef)**2) / np.sum(signalRef**2)

    def nearestPattern(self, shapeSignature, patternSignatures):
        minDist, closestPatternID = float('inf'), None

        for gid, patternSignature in list(patternSignatures.items()):
            _dist = self.distance(shapeSignature, patternSignature)
            if _dist < minDist:
                minDist = _dist
                closestPatternID = gid
        return { self.attrName():closestPatternID }

    def signature(self, raylens, isAPatternLayer):
        raise NotImplementedError('The method must be implemented!')
