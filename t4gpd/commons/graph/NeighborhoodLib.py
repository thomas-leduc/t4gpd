'''
Created on 22 nov. 2020

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
from geopandas import GeoDataFrame
from shapely import line_interpolate_point, LineString, Point, union_all
from t4gpd.commons.ArrayCoding import ArrayCoding
from t4gpd.commons.graph.UrbanGraphFactory import UrbanGraphFactory


class NeighborhoodLib(object):
    '''
    classdocs
    '''
    @staticmethod
    def hash_edge(id1, id2):
        str_hash = ArrayCoding.encode([int(min(id1, id2)), int(max(id1, id2))])
        return str_hash

    @staticmethod
    def neighborhood(roads, fromPoint, maxDist):
        # WRONG IDEA:
        # roi = fromPoint.buffer(maxDist, cap_style=CAP_STYLE.round)
        # roi = GeoDataFrame([{"geometry": roi}], crs=roads.crs)
        # ug = UrbanGraphFactory.create(roads, method="networkx", roi=roi)
        ug = UrbanGraphFactory.create(roads, method="networkx")
        sourceIdx = ug._add_new_point(fromPoint)

        # Identification of full edges and vertices in the neighborhood
        burned_vertices, burned_edges = {sourceIdx: maxDist}, {}
        for vtxIdx, vtxGeom in ug.icVertices.items():
            geom = Point(vtxGeom)
            if (maxDist >= fromPoint.distance(geom)):
                path = ug.shortest_path(fromPoint, geom)
                if (0 < len(path)):
                    pathVertices = ArrayCoding.decode(path.path.squeeze())
                    pathLen = path.geometry.squeeze().length

                    if (maxDist >= pathLen):
                        burned_vertices[vtxIdx] = maxDist - pathLen
                        for i in range(1, len(pathVertices)):
                            burned_edges[NeighborhoodLib.hash_edge(
                                pathVertices[i-1], pathVertices[i]
                            )] = True

        rows = []
        for str_hash in burned_edges.keys():
            id1, id2 = ArrayCoding.decode(str_hash, outputType=int)
            rows.append(LineString([ug.icVertices[id1], ug.icVertices[id2]]))

        # Identification of remaining edges in the neighborhood
        for id1, remaining_dist in burned_vertices.items():
            for id2 in ug.nx_graph.adj[id1].keys():
                str_hash = NeighborhoodLib.hash_edge(id1, id2)
                if not str_hash in burned_edges:
                    ls = LineString([ug.icVertices[id1], ug.icVertices[id2]])
                    rp = line_interpolate_point(ls, remaining_dist)
                    ls = LineString([ug.icVertices[id1], rp])
                    rows.append(ls)

        return GeoDataFrame([{"geometry": union_all(rows)}], crs=roads.crs)
