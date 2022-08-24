'''
Created on 9 sept. 2021

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
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

from qgis.PyQt.Qt import QVariant
from qgis.core import QgsCoordinateReferenceSystem, QgsFeature, QgsField, QgsGeometry, QgsProject, QgsVectorLayer


class AddMemoryLayer(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, gdf, layername):
        '''
        Constructor
        '''
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, 'GeoDataFrame')
        self.gdf = gdf

        if not isinstance(layername, str):
            raise IllegalArgumentTypeException(layername, 'str')
        self.layername = layername

    @staticmethod
    def __fromGeoDataFrameToQgsVectorLayer(gdf, layername):
        geomTypes = gdf.geom_type.unique()
        if (1 == len(geomTypes)):
            geomType = geomTypes[0]
        elif (2 == len(geomTypes)):
            geomType = geomTypes[0] if (str(geomTypes[0]).startswith('Multi')) else geomTypes[1]

        qgsVectorLayer = QgsVectorLayer(geomType, layername, 'memory')
        provider = qgsVectorLayer.dataProvider()
        qgsVectorLayer.startEditing()
        fieldnames, qgsFields = [], []
        for _fieldname, _fieldtype in gdf.dtypes.items():
            if not ('geometry' == str(_fieldtype)):
                _fieldtype = QVariant.String
                if (str(_fieldtype).startswith('int')):
                    _fieldtype = QVariant.Int
                elif (str(_fieldtype).startswith('float')):
                    _fieldtype = QVariant.Double
                elif (str(_fieldtype).startswith('datetime')):
                    _fieldtype = QVariant.DateTime
                fieldnames.append(_fieldname)
                qgsFields.append(QgsField(_fieldname, QVariant.String))
        provider.addAttributes(qgsFields)

        qgsFeatures = []
        for _, row in gdf.iterrows():
            qgsFeature = QgsFeature()
            qgsFeature.setGeometry(QgsGeometry.fromWkt(row.geometry.wkt))
            qgsFeature.setAttributes([row[_f] for _f in fieldnames])
            qgsFeatures.append(qgsFeature)
        provider.addFeatures(qgsFeatures)

        # qgsVectorLayer.setCrs(QgsCoordinateReferenceSystem(gdf.crs.to_epsg()))
        qgsVectorLayer.setCrs(QgsCoordinateReferenceSystem.fromEpsgId(gdf.crs.to_epsg()))
        qgsVectorLayer.commitChanges()
        qgsVectorLayer.updateExtents()
        return qgsVectorLayer

    def run(self):
        qgsVectorLayer = self.__fromGeoDataFrameToQgsVectorLayer(self.gdf, self.layername)
        QgsProject.instance().addMapLayer(qgsVectorLayer)
        return qgsVectorLayer
