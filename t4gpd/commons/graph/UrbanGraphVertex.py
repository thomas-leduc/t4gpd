'''
Created on 27 oct 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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


class UrbanGraphVertex(object):
    '''
    classdocs
    '''

    @ staticmethod
    def hash_coord(coord):
        str_coord = f"{coord[0]}_{coord[1]}"
        return str_coord

    @staticmethod
    def add_vertex(ciVertices, icVertices, coord):
        str_coord = UrbanGraphVertex.hash_coord(coord)
        if not str_coord in ciVertices:
            nodeIndex = len(ciVertices)
            ciVertices[str_coord] = nodeIndex
            icVertices[nodeIndex] = coord
        else:
            nodeIndex = ciVertices[str_coord]
        return nodeIndex
