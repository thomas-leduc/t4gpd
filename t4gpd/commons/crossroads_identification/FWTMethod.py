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
from numpy import log2, roll

from t4gpd.commons.crossroads_identification.AbstractMethod import AbstractMethod


try:
    from pywt import wavedec, waverec

    class FWTMethod(AbstractMethod):
        '''
        classdocs
        '''

        def __init__(self, level=None, wavelet='haar', nRays=64, nOutputRays=8):
            self.level = level
            self.wavelet = wavelet
            self.nRays = nRays
            self.nOutputRays = nOutputRays

        def attrName(self):
            return 'recId_fwt'

        def distance(self, signal, signalRef):
            return sum(abs(signal - signalRef)) / sum(abs(signalRef))

        def nearestPattern(self, shapeSignature, patternSignatures):
            minDist, minCircShift, closestPatternID = float('inf'), None, None

            for gid in list(patternSignatures.keys()):
                for circShift in list(patternSignatures[gid].keys()):  # SYSTEMATIC ROTATION
                    patternSignature = patternSignatures[gid][circShift]
                    _dist = self.distance(shapeSignature, patternSignature)
                    if _dist < minDist:
                        minDist = _dist
                        minCircShift = circShift
                        closestPatternID = gid
            rotation = -(360.0 * minCircShift) / float(self.nRays)
            return {
                self.attrName():closestPatternID,
                'rotation': rotation,
                'min_dist': minDist
                }

        def __signature(self, raylens):
            coeffs = wavedec(raylens, self.wavelet, level=self.level)
            cAn, cDn = coeffs[0:2]
            rec = waverec([cAn, cDn], self.wavelet)
            return rec

        def signature(self, raylens, isAPatternLayer):
            nRays = len(raylens)
            if self.level is None:
                self.level = int(log2(nRays / self.nOutputRays))

            if isAPatternLayer:
                signatures = dict()
                for circShift in range(0, nRays):  # SYSTEMATIC ROTATION
                # for circShift in [0]:
                    _raylens = roll(raylens, circShift)
                    signatures[circShift] = self.__signature(_raylens)
                return signatures
            return self.__signature(raylens)

except ImportError:

    class FWTMethod(AbstractMethod):
        '''
        classdocs
        '''

        def __init__(self, level=None, wavelet='haar', nRays=64, nOutputRays=8):
            raise Exception('Install PyWavelets first!')
