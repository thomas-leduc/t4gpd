'''
Created on 21 nov. 2020

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
import copy

from dijkstar.graph import Graph
from geopandas.geodataframe import GeoDataFrame
from shapely.geometry import LineString, MultiLineString
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class AbstractUrbanGraphLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def addCoupleOfVertices(graph, edges, first, last, linestring):
        linestringLength = linestring.length

        graph.add_edge(first, last, (linestringLength, linestring.wkt))

        edgeItem = { 'geometry': linestring, 'length': linestringLength }
        if first in edges:
            if last in edges[first]:
                raise Exception('Unreachable instruction!')
            else:
                edges[first][last] = edgeItem
        else:
            edges[first] = dict({ last: edgeItem })

    @staticmethod
    def addEdge(graph, ciVertices, icVertices, edges, linestring):
        coords = linestring.coords
        if (2 <= len(coords)):
            first = AbstractUrbanGraphLib.addVertex(ciVertices, icVertices, coords[0])
            last = AbstractUrbanGraphLib.addVertex(ciVertices, icVertices, coords[-1])

            if (first in edges) and (first == last):
                print('This is a multigraph (loop)!')
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges1 = GeomLib.cutsLineStringByCurvilinearDistance(linestring, linestring.length / 3.0)
                newEdges2 = GeomLib.cutsLineStringByCurvilinearDistance(linestring, 2.0 * linestring.length / 3.0)
                newEdges = newEdges1 + newEdges2[:-1]
                for _edge in newEdges:
                    AbstractUrbanGraphLib.addEdge(graph, ciVertices, icVertices, edges, _edge)

            elif (first in edges) and (last in edges[first]):
                print('This is a multigraph!')
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges = GeomLib.cutsLineStringByCurvilinearDistance(linestring, linestring.length / 2.0)
                for _edge in newEdges:
                    AbstractUrbanGraphLib.addEdge(graph, ciVertices, icVertices, edges, _edge)

            else:
                AbstractUrbanGraphLib.addCoupleOfVertices(graph, edges, first, last, linestring)
                AbstractUrbanGraphLib.addCoupleOfVertices(graph, edges, last, first, LineString(reversed(coords)))

    @staticmethod
    def addVertex(ciVertices, icVertices, coord):
        str_coord = AbstractUrbanGraphLib.hashCoord(coord)

        if not str_coord in ciVertices:
            nodeIndex = len(ciVertices)
            ciVertices[str_coord] = nodeIndex
            icVertices[nodeIndex] = coord
        else:
            nodeIndex = ciVertices[str_coord]

        return nodeIndex   

    @staticmethod
    def buildGraph(geometries):
        graph = Graph()
        ciVertices = dict()
        icVertices = dict()
        edges = dict()

        for geom in geometries:
            if isinstance(geom, MultiLineString):
                for _geom in geom.geoms:
                    AbstractUrbanGraphLib.addEdge(graph, ciVertices, icVertices, edges, _geom)
            elif isinstance(geom, LineString):
                AbstractUrbanGraphLib.addEdge(graph, ciVertices, icVertices, edges, geom)
            else:
                raise IllegalArgumentTypeException(geom, 'LineString or MultiLineString')

        return graph, ciVertices, icVertices, edges

    @staticmethod
    def cost_function(u, v, edge, prev_edge):
        length, _ = edge
        return length

    @staticmethod
    def hashCoord(coord):
        str_coord = ('%f_%f') % (coord[0], coord[1])
        return str_coord

    @staticmethod
    def initializeGraph(roads, roi=None):
        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, 'GeoDataFrame')

        if roi is None:
            _roads = roads
            geometries = [geom for geom in roads.geometry]
        else:
            ids = roads.sindex.intersection(roi)
            geometries = [roads.loc[_id].geometry for _id in ids]
            _roads = GeoDataFrame([{'geometry': geom} for geom in geometries], crs=roads.crs)

        graph, ciVertices, icVertices, edges = AbstractUrbanGraphLib.buildGraph(geometries)
        return _roads, graph, ciVertices, icVertices, edges

    @staticmethod
    def addEndPoint(roads, spatialIdx, graph, ciVertices, icVertices, edges, endPoint):
        buffDist = 40.0
        minDist, nearestPoint, nearestRow = GeomLib.getNearestFeature(
            roads, spatialIdx, endPoint, buffDist)
        nearestLine = nearestRow.geometry

        if (0 < minDist):
            AbstractUrbanGraphLib.addEdge(graph, ciVertices, icVertices, edges, LineString([nearestPoint, endPoint]))

        # Cuts the nearestLine in two
        newEdges = GeomLib.cutsLineStringByCurvilinearDistance(
            nearestLine, nearestLine.project(nearestPoint))
        for _edge in newEdges:
            AbstractUrbanGraphLib.addEdge(graph, ciVertices, icVertices, edges, _edge)

        return ciVertices[AbstractUrbanGraphLib.hashCoord([endPoint.x, endPoint.y])], nearestLine

    @staticmethod
    def backupUrbanGraph(graph, ciVertices, icVertices, edges):
        _graph = copy.deepcopy(graph)
        _ciVertices = copy.deepcopy(ciVertices) if ciVertices is not None else None 
        _icVertices = copy.deepcopy(icVertices) if icVertices is not None else None
        _edges = copy.deepcopy(edges) if edges is not None else None
        return _graph, _ciVertices, _icVertices, _edges
