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
from pandas.core.common import flatten


class ListUtilities(object):
    '''
    classdocs
    '''

    @staticmethod
    def isASubList(smallList, bigList):
        return all(i in bigList for i in smallList)
        
    @staticmethod
    def isASubSeq(smallList, bigList):
        if (len(bigList) < len(smallList)):
            return False
        for i in range(len(bigList)):            
            if smallList == ListUtilities.rotate(bigList, i)[:len(smallList)]:
                return True
        return False

    @staticmethod
    def flatten(myList):
        return list(flatten(myList))

    @staticmethod
    def lengthOfTheLongestConsecutiveSeq(seq):
        seq = sorted(seq)
        prev, currLen, longestLen = None, 0, 0
        for curr in seq:
            currLen += 1
            if prev is not None:
                if 1 < (curr - prev):
                    longestLen = max(longestLen, currLen - 1)
                    currLen = 1
            prev = curr
        return max(longestLen, currLen)

    @staticmethod
    def rotate(seq, n):
        n = n % len(seq)
        return seq[n:] + seq[:n]

    @staticmethod
    def allRotations(seq):
        if seq is None:
            return None
        return [ListUtilities.rotate(seq, n) for n in range(len(seq))]
