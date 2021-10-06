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
from shapely.geometry import LineString, Point
from t4gpd.commons.graph.AbstractUrbanGraphLib import AbstractUrbanGraphLib


class UrbanGraphLib(AbstractUrbanGraphLib):
    '''
    classdocs
    '''

    def __init__(self, roads):
        '''
        Constructor
        '''
        self.roads, self.graph, self.ciVertices, self.icVertices, self.edges = AbstractUrbanGraphLib.initializeGraph(roads)
        self.spatialIdx = self.roads.sindex

    def getUniqueRoadsSectionsNodes(self):
        result = list()
        for k, v in self.edges.items():
            nbConnectedVertices = len(v)
            if 2 != nbConnectedVertices:
                result.append({'geometry': Point(self.icVertices[k]), 'gid': k,
                               'nb_connections': nbConnectedVertices })
        return result

    def __getNextVertex(self, prev, curr):
        succ = list(self.edges[curr])
        if 2 == len(succ):
            if (prev == succ[0]) and not (prev == succ[1]):
                return succ[1]
            elif (prev == succ[1]) and not (prev == succ[0]):
                return succ[0]
        return None

    def __burnEdge(self, idx1, idx2, burnedEdges):
        minIdx = min(idx1, idx2)
        maxidx = max(idx1, idx2)
        if minIdx in burnedEdges:
            burnedEdges[minIdx].add(maxidx)
        else:
            burnedEdges[minIdx] = set({ maxidx })

    def __buildRoadSection(self, vertexIndex, nextVertexIndex, burnedEdges):
        result = []

        prevIdx = vertexIndex
        result.append(self.icVertices[prevIdx])
        currIdx = nextVertexIndex
        result.append(self.icVertices[currIdx])
        self.__burnEdge(prevIdx, currIdx, burnedEdges)

        nextIdx = self.__getNextVertex(prevIdx, currIdx)
        while nextIdx is not None:
            result.append(self.icVertices[nextIdx])
            prevIdx = currIdx
            currIdx = nextIdx
            self.__burnEdge(prevIdx, currIdx, burnedEdges)

            if (nextIdx == vertexIndex):
                # current road section is a loop, stop the process
                nextIdx = None
            else:
                nextIdx = self.__getNextVertex(prevIdx, currIdx)            

        return LineString(result)

    def getUniqueRoadsSections(self):
        result = []
        burnedEdges = dict()
        for vertexIndex in list(self.edges.keys()):
            nbConnectedVertices = len(self.edges[vertexIndex])
            if 2 != nbConnectedVertices:
                # current vertex is a 'boundary' of a 'road section'
                for nextVertexIndex in self.edges[vertexIndex]:
                    minIdx = min(vertexIndex, nextVertexIndex)
                    maxIdx = max(vertexIndex, nextVertexIndex)
                    if not (minIdx in burnedEdges and (maxIdx in burnedEdges[minIdx])):
                        geom = self.__buildRoadSection(vertexIndex, nextVertexIndex, burnedEdges)
                        result.append({ 'geometry': geom, 'gid': len(result),
                                       'distance': geom.length })
        return result

    def getUniqueRoadsSectionsWithoutCulDeSac(self):
        result = []

        rs = self.getUniqueRoadsSections()
        for row in rs:
            _coords = list(row['geometry'].coords)
            startHash = UrbanGraphLib.hashCoord(_coords[0])
            stopHash = UrbanGraphLib.hashCoord(_coords[-1])
            if ((1 < len(self.edges[self.ciVertices[startHash]])) and
                (1 < len(self.edges[self.ciVertices[stopHash]]))):
                result.append(row)
        return result
