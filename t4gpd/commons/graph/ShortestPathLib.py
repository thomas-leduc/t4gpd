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
from dijkstar.algorithm import find_path, NoPathError
from shapely.geometry import MultiLineString
from shapely.wkt import loads

from t4gpd.commons.graph.AbstractUrbanGraphLib import AbstractUrbanGraphLib


class ShortestPathLib(AbstractUrbanGraphLib):
    '''
    classdocs
    '''

    def __init__(self, roads, roi=None):
        '''
        Constructor
        '''
        self.roads, self.graph, self.ciVertices, self.icVertices, self.edges = AbstractUrbanGraphLib.initializeGraph(roads, roi)
        self.spatialIdx = self.roads.sindex
        self.roi = roi

    def shortestPath(self, fromPoint, toPoint):
        # Backup the input graph
        _graph, _ciVertices, _icVertices, _edges = AbstractUrbanGraphLib.backupUrbanGraph(
            self.graph, self.ciVertices, self.icVertices, self.edges)

        if (fromPoint == toPoint):
            return MultiLineString([]), 0.0

        str_coord = AbstractUrbanGraphLib.hashCoord([fromPoint.x, fromPoint.y])
        if str_coord in self.ciVertices:
            fromIdx = self.ciVertices[str_coord]
        else:
            fromIdx, _ = AbstractUrbanGraphLib.addEndPoint(
                self.roads, self.spatialIdx, self.graph, self.ciVertices, self.icVertices, self.edges, fromPoint)

        str_coord = AbstractUrbanGraphLib.hashCoord([toPoint.x, toPoint.y])
        if str_coord in self.ciVertices:
            toIdx = self.ciVertices[str_coord]
        else:
            toIdx, _ = AbstractUrbanGraphLib.addEndPoint(
                self.roads, self.spatialIdx, self.graph, self.ciVertices, self.icVertices, self.edges, toPoint)

        try:
            tmp = find_path(self.graph, fromIdx, toIdx, cost_func=AbstractUrbanGraphLib.cost_function)
            pathGeom = MultiLineString([loads(wkt) for _, wkt in tmp.edges])
            pathLen = tmp.total_cost

        except NoPathError as error:
            pathGeom, pathLen = None, None
            print(error)

        finally:
            # Rollback to the input graph (must be executed under all circumstances)
            self.graph, self.ciVertices, self.icVertices, self.edges = _graph, _ciVertices, _icVertices, _edges

        return pathGeom, pathLen
