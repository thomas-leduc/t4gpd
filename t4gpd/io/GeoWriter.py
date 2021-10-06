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
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import Point

from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.MyEdge import MyEdge
from t4gpd.commons.MyNode import MyNode


class GeoWriter(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, outputFile, characteristicLength=10.0, toLocalCrs=True):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.outputFile = outputFile
        self.lc = characteristicLength
        self.toLocalCrs = toLocalCrs

    def run(self):
        newOrigin = Point((0.0, 0.0, 0.0))
        if self.toLocalCrs:
            minx, miny, _, _ = self.inputGdf.total_bounds
            newOrigin = Point((minx, miny, 0.0))

        mapOfNodes = {}
        mapOfEdges = {}
        arrayOfLineLoops = []
        arrayOfPlaneSurfaces = []

        for _, row in self.inputGdf.iterrows():
            geom = row.geometry
            if GeomLib.isMultipart(geom):
                for g in geom.geoms:
                    self.__dumpPolygon(g, mapOfNodes, mapOfEdges, arrayOfLineLoops, arrayOfPlaneSurfaces)
            else:
                self.__dumpPolygon(geom, mapOfNodes, mapOfEdges, arrayOfLineLoops, arrayOfPlaneSurfaces)
 
        with open(self.outputFile, 'w') as output: 
            self.__dumpNodes(output, mapOfNodes, newOrigin)
            self.__dumpEdges(output, mapOfEdges, mapOfNodes)
            self.__dumpLineLoops(output, arrayOfLineLoops)
            self.__dumpPlaneSurfaces(output, arrayOfPlaneSurfaces)

    def __dumpPolygon(self, polygon, mapOfNodes, mapOfEdges, arrayOfLineLoops, arrayOfPlaneSurfaces):
        tmp = list()
        tmp.append(self.__fulfillWith(mapOfNodes, mapOfEdges, arrayOfLineLoops, polygon.exterior))
        for hole in polygon.interiors:
            tmp.append(self.__fulfillWith(mapOfNodes, mapOfEdges, arrayOfLineLoops, hole))
        arrayOfPlaneSurfaces.append(tmp)
        
    def __fulfillWith(self, mapOfNodes, mapOfEdges, arrayOfLineLoops, ring):
        nodes, tmp = list(ring.coords)[:-1], list()

        prev = MyNode(nodes[-1])
        for curr in nodes:
            curr = MyNode(curr)
            if curr not in mapOfNodes:
                mapOfNodes[curr] = 1 + len(mapOfNodes)

            myEdge = MyEdge(prev, curr)
            if myEdge not in mapOfEdges:
                mapOfEdges[myEdge] = 1 + len(mapOfEdges)
            myEdgeIdx = mapOfEdges[myEdge]

            if myEdge.startNode.__eq__(prev):
                tmp.append(myEdgeIdx)
            else:
                tmp.append(-myEdgeIdx)

            prev = curr

        arrayOfLineLoops.append(tmp)
        return len(arrayOfLineLoops)

    def __dumpCoords(self, node, newOrigin):
        return '%.2f, %.2f, %.2f' % (node.x - newOrigin.x, node.y - newOrigin.y, node.z - newOrigin.z)

    def __dumpNodes(self, output, mapOfNodes, newOrigin):
        output.write('lc = %g;\n' % self.lc)
        output.write('\n// =====> %d POINT(S)\n' % len(mapOfNodes))

        # for key, value in sorted(mapOfNodes.iteritems(), key=lambda(k, v): (v)):
        for key, value in sorted(list(mapOfNodes.items()), key=lambda kv: kv[1]):
            output.write('Point(%d) = {%s, lc};\n' % (value, self.__dumpCoords(key, newOrigin)))

    def __dumpEdges(self, output, mapOfEdges, mapOfNodes):
        output.write('\n// =====> %d LINE(S)\n' % len(mapOfEdges))
        # for key, value in sorted(mapOfEdges.iteritems(), key=lambda(k, v): v):
        for key, value in sorted(list(mapOfEdges.items()), key=lambda kv: kv[1]):
            output.write('Line(%d) = {%d, %d};\n' % (value, mapOfNodes[key.startNode], mapOfNodes[key.endNode]))

    def __dumpLineLoops(self, output, arrayOfLineLoops):
        output.write('\n// =====> %d LINE LOOP(S)\n' % len(arrayOfLineLoops))
        for i in range(len(arrayOfLineLoops)):
            output.write('Line Loop(%d) = {%s};\n' % (i + 1, ', '.join([str(x) for x in arrayOfLineLoops[i]])))

    def __dumpPlaneSurfaces(self, output, arrayOfPlaneSurfaces):
        output.write('\n// =====> %d PLANE SURFACE(S)\n' % len(arrayOfPlaneSurfaces))
        for i in range(len(arrayOfPlaneSurfaces)):
            output.write('Plane Surface(%d) = {%s};\n' % (i + 1, ', '.join([str(x) for x in arrayOfPlaneSurfaces[i]])))
