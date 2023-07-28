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
from shapely.ops import unary_union


class Sequence(object):
    '''
    classdocs
    '''

    def __init__(self, nbranchs=8, seq=None, mirror=False):
        '''
        Constructor
        '''
        self.nbranchs = nbranchs
        self.seq = sorted(seq,
                          key=lambda item: item[0] if self.__isContinuousItem(item) else item,
                          reverse=False)
        self.__mirror = mirror
        self.__validation()

    def __eq__(self, obj):
        if ((obj is None) or 
            (not isinstance(obj, Sequence))):
            return False
        return self.__isCongruent(obj)

    def __hash__(self):
        return len(self.seq)

    def mirror(self):
        mirrorSeq = list()
        for item in self.seq:
            if self.__isContinuousItem(item):
                mirrorSeq.append(((self.nbranchs - item[1]) % self.nbranchs,
                                  (self.nbranchs - item[0]) % self.nbranchs))
            else:
                mirrorSeq.append((self.nbranchs - item) % self.nbranchs)
        return Sequence(self.nbranchs, mirrorSeq, self.__mirror);

    def __isCongruent(self, otherSequence):
        if ((otherSequence is None) or
            (not isinstance(otherSequence, Sequence))):
            return False
        if self.__mirror:
            return (self.__isCongruentModuloARotation(otherSequence) or
                    self.__isCongruentModuloARotation(otherSequence.mirror()))
        else:
            return self.__isCongruentModuloARotation(otherSequence)

    def __isCongruentModuloARotation(self, otherSequence):
        if (self.__strictEquality(otherSequence)):
            return True
        for i in range(1, self.nbranchs):
            if (self.__strictEquality(otherSequence.rotate(i))):
                return True
        return False

    def __isContinuousItem(self, item):
        return isinstance(item, (list, tuple))

    def __isValidItem(self, item):
        if self.__isContinuousItem(item):
            return (((0 == item[0]) and (self.nbranchs == item[1])) or 
                    ((item[0] in range(self.nbranchs)) and (item[1] in range(self.nbranchs)))) 
        return (item in range(self.nbranchs))

    def __plus(self, item, offset=1):
        if self.__isContinuousItem(item):
            return ((item[0] + offset) % self.nbranchs, (item[1] + offset) % self.nbranchs)
        return (item + offset) % self.nbranchs

    def __repr__(self):
        return str(self.seq)  # return str(self.seq)

    def __strictEquality(self, otherSequence):
        if ((otherSequence is None) or
            (not isinstance(otherSequence, Sequence)) or
            (self.nbranchs != otherSequence.nbranchs) or
            (len(self.seq) != len(otherSequence.seq))):
            return False
        for i in self.seq:
            if not i in otherSequence.seq:
                return False
        return True

    def __validation(self):
        if (self.nbranchs < 4):
            raise Exception('Illegal argument: nbranchs mut be greater or equal 4!')
        if (len(self.seq) > self.nbranchs):
            raise Exception('Illegal argument: nbranchs mut be greater or equal the seq list number!')
        for item in self.seq:
            if not self.__isValidItem(item):
                raise Exception('Illegal argument: %s is neither in (0..%d) nor in (0..%d, 0..%d)!' % (
                        item, self.nbranchs - 1, self.nbranchs - 1, self.nbranchs - 1))
        # A CONTINUER

    def rotate(self, offset=1):
        newseq = [self.__plus(item, offset) for item in self.seq]
        return Sequence(self.nbranchs, newseq, self.__mirror)

    def asPolygon(self, sequenceRadii, centre=[0, 0]):
        geoms = []

        for item in self.seq:
            if self.__isContinuousItem(item):
                geoms.append(sequenceRadii.getSector(item, centre))
            else:
                geoms.append(sequenceRadii.getBranch(item, centre))

        result = unary_union(geoms).buffer(sequenceRadii.getWidth())
        return result

    def getMinModel(self):
        if (4 == self.nbranchs):
            return 4

        if (0 == (self.nbranchs % 4)):
            q1 = int(self.nbranchs / 4)
            setToTest = [0, q1, 2 * q1, 3 * q1]
            if all([(self.__isContinuousItem(i) or (i in setToTest)) for i in self.seq]):
                return 4

            if (8 == self.nbranchs):
                return 8

            if (0 == (self.nbranchs % 8)):
                e1 = int(self.nbranchs / 8)
                setToTest = [0, e1, 2 * e1, 3 * e1, 4 * e1, 5 * e1, 6 * e1, 7 * e1]
                if all([(self.__isContinuousItem(i) or (i in setToTest)) for i in self.seq]):
                    return 8

        return self.nbranchs
