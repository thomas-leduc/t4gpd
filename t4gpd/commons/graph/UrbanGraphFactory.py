'''
Created on 25 oct 2023

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
from dijkstar.graph import Graph
from geopandas import GeoDataFrame, overlay
from networkx import DiGraph
from shapely import LineString, union_all
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.UrbanGraph import UrbanGraph
from t4gpd.commons.graph.UrbanGraphVertex import UrbanGraphVertex
from warnings import warn


class UrbanGraphFactory(object):
    '''
    classdocs
    '''

    @staticmethod
    def create(roads, method=None):
        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, "GeoDataFrame")

        geometryCollection = union_all(roads.geometry)
        listOfBipoints = GeomLib.toListOfBipointsAsLineStrings(
            geometryCollection)
        listOfBipoints = [GeomLib.removeZCoordinate(
            bp) for bp in listOfBipoints]

        if method is None:
            ciVertices, icVertices, edges = UrbanGraphFactory.__M1_build_graph(
                listOfBipoints)
            return UrbanGraph(ciVertices=ciVertices, icVertices=icVertices,
                              edges=edges, crs=roads.crs)

        elif ("networkx" == method):
            # USEFUL FOR CALCULATING MULTI-CENTRALITIES, MST
            gdfOfBipoints = GeoDataFrame(
                {"gid": range(len(listOfBipoints)), "geometry": listOfBipoints}, crs=roads.crs)
            ciVertices, icVertices, nx_graph = UrbanGraphFactory.__M2_build_graph(
                listOfBipoints)
            return UrbanGraph(ciVertices=ciVertices, icVertices=icVertices,
                              nx_graph=nx_graph, gdfOfBipoints=gdfOfBipoints,
                              crs=roads.crs)

        elif ("dijkstar" == method):
            ciVertices, icVertices, edges, dk_graph = UrbanGraphFactory.__M3_build_graph(
                listOfBipoints)
            return UrbanGraph(ciVertices=ciVertices, icVertices=icVertices,
                              edges=edges, dk_graph=dk_graph, crs=roads.crs)

        raise IllegalArgumentTypeException(
            method, "None, 'networkx' or 'dijkstar'")

    @ staticmethod
    def __M1_build_graph(listOfBipoints):
        ciVertices = dict()
        icVertices = dict()
        edges = dict()

        for linestring in listOfBipoints:
            UrbanGraphFactory.__M1_add_linestring(
                ciVertices, icVertices, edges, linestring)

        return ciVertices, icVertices, edges

    @ staticmethod
    def __M1_add_linestring(ciVertices, icVertices, edges, linestring):
        coords = linestring.coords
        if (2 <= len(coords)):
            first = UrbanGraphVertex.add_vertex(
                ciVertices, icVertices, coords[0])
            last = UrbanGraphVertex.add_vertex(
                ciVertices, icVertices, coords[-1])

            if (first in edges) and (first == last):
                warn("This is a multigraph (loop)!")
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges1 = GeomLib.cutsLineStringByCurvilinearDistance(
                    linestring, linestring.length / 3.0)
                newEdges2 = GeomLib.cutsLineStringByCurvilinearDistance(
                    linestring, 2.0 * linestring.length / 3.0)
                newEdges = newEdges1 + newEdges2[:-1]
                for _edge in newEdges:
                    UrbanGraphFactory.__M1_add_linestring(
                        ciVertices, icVertices, edges, _edge)

            elif (first in edges) and (last in edges[first]):
                warn("This is a multigraph!")
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges = GeomLib.cutsLineStringByCurvilinearDistance(
                    linestring, linestring.length / 2.0)
                for _edge in newEdges:
                    UrbanGraphFactory.__M1_add_linestring(
                        ciVertices, icVertices, edges, _edge)

            else:
                UrbanGraphFactory.__M1_add_pair_or_vertices(
                    edges, first, last, linestring)
                UrbanGraphFactory.__M1_add_pair_or_vertices(
                    edges, last, first, LineString(reversed(coords)))

    @staticmethod
    def __M1_add_pair_or_vertices(edges, first, last, linestring):
        linestringLength = linestring.length

        edgeItem = {"geometry": linestring, "length": linestringLength}
        if first in edges:
            if last in edges[first]:
                raise Exception("Unreachable instruction!")
            else:
                edges[first][last] = edgeItem
        else:
            edges[first] = dict({last: edgeItem})
        pass

    @staticmethod
    def __M2_build_graph(listOfBipoints):
        ciVertices = dict()
        icVertices = dict()
        nx_graph = DiGraph()

        multigraph = 0
        for linestring in listOfBipoints:
            multigraph += UrbanGraphFactory.__M2_add_linestring(
                ciVertices, icVertices, nx_graph, linestring)

        if 0 < multigraph:
            warn(f"Handle {multigraph} multigraphs!")

        return ciVertices, icVertices, nx_graph

    @staticmethod
    def __M2_add_linestring(ciVertices, icVertices, nx_graph, linestring):
        multigraph = 0
        coords = linestring.coords
        if (2 <= len(coords)):
            first = UrbanGraphVertex.add_vertex(
                ciVertices, icVertices, coords[0])
            last = UrbanGraphVertex.add_vertex(
                ciVertices, icVertices, coords[-1])

            if (first in nx_graph) and (last in nx_graph[first]):
                multigraph = 1
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges = GeomLib.cutsLineStringByCurvilinearDistance(
                    linestring, linestring.length / 2.0)
                for _edge in newEdges:
                    UrbanGraphFactory.__M2_add_linestring(
                        ciVertices, icVertices, nx_graph, _edge)
            else:
                UrbanGraphFactory.__M2_add_pair_or_vertices(
                    nx_graph, first, last, linestring)
                UrbanGraphFactory.__M2_add_pair_or_vertices(
                    nx_graph, last, first, LineString(reversed(coords)))
        return multigraph

    @staticmethod
    def __M2_add_pair_or_vertices(nx_graph, first, last, linestring):
        nx_graph.add_edge(first, last, weight=linestring.length, object={
            "geometry": linestring, "weight": linestring.length})

    @staticmethod
    def __M3_build_graph(listOfBipoints):
        ciVertices = dict()
        icVertices = dict()
        edges = dict()
        dk_graph = Graph()

        for linestring in listOfBipoints:
            UrbanGraphFactory.__M3_add_linestring(
                ciVertices, icVertices, edges, dk_graph, linestring)

        return ciVertices, icVertices, edges, dk_graph

    @staticmethod
    def __M3_add_linestring(ciVertices, icVertices, edges, dk_graph,  linestring):
        coords = linestring.coords
        if (2 <= len(coords)):
            first = UrbanGraphVertex.add_vertex(
                ciVertices, icVertices, coords[0])
            last = UrbanGraphVertex.add_vertex(
                ciVertices, icVertices, coords[-1])

            if (first in edges) and (first == last):
                warn("This is a multigraph (loop)!")
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges1 = GeomLib.cutsLineStringByCurvilinearDistance(
                    linestring, linestring.length / 3.0)
                newEdges2 = GeomLib.cutsLineStringByCurvilinearDistance(
                    linestring, 2.0 * linestring.length / 3.0)
                newEdges = newEdges1 + newEdges2[:-1]
                for _edge in newEdges:
                    UrbanGraphFactory.__M3_add_linestring(
                        ciVertices, icVertices, edges, dk_graph, _edge)

            elif (first in edges) and (last in edges[first]):
                warn("This is a multigraph!")
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges = GeomLib.cutsLineStringByCurvilinearDistance(
                    linestring, linestring.length / 2.0)
                for _edge in newEdges:
                    UrbanGraphFactory.__M3_add_linestring(
                        ciVertices, icVertices, edges, dk_graph, _edge)

            else:
                UrbanGraphFactory.__M3_add_pair_or_vertices(
                    edges, dk_graph, first, last, linestring)
                UrbanGraphFactory.__M3_add_pair_or_vertices(
                    edges, dk_graph, last, first, LineString(reversed(coords)))

    @staticmethod
    def __M3_add_pair_or_vertices(edges, dk_graph, first, last, linestring):
        linestringLength = linestring.length

        dk_graph.add_edge(first, last, (linestringLength, linestring.wkt))

        edgeItem = {"geometry": linestring, "length": linestringLength}
        if first in edges:
            if last in edges[first]:
                raise Exception("Unreachable instruction!")
            else:
                edges[first][last] = edgeItem
        else:
            edges[first] = dict({last: edgeItem})
