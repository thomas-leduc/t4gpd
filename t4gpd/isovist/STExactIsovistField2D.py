'''
Created on 19 dec. 2021

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.isovist.ExactIsovistLib import ExactIsovistLib


class STExactIsovistField2D(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, viewpoints, rayLength=100.0, delta=10.0):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(
                buildings, 'buildings GeoDataFrame')
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(
                viewpoints, 'viewpoints GeoDataFrame')
        if not (buildings.crs == viewpoints.crs):
            raise Exception(
                'Illegal argument: buildings and viewpoints must share shames CRS!')

        self.buildings = buildings
        # CLEAN GEOMETRIES
        self.buildings.geometry = self.buildings.geometry.apply(
            lambda g: g.buffer(0))

        self.viewpoints = viewpoints
        self.rayLength = rayLength
        self.delta = delta

    def run(self):
        rows = []
        for _, row in self.viewpoints.iterrows():
            _vp = row.geometry.centroid
            # Update 21.08.2024
            _rayLength = row[self.rayLength] if (
                self.rayLength in self.viewpoints) else self.rayLength
            _isov = ExactIsovistLib.run(
                self.buildings, _vp, _rayLength, self.delta)

            del (_isov['nodes'])
            _isov['artif_hori'] = _isov['artif_hori'].wkt
            _isov['solid_surf'] = _isov['solid_surf'].wkt
            _isov['occlu_surf'] = _isov['occlu_surf'].wkt

            # Update 21.08.2024
            _newrow = dict(row)
            _newrow["viewpoint"] = _newrow["geometry"]
            _newrow.update(_isov)
            rows.append(_newrow)
            # rows.append(_isov)

        return GeoDataFrame(rows, crs=self.buildings.crs)
