"""
Created on 15 janv. 2021

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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
"""

from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from numpy import exp, log, log2, log10, unique


class Entropy(object):
    """
    classdocs
    """

    __slots__ = "probs"

    def __init__(self, probs):
        """
        Constructor
        """
        for prob in probs:
            if not (0 <= prob <= 1):
                raise IllegalArgumentTypeException(
                    prob, "float value between 0.0 and 1.0"
                )
        self.probs = probs

    @staticmethod
    def createFromIntValuesArray(intValues):
        _, counts = unique(intValues, return_counts=True)
        probs = counts / counts.sum()
        return Entropy(probs)

    @staticmethod
    def createFromDoubleValuesArray(doubleValues, precision=1.0):
        intValues = [int(x / precision) for x in doubleValues]
        return Entropy.createFromIntValuesArray(intValues)

    @staticmethod
    def createFromString(string):
        arrayOfChars = [ord(c) for c in string]
        return Entropy.createFromIntValuesArray(arrayOfChars)

    def h(self, base=exp(1)):
        if exp(1) == base:
            return -sum([prob * log(prob) for prob in self.probs if (0.0 < prob)])
        elif 2 == base:
            return -sum([prob * log2(prob) for prob in self.probs if (0.0 < prob)])
        elif 10 == base:
            return -sum([prob * log10(prob) for prob in self.probs if (0.0 < prob)])
        elif 0 < base:
            _tmp = 1 / log(base)
            return -sum(
                [prob * log(prob) * _tmp for prob in self.probs if (0.0 < prob)]
            )
        raise IllegalArgumentTypeException(base, "must be strictly positive")
