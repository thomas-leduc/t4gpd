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
from numpy import roll
from t4gpd.commons.Distances import EuclideanDistance

from t4gpd.commons.crossroads_identification.AbstractMethod import AbstractMethod


class MeanAngularityMethod(AbstractMethod):
    '''
    classdocs
    '''
    def __init__(self, maxRayLength, maxThresholdRatio=0.9):
        self.maxRayLength = maxRayLength
        self.maxThresholdRatio = maxThresholdRatio

    def attrName(self):
        return 'recId_avgA'

    def distance(self, signal, signalRef):
        dists = [EuclideanDistance.compute(roll(signal, offset), signalRef) for offset in range(len(signal))]
        return min(dists)

    def signature(self, raylens, isAPatternLayer):
        azims = self.__azimOffsets(raylens)
        return azims

    def __azimOffsets(self, raylens):
        aw = self.__maximaSequence(raylens)
        if (1 >= len(aw)):
            return [360]
        azimuths = sorted(aw.keys())
        _azimOffsets = []
        prev = -1
        for azim in azimuths:
            if (-1 < prev):
                _azimOffsets.append(azim - prev)
            prev = azim
        if (1 < len(azimuths)):
            _azimOffsets.append(360.0 + azimuths[0] - prev)
        return list(map(int, _azimOffsets))

    def __maximaSequence(self, raylens):
        nRays = len(raylens)

        aw = dict()
        azim, width = -1, -1
        threshold = self.maxThresholdRatio * self.maxRayLength
        for i in range(nRays):
            if (threshold < raylens[i]):
                if 0 == i:
                    j = -1
                    while (threshold < raylens[j]) and (-nRays < j):
                        j -= 1
                    if (-nRays == j):
                        return aw
                    azim = ((nRays + j) * 360.0) / nRays
                    width = 0
                    for _ in range(j, 1):
                        azim += 0.5
                        width += 1
                elif (-1 != width):
                    azim += 0.5
                    width += 1
                else:
                    azim = (i * 360.0) / nRays
                    width = 1
            else:
                if (-1 != width):
                    aw[azim % 360] = width
                    azim = width = -1
        return aw
