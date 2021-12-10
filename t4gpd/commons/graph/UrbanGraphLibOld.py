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
from shapely.geometry import LinearRing, LineString, Point, Polygon

from t4gpd.commons.GeomLib import GeomLib


class UrbanGraphLibOld(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.ciVertices = dict()
        self.icVertices = dict()
        self.edges = dict()

    def add(self, features):
        if isinstance(features, list):
            for feature in features:
                self.add(feature)
        else:
            if GeomLib.isAShapelyGeometry(features):
                geom = features
            else:
                geom = features.geometry

            if GeomLib.isMultipart(geom):
                for g in geom.geoms:
                    self.add(g)
            elif isinstance(geom, LineString):
                self.__addPolyline(geom)
            elif isinstance(geom, Polygon):
                self.__addPolyline(geom.exterior)
                for g in geom.interiors:
                    self.__addPolyline(g)
            else:
                raise Exception('Illegal argument in UrbanGraphLib.add(...)!')
        # print('self.icVertices: %s' % self.icVertices)
        # print('self.edges: %s' % self.edges)

    def __addPolyline(self, line):
        if isinstance(line, LinearRing):
            coords = line.coords[:-1]
        else:
            coords = line.coords

        if (2 <= len(coords)):
            prev = self.__addAndGetANode(coords[0])
            for i in range(1, len(coords)):
                curr = self.__addAndGetANode(coords[i]);
                if self.edges.get(prev) is None:
                    self.edges[prev] = set([ curr ])
                else:
                    self.edges[prev].add(curr)
                if self.edges.get(curr) is None:
                    self.edges[curr] = set([ prev ])
                else:
                    self.edges[curr].add(prev)
                prev = curr;

    @staticmethod
    def hashCoord(coord):
        str_coord = ('%f_%f') % (coord[0], coord[1])
        return str_coord

    def __addAndGetANode(self, coord):
        str_coord = UrbanGraphLibOld.hashCoord(coord)
        if self.ciVertices.get(str_coord) is None:
            nodeIndex = len(self.ciVertices)
            self.ciVertices[str_coord] = nodeIndex
            self.icVertices[nodeIndex] = coord
            return nodeIndex   
        else:
            nodeIndex = self.ciVertices[str_coord]
            return nodeIndex   

    def getUniqueRoadsSectionsNodes(self):
        result = list()
        for k, v in list(self.edges.items()):
            nbConnectedVertices = len(v)
            if 2 != nbConnectedVertices:
                result.append({ 'geometry': Point(self.icVertices[k]), 'gid': k,
                               'valency': nbConnectedVertices })
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

    def _buildRoadSection(self, vertexIndex, nextVertexIndex, burnedEdges):
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
                        geom = self._buildRoadSection(vertexIndex, nextVertexIndex, burnedEdges)
                        result.append({ 'geometry': geom, 'gid': len(result),
                                       'distance': geom.length })
        return result

    def getUniqueRoadsSectionsWithoutCulDeSac(self):
        result = []

        rs = self.getUniqueRoadsSections()
        for row in rs:
            _coords = list(row['geometry'].coords)
            startHash = UrbanGraphLibOld.hashCoord(_coords[0])
            stopHash = UrbanGraphLibOld.hashCoord(_coords[-1])
            if ((1 < len(self.edges[self.ciVertices[startHash]])) and
                (1 < len(self.edges[self.ciVertices[stopHash]]))):
                result.append(row)
        return result
