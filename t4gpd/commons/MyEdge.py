"""
Created on 17 juin 2020

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
from t4gpd.commons.MyNode import MyNode


class MyEdge(object):
    """
    classdocs
    """

    __slots__ = ("startNode", "endNode", "startHash", "endHash", "hash")

    def __init__(self, startNode, endNode):
        """
        Constructor
        """
        if isinstance(startNode, list):
            startNode = MyNode(startNode)
        if isinstance(endNode, list):
            endNode = MyNode(endNode)
        startHash = startNode.__hash__()
        endHash = endNode.__hash__()

        if startHash < endHash:
            self.startNode, self.endNode = [startNode, endNode]
            self.startHash, self.endHash = [startHash, endHash]
        else:
            self.startNode, self.endNode = [endNode, startNode]
            self.startHash, self.endHash = [endHash, startHash]

        self.hash = None

    def __eq__(self, other):
        # print 'test MyEdge equality: %s =?= %s' % (self, other)
        return (
            isinstance(other, MyEdge)
            and (self.startNode == other.startNode)
            and (self.endNode == other.endNode)
        )

    def __hash__(self):
        if self.hash is None:
            self.hash = 17
            self.hash = 37 * self.hash + self.startHash
            self.hash = 37 * self.hash + self.endHash
        # print 'hash%s = %d' % (self, self.hash)
        return self.hash

    @staticmethod
    def isnumeric(x):
        return isinstance(x, (int, float))

    def __repr__(self):
        return "[%s --- %s]" % (self.startNode, self.endNode)
