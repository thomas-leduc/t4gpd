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


class ListUtilities(object):
    '''
    classdocs
    '''

    @staticmethod
    def isASubSeq(bigList, smallList):
        if (len(bigList) < len(smallList)):
            return False
        for i in range(len(bigList)):            
            if smallList == ListUtilities.rotate(bigList, i)[:len(smallList)]:
                return True
        return False

    @staticmethod
    def rotate(seq, n):
        n = n % len(seq)
        return seq[n:] + seq[:n]

    @staticmethod
    def allRotations(seq):
        if seq is None:
            return None
        return [ListUtilities.rotate(seq, n) for n in range(len(seq))]
