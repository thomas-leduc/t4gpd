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
from copy import deepcopy
from geopandas import GeoDataFrame, sjoin_nearest
from networkx import betweenness_centrality, closeness_centrality, degree_centrality, DiGraph, NetworkXNoPath, shortest_path, to_numpy_array
from scipy.sparse.csgraph import minimum_spanning_tree
from shapely import delaunay_triangles, LineString, MultiPoint, Point
from shapely.ops import nearest_points
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.graph.UrbanGraphVertex import UrbanGraphVertex


class UrbanGraph(object):
    '''
    classdocs
    '''

    def __init__(self, ciVertices=None, icVertices=None, edges=None,
                 nx_graph=None, dk_graph=None, gdfOfBipoints=None, crs=None):
        '''
        Constructor
        '''
        if not ((ciVertices is None) or (icVertices is None) or
                (nx_graph is None) or (gdfOfBipoints is None)):
            self.method = "networkx"

        elif not ((ciVertices is None) or (icVertices is None) or
                  (edges is None) or (dk_graph is None)):
            self.method = "dijkstar"

        elif not ((ciVertices is None) or (icVertices is None) or
                  (edges is None)):
            self.method = None

        else:
            raise NotImplementedError(
                "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

        self.ciVertices = ciVertices
        self.icVertices = icVertices
        self.edges = edges
        self.nx_graph = nx_graph
        self.dk_graph = dk_graph
        self.gdfOfBipoints = gdfOfBipoints
        self.crs = crs

    def __str__(self) -> str:
        if self.method is None:
            edges = ""
            for k1, v1 in self.edges.items():
                for k2, v2 in v1.items():
                    edges = f"{edges}\n{k1}->{k2}: {v2}"
            return f"""
{self.icVertices}
{edges}
"""

    def __get_next_vertex(self, prev, curr):
        succ = list(self.edges[curr])
        if 2 == len(succ):
            if (prev == succ[0]) and not (prev == succ[1]):
                return succ[1]
            elif (prev == succ[1]) and not (prev == succ[0]):
                return succ[0]
        return None

    def __burn_edge(self, idx1, idx2, burnedEdges):
        minIdx = min(idx1, idx2)
        maxidx = max(idx1, idx2)
        if minIdx in burnedEdges:
            burnedEdges[minIdx].add(maxidx)
        else:
            burnedEdges[minIdx] = set({maxidx})

    def __build_road_section(self, vertexIndex, nextVertexIndex, burnedEdges):
        result = []

        prevIdx = vertexIndex
        result.append(self.icVertices[prevIdx])
        currIdx = nextVertexIndex
        result.append(self.icVertices[currIdx])
        self.__burn_edge(prevIdx, currIdx, burnedEdges)

        nextIdx = self.__get_next_vertex(prevIdx, currIdx)
        while nextIdx is not None:
            result.append(self.icVertices[nextIdx])
            prevIdx = currIdx
            currIdx = nextIdx
            self.__burn_edge(prevIdx, currIdx, burnedEdges)

            if (nextIdx == vertexIndex):
                # current road section is a loop, stop the process
                nextIdx = None
            else:
                nextIdx = self.__get_next_vertex(prevIdx, currIdx)

        return LineString(result)

    def getUniqueRoadsSections(self):
        if (self.method in [None, "dijkstar"]):
            rows = []
            burnedEdges = dict()
            for vertexIndex in list(self.edges.keys()):
                nbConnectedVertices = len(self.edges[vertexIndex])
                if (2 != nbConnectedVertices):
                    # current vertex is a "boundary" of a "road section"
                    for nextVertexIndex in self.edges[vertexIndex]:
                        minIdx = min(vertexIndex, nextVertexIndex)
                        maxIdx = max(vertexIndex, nextVertexIndex)
                        if not (minIdx in burnedEdges and (maxIdx in burnedEdges[minIdx])):
                            geom = self.__build_road_section(
                                vertexIndex, nextVertexIndex, burnedEdges)
                            rows.append({
                                "geometry": geom,
                                "gid": len(rows),
                                "distance": geom.length
                            })
            return GeoDataFrame(rows, crs=self.crs)
        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

    def getUniqueRoadsSectionsNodes(self):
        if (self.method in [None, "dijkstar"]):
            rows = []
            for k, v in self.edges.items():
                nbConnectedVertices = len(v)
                if (2 != nbConnectedVertices):
                    rows.append({
                        "gid": k,
                        "valency": nbConnectedVertices,
                        # "nb_connections": nbConnectedVertices,
                        "geometry": Point(self.icVertices[k]),
                    })
            return GeoDataFrame(rows, crs=self.crs)
        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

    def getUniqueRoadsSectionsWithoutCulDeSac(self):
        rs = self.getUniqueRoadsSections()
        rows = []
        for _, row in rs.iterrows():
            _coords = list(row["geometry"].coords)
            startHash = UrbanGraphVertex.hash_coord(_coords[0])
            stopHash = UrbanGraphVertex.hash_coord(_coords[-1])
            if ((1 < len(self.edges[self.ciVertices[startHash]])) and
                    (1 < len(self.edges[self.ciVertices[stopHash]]))):
                rows.append(row)
        return GeoDataFrame(rows, crs=self.crs)

    def __fromGraphToGeoDataFrame1(self, nx_graph, centralities, label):
        rows = []
        for nodeIndex, centrality in centralities.items():
            rows.append({
                "gid": nodeIndex,
                "valency": len(nx_graph.adj[nodeIndex]),
                label: centrality,
                "geometry": Point((self.icVertices[nodeIndex])),
            })
        return GeoDataFrame(rows, crs=self.crs)

    def betweenness_centrality(self):
        if ("networkx" == self.method):
            centralities = betweenness_centrality(
                self.nx_graph, weight="weight")
            return self.__fromGraphToGeoDataFrame1(self.nx_graph, centralities, "betweenness")
        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

    def closeness_centrality(self):
        if ("networkx" == self.method):
            centralities = closeness_centrality(
                self.nx_graph, distance="weight")
            return self.__fromGraphToGeoDataFrame1(self.nx_graph, centralities, "closeness")
        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

    def degree_centrality(self):
        if ("networkx" == self.method):
            centralities = degree_centrality(self.nx_graph)
            return self.__fromGraphToGeoDataFrame1(self.nx_graph, centralities, "degree_c")
        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

    def __fromGraphToGeoDataFrame2(self, nx_graph):
        rows = []
        for nodeIndex1, v1 in nx_graph.adj.items():
            for nodeIndex2, v2 in v1.items():
                rows.append({
                    "from": nodeIndex1,
                    "to": nodeIndex2,
                    "weight": v2["weight"],
                    "geometry": LineString([self.icVertices[nodeIndex1], self.icVertices[nodeIndex2]]),
                })
        return GeoDataFrame(rows, crs=self.crs)

    def minimum_spanning_tree(self):
        if ("networkx" == self.method):
            matrix = to_numpy_array(self.nx_graph)
            mst = minimum_spanning_tree(matrix)
            mst = DiGraph(mst.toarray())
            return self.__fromGraphToGeoDataFrame2(mst)
        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

    def delaunay_triangulation(self):
        if (self.method in [None, "dijkstar"]):
            mpt = MultiPoint(list(self.icVertices.values()))
            tins = delaunay_triangles(mpt, tolerance=0, only_edges=True)
            rows = []
            for gid, linestring in enumerate(tins.geoms, start=1):
                rows.append({
                    "gid": gid,
                    "geometry": linestring,
                })
            return GeoDataFrame(rows, crs=self.crs)
        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")

    def __spaths_to_lineString(self, spaths):
        if 2 <= len(spaths):
            return LineString([
                self.icVertices[nodeIndex] for nodeIndex in spaths
            ])
        return None

    def __fromGraphToGeoDataFrame3(self, spaths, source, target):
        rows = []

        if (source is None) and (target is None):
            raise NotImplementedError("")

        elif (source is None) or (target is None):
            for spath in spaths.values():
                ls = self.__spaths_to_lineString(spath)
                if not ls is None:
                    rows.append({
                        "fromPoint": Point(self.icVertices[spath[0]]).wkt,
                        "toPoint": Point(self.icVertices[spath[-1]]).wkt,
                        "path": ArrayCoding.encode(spath),
                        "pathLen": ls.length,
                        "geometry": ls
                    })
        else:
            ls = self.__spaths_to_lineString(spaths)
            if not ls is None:
                rows.append({
                    "fromPoint": Point(self.icVertices[spaths[0]]).wkt,
                    "toPoint": Point(self.icVertices[spaths[-1]]).wkt,
                    "path": ArrayCoding.encode(spaths),
                    "pathLen": ls.length,
                    "geometry": ls
                })

        return GeoDataFrame(rows, crs=self.crs)

    def __add_two_new_edges(self, id1, id2):
        ls = LineString([self.icVertices[id1][0:2], self.icVertices[id2][0:2]])
        self.nx_graph.add_edge(id1, id2, weight=ls.length, object={
            "geometry": ls, "weight": ls.length})

        ls = LineString([self.icVertices[id2][0:2], self.icVertices[id1][0:2]])
        self.nx_graph.add_edge(id2, id1, weight=ls.length, object={
            "geometry": ls, "weight": ls.length})

    def _add_new_point(self, pt):
        if pt is None:
            return None
        if not isinstance(pt, Point):
            raise IllegalArgumentTypeException(pt, "Point or None")
        str_coord = UrbanGraphVertex.hash_coord(pt.coords[0])
        if str_coord in self.ciVertices:
            return self.ciVertices[str_coord]

        tmp = sjoin_nearest(GeoDataFrame([{"geometry": pt}], crs=self.crs),
                            self.gdfOfBipoints)

        if (0 < len(tmp)):
            # CAUTION WITH THE 2 FOLLOWING iat[]
            bipoint = self.gdfOfBipoints.iat[tmp.iat[0, 1], 1]
            _, rp = nearest_points(pt, bipoint)
            id1 = UrbanGraphVertex.add_vertex(
                self.ciVertices, self.icVertices, pt.coords[0])
            id2 = UrbanGraphVertex.add_vertex(
                self.ciVertices, self.icVertices, rp.coords[0])
            id3 = self.ciVertices[UrbanGraphVertex.hash_coord(
                bipoint.coords[0])]
            id4 = self.ciVertices[UrbanGraphVertex.hash_coord(
                bipoint.coords[-1])]
            self.__add_two_new_edges(id1, id2)
            self.__add_two_new_edges(id2, id3)
            self.__add_two_new_edges(id2, id4)

            return id1
        raise Exception("Unreachable instruction!")

    def shortest_path(self, sourcePt=None, targetPt=None):
        if ("networkx" == self.method):
            if not ((sourcePt is None) or (isinstance(sourcePt, Point))):
                raise IllegalArgumentTypeException(sourcePt, "Point or None")
            if not ((targetPt is None) or (isinstance(targetPt, Point))):
                raise IllegalArgumentTypeException(targetPt, "Point or None")
            if (sourcePt == targetPt):
                return GeoDataFrame([])

            ugClone = UrbanGraph(
                ciVertices=deepcopy(self.ciVertices),
                icVertices=deepcopy(self.icVertices),
                nx_graph=deepcopy(self.nx_graph),
                gdfOfBipoints=self.gdfOfBipoints.copy(deep=True),
                crs=self.crs)
            sourceIdx = ugClone._add_new_point(sourcePt)
            targetIdx = ugClone._add_new_point(targetPt)

            try:
                sp = shortest_path(ugClone.nx_graph, source=sourceIdx,
                                   target=targetIdx, weight="weight",
                                   method="dijkstra")
            except NetworkXNoPath as error:
                print(error)
                return GeoDataFrame()

            return ugClone.__fromGraphToGeoDataFrame3(sp, sourceIdx, targetIdx)

        raise NotImplementedError(
            "Bad invocation of the UrbanGraph constructor, use UrbanGraphFactory.create(...)")
