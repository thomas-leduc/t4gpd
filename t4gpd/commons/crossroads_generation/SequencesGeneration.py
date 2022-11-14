'''
Created on 17 juin 2020

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
from itertools import combinations

from numpy import ceil, log10

from t4gpd.commons.crossroads_generation.Sequence import Sequence


class SequencesGeneration(object):
    '''
    classdocs
    '''
    def __init__(self, nbranchs=8, mirror=False, withBranchs=True, withSectors=True):
        '''
        Constructor
        '''
        self.nbranchs = nbranchs
        self.mirror = mirror
        self.withBranchs = withBranchs
        self.withSectors = withSectors

    def __addSingleSeq(self, intermed, seq):
        s = Sequence(self.nbranchs, seq, self.mirror)
        if not s in intermed.keys():
            intermed[s] = None

    def __addMultipleSeq(self, intermed, sector, listOfBranchs):
        for n in range(0, 1 + len(listOfBranchs)):
            listOfCombinations = list(combinations(listOfBranchs, n))
            for combins in listOfCombinations:
                seq = [sector]
                for item in combins:
                    seq.append(item)
                self.__addSingleSeq(intermed, seq)

    def __getSequencesOfBranches(self):
        intermed = dict()
        for n in range(1, self.nbranchs + 1):
            intermed[n] = dict()
            for seq in combinations(range(self.nbranchs), n):
                self.__addSingleSeq(intermed[n], seq)

        maxNumOfSeqPerLen = max([len(intermed[n]) for n in intermed.keys()])
        magnitude = 10 ** int(ceil(log10(maxNumOfSeqPerLen)))

        result = dict()
        for n in intermed.keys():
            for i, seqRef in enumerate(intermed[n].keys()):
                result[n * magnitude + i] = seqRef

        return result

    def __getSequencesOfSectors(self):
        intermed = dict()

        if (0 == (self.nbranchs % 4)):
            q1 = int(self.nbranchs / 4)

            for i in [1, 2, 3]:
                q = i * q1
                complement = [j for j in range(self.nbranchs) if (q < j)]
                intermed[i] = dict()
                self.__addMultipleSeq(intermed[i], (0, q), complement)

            maxNumOfSeqPerLen = max([len(intermed[n]) for n in intermed.keys()])
            magnitude = 10 ** int(ceil(log10(maxNumOfSeqPerLen)))          

        result = dict()
        for n in intermed.keys():
            for i, seqRef in enumerate(intermed[n].keys()):
                result[-n * magnitude - i] = seqRef

        result[-4 * magnitude] = Sequence(self.nbranchs, [(0, self.nbranchs)], self.mirror)

        return result

    def run(self):
        result = dict()

        if (self.withBranchs and self.withSectors):
            allSeq = [self.__getSequencesOfBranches(), self.__getSequencesOfSectors()]
        elif self.withBranchs:
            allSeq = [self.__getSequencesOfBranches()]
        elif self.withSectors:
            allSeq = [self.__getSequencesOfSectors()]
        else:
            allSeq = []

        for r in allSeq:
            result.update(r)
        return result
