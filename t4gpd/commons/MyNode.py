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
from shapely.geometry import Point

from t4gpd.commons.Epsilon import Epsilon


class MyNode(object):
    '''
    classdocs
    '''

    @staticmethod
    def isnumeric(x):
        return isinstance(x, (int, float))

    def __init__(self, *args):
        '''
        Constructor
        '''
        if (1 == len(args)) and isinstance(args[0], Point):
            self.x, self.y, self.z = [args[0].x, args[0].y] + [0.0]

        elif (1 == len(args)) and isinstance(args[0], (list, tuple)) and (2 <= len(args[0])):
            self.x, self.y, self.z = list(args[0]) + [0.0] if (2 == len(args[0])) else args[0]

        elif (2 <= len(args)) and MyNode.isnumeric(args[0]) and MyNode.isnumeric(args[1]):
            self.x, self.y = [ args[0], args[1] ]
            self.z = args[2] if (3 <= len(args)) else 0.0

        else:
            raise RuntimeError('Initialization error with %s of type %s' % (args, type(args)))
        self.hash = None

    def foo(self, x):
        # TODO: comprendre pourquoi j'ai besoin de ce patch debile ?!
        return x if isinstance(x, float) else x()

    def __eq__(self, other):
        selfx, selfy, selfz = [ self.foo(self.x), self.foo(self.y), self.foo(self.z)]
        otherx, othery, otherz = [ self.foo(other.x), self.foo(other.y), self.foo(other.z)]
        result = (isinstance(other, MyNode) and Epsilon.equals(selfx, otherx) and 
                  Epsilon.equals(selfy, othery) and Epsilon.equals(selfz, otherz))
        return result 

    def __hash__(self):
        selfx, selfy, selfz = [ self.foo(self.x), self.foo(self.y), self.foo(self.z)]

        if self.hash is None:
            self.hash = 17
            self.hash = 37 * self.hash + hash(selfx)
            self.hash = 37 * self.hash + hash(selfy)
            self.hash = 37 * self.hash + hash(selfz)
        return self.hash

    def __repr__(self):
        selfx, selfy, selfz = [ self.foo(self.x), self.foo(self.y), self.foo(self.z)]
        return '(%.1f, %.1f, %.1f)' % (selfx, selfy, selfz)
