'''
Created on 17 sept. 2021

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
from geopandas.geodataframe import GeoDataFrame
from numpy import ndarray
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from qgis.core import QgsRectangle, QgsVectorLayer
from qgis.utils import iface


class ZoomLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def setExtent(roi):
        if not isinstance(roi, QgsRectangle):
            if isinstance(roi, QgsVectorLayer):
                roi = roi.extent()
            elif isinstance(roi, GeoDataFrame):
                roi = QgsRectangle(*roi.total_bounds)
            elif GeomLib.isAShapelyGeometry(roi):
                roi = QgsRectangle(*roi.bounds)
            elif isinstance(roi, ndarray) and (4 == len(roi)):
                roi = QgsRectangle(*roi)
            else:
                raise IllegalArgumentTypeException(roi, 'QgsRectangle, QgsVectorLayer, GeoDataFrame or ndarray')

        iface.mapCanvas().setExtent(roi)
        iface.mapCanvas().refresh()
        return roi
