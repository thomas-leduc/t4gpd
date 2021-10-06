'''
Created on 11 juin 2020

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
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.grid.GridLib import GridLib


class STGrid(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, dx, dy=None, indoor=None, intoPoint=True, encode=True):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')

        self.inputGdf = inputGdf
        self.dx = dx
        self.dy = dy
        if indoor in [None, True, False, 'both']:
            self.indoor = indoor
        else:
            raise Exception('Illegal argument: indoor must be chosen in [None, True, False, "both"]!')
        self.intoPoint = intoPoint
        self.encode = encode

    def run(self):
        gridLib = GridLib(self.inputGdf, self.dx, self.dy, self.encode)

        if self.indoor is None:
            grid = gridLib.grid()
        elif ('both' == self.indoor):
            grid = gridLib.indoorOutdoorGrid()
        elif self.indoor:
            grid = gridLib.indoorGrid()
        else:
            grid = gridLib.outdoorGrid()

        if self.intoPoint:
            grid.geometry = grid.centroid
        return grid
