'''
Created on 16 dec. 2020

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
from shapely.geometry import LineString, MultiLineString
from shapely.geometry import Point
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.AbstractUrbanGraphLib import AbstractUrbanGraphLib

import networkx as nx


class MCALib(object):
    '''
    classdocs
    '''

    def __init__(self, roads, roi=None):
        '''
        Constructor
        '''
        if not isinstance(roads, GeoDataFrame):
            raise IllegalArgumentTypeException(roads, 'GeoDataFrame')

        if roi is None:
            _roads = roads
            geometries = [geom for geom in roads.geometry]
        else:
            ids = roads.sindex.intersection(roi)
            geometries = [roads.loc[_id].geometry for _id in ids]
            _roads = GeoDataFrame([{'geometry': geom} for geom in geometries], crs=roads.crs)

        self.roads = _roads
        self.graph, self.icVertices = MCALib.__buildGraph(geometries)

    @staticmethod
    def __addCoupleOfVertices(graph, first, last, linestring):
        graph.add_edge(first, last, object={
            'geometry': linestring, 'weight':linestring.length})

    @staticmethod
    def __addEdge(graph, ciVertices, icVertices, linestring):
        multigraph = 0
        coords = linestring.coords
        if (2 <= len(coords)):
            first = AbstractUrbanGraphLib.addVertex(ciVertices, icVertices, coords[0])
            last = AbstractUrbanGraphLib.addVertex(ciVertices, icVertices, coords[-1])

            if (first in graph) and (last in graph[first]):
                multigraph = 1
                # Handle multigraph (two vertices may be connected by more than one edge)
                newEdges = GeomLib.cutsLineStringByCurvilinearDistance(linestring, linestring.length / 2.0)
                for _edge in newEdges:
                    MCALib.__addEdge(graph, ciVertices, icVertices, _edge)
            else:
                MCALib.__addCoupleOfVertices(graph, first, last, linestring)
                MCALib.__addCoupleOfVertices(graph, last, first, LineString(reversed(coords)))
        return multigraph

    @staticmethod
    def __buildGraph(geometries):
        graph = nx.DiGraph()
        ciVertices = dict()
        icVertices = dict()

        multigraph = 0
        for geom in geometries:
            if isinstance(geom, MultiLineString):
                for _geom in geom.geoms:
                    multigraph += MCALib.__addEdge(graph, ciVertices, icVertices, _geom)
            elif isinstance(geom, LineString):
                multigraph += MCALib.__addEdge(graph, ciVertices, icVertices, geom)
            # else:
                # raise IllegalArgumentTypeException(geom, 'LineString or MultiLineString')

        if 0 < multigraph:
            print('Handling of %d multigraph cases!' % multigraph)

        return graph, icVertices

    def __fromGraphToGeoDataFrame(self, centralities, label):
        rows = []
        for nodeIndex, centrality in centralities.items():
            rows.append({
                'geometry': Point((self.icVertices[nodeIndex])),
                label: centrality
                })
        return GeoDataFrame(rows, crs=self.roads.crs)

    def betweenness_centrality(self):
        centralities = nx.betweenness_centrality(self.graph, weight='weight')
        return self.__fromGraphToGeoDataFrame(centralities, 'betweenness')

    def closeness_centrality(self):
        centralities = nx.closeness_centrality(self.graph, distance='weight')
        return self.__fromGraphToGeoDataFrame(centralities, 'closeness')

    def degree_centrality(self):
        centralities = nx.degree_centrality(self.graph)
        return self.__fromGraphToGeoDataFrame(centralities, 'degree_c')
