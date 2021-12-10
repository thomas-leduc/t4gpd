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
        
        qgsVectorLayer.setCrs(QgsCoordinateReferenceSystem(gdf.crs.to_epsg()))
        qgsVectorLayer.commitChanges()
        qgsVectorLayer.updateExtents()
        return qgsVectorLayer

    def run(self):
        qgsVectorLayer = self.__fromGeoDataFrameToQgsVectorLayer(self.gdf, self.layername)
        QgsProject.instance().addMapLayer(qgsVectorLayer)
        return qgsVectorLayer

'''
from shapely.wkt import loads

from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.future.morph.geoProcesses.CrossroadRecognition import CrossroadRecognition
from t4gpd.future.STCrossroadsGeneration import STCrossroadsGeneration
from t4gpd.graph.STToRoadsSectionsNodes import STToRoadsSectionsNodes
from t4gpd.isovist.STIsovistField2D import STIsovistField2D
from t4gpd.morph.geoProcesses.AngularAbscissa import AngularAbscissa
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess
from t4gpd.pyqgis.AddMemoryLayer import AddMemoryLayer
from t4gpd.pyqgis.PdfMapWriter import PdfMapWriter
from t4gpd.pyqgis.SetSymbolLib import SetSymbolLib
from t4gpd.pyqgis.ShowFeatureCount import ShowFeatureCount

QgsProject.instance().clear()

t = GeoDataFrameDemos.ensaNantesTrees()
layer = AddMemoryLayer(t, 'trees').run()
SetSymbolLib.setHeatMap(layer)

b = GeoDataFrameDemos.ensaNantesBuildings()
layer = AddMemoryLayer(b, 'buildings').run()
SetSymbolLib.setFillSymbol(layer)
SetSymbolLib.setAlternateFillSymbol(layer)
SetSymbolLib.setAlternateFillSymbol2(layer)
SetSymbolLib.setAlternateFillSymbol3(layer)
SetSymbolLib.setSimpleOutlineFillSymbol(layer)

r = GeoDataFrameDemos.ensaNantesRoads()
layer = AddMemoryLayer(r, 'roads').run()
SetSymbolLib.setLineSymbol(layer)
SetSymbolLib.setArrowSymbol(layer)

n = STToRoadsSectionsNodes(r).run()
n = n[n.gid.isin([30, 77])]
layer = AddMemoryLayer(n, 'nodes').run()
# SetSymbolLib.setMarkerSymbol(layer)
# SetSymbolLib.setLabelSymbol(layer, 'gid')

isovRays, _ = STIsovistField2D(b, n, nRays=64, rayLength=100.0).run()
patterns = STCrossroadsGeneration(nbranchs=8, length=100.0, width=10.0,
    mirror=False, withBranchs=True, withSectors=True,
    crs='EPSG:2154', magnitude=2.5).run()
pattRays = STGeoProcess(AngularAbscissa(patterns, 'vpoint_x',
    'vpoint_y', nRays=64), patterns).run()

op = CrossroadRecognition('FWT', pattRays, 'gid', nRays=64, maxRayLength=100.0)
result = STGeoProcess(op, isovRays).run()
result.geometry = result.viewpoint.apply(lambda p: loads(p))

layer = AddMemoryLayer(result, 'result').run()
SetSymbolLib.setSvgSymbol(layer, 'recId_fwt', 'c:/Users/tleduc/t4gs/papers/2021_crossroads_patterns/dev/icons_08')
SetSymbolLib.setLabelSymbol(layer, 'gid')

ShowFeatureCount(['buildings', 'roads', 'nodes', 'trees', 'result']).run()
PdfMapWriter('123.pdf', layer.extent()).run()
'''
