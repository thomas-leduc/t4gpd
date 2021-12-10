'''
Created on 10 sept. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
from t4gpd.commons.GeoProcess import GeoProcess

from qgis.core import QgsLayerTreeLayer, QgsProject


class ShowFeatureCount(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, layerNames):
        '''
        Constructor
        '''
        self.layerNames = layerNames

    def run(self):
        root = QgsProject.instance().layerTreeRoot()
        for child in root.children():
            if isinstance(child, QgsLayerTreeLayer):
                if child.name() in self.layerNames:
                    child.setCustomProperty("showFeatureCount", True)
