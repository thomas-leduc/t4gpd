'''
Created on 31 janv. 2022

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
import numbers

from geopandas import GeoDataFrame
from shapely.affinity import rotate
from shapely.geometry import Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

import matplotlib.pyplot as plt
from t4gpd.morph.STCrossroadsGeneration import STCrossroadsGeneration


class MultipleMarkerStyles(GeoProcess):
    '''
    classdocs
    '''
    MPATH = '__mpath__'

    def __init__(self, nodes, patterns=None, left_on='recId_fwt', right_on='gid',
                 rotation=None, basemap=None, marker_color='black', marker_size=2000,
                 alpha=None, nbranchs=8):
        '''
        Constructor
        '''
        if not isinstance(nodes, GeoDataFrame):
            raise IllegalArgumentTypeException(nodes, 'GeoDataFrame')
        if left_on not in nodes:
            raise IllegalArgumentTypeException(left_on, 'is not a valid field name')
        self.left_on = left_on

        if patterns is None:
            _patterns = STCrossroadsGeneration(nbranchs, length=100.0, width=10.0,
                                               mirror=False, withBranchs=True, withSectors=True,
                                               crs='epsg:2154', magnitude=0).run()
        else:
            if not isinstance(patterns, GeoDataFrame):
                raise IllegalArgumentTypeException(patterns, 'GeoDataFrame')
            _patterns = patterns.copy()
        if right_on not in _patterns:
            raise IllegalArgumentTypeException(right_on, 'is not a valid field name')

        if isinstance(rotation, numbers.Number):
            _patterns[MultipleMarkerStyles.MPATH] = _patterns.geometry.apply(
                lambda g: rotate(g, rotation, origin='center').exterior.coords)
            self.rotation = None
        else:
            _patterns[MultipleMarkerStyles.MPATH] = _patterns.geometry.apply(
                lambda g: g.exterior.coords)
            if isinstance(rotation, str) and (rotation not in nodes):
                raise IllegalArgumentTypeException(rotation, 'is not a valid field name')
            self.rotation = rotation
        self.mapOfPatterns = _patterns[[right_on, MultipleMarkerStyles.MPATH]].set_index(right_on).to_dict('index')

        self.nodes = nodes.copy()
        self.nodes = self.nodes.merge(_patterns[[right_on, MultipleMarkerStyles.MPATH]], how='left',
                                      left_on=left_on, right_on=right_on)

        self.basemap = plt if basemap is None else basemap
        self.marker_color = marker_color
        self.marker_size = marker_size
        self.alpha = alpha

    def run(self):
        if self.rotation is None:
            for _pattId in self.mapOfPatterns.keys():
                _nodes = self.nodes[ self.nodes[self.left_on] == _pattId ]
                _mpath = self.mapOfPatterns[_pattId][MultipleMarkerStyles.MPATH]
                self.basemap.scatter(_nodes.centroid.x, _nodes.centroid.y,
                                     c=self.marker_color, s=self.marker_size,
                                     alpha=self.alpha, marker=_mpath)
        else:
            for _pattId in self.mapOfPatterns.keys():
                _mpath = Polygon(self.mapOfPatterns[_pattId][MultipleMarkerStyles.MPATH])
                _nodes = self.nodes[ self.nodes[self.left_on] == _pattId ]
                for _, _row in _nodes.iterrows():
                    _rot, _geom = _row[self.rotation], _row.geometry.centroid
                    _curr_mpath = rotate(_mpath, 360 - _rot, origin='center').exterior.coords
                    self.basemap.scatter(_geom.x, _geom.y,
                                         c=self.marker_color, s=self.marker_size,
                                         alpha=self.alpha, marker=_curr_mpath)
