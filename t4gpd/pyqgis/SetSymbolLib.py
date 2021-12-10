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
from qgis.core import (QgsArrowSymbolLayer, QgsCategorizedSymbolRenderer,
                       QgsFillSymbol, QgsHeatmapRenderer,
                       QgsLineSymbol, QgsMarkerSymbol,
                       QgsPalLayerSettings, QgsLinePatternFillSymbolLayer,
                       QgsPointPatternFillSymbolLayer, QgsProperty,
                       QgsRendererCategory, QgsSimpleFillSymbolLayer,
                       QgsSimpleLineSymbolLayer, QgsStyle,
                       QgsSvgMarkerSymbolLayer, QgsSymbol, QgsSymbolLayer,
                       QgsTextFormat, QgsVectorLayerSimpleLabeling)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface


class SetSymbolLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def __setSymbol(layer, symbol):
        if layer is not None:
            layer.renderer().setSymbol(symbol)
            iface.layerTreeView().refreshLayerSymbology(layer.id())
            layer.triggerRepaint()

    @staticmethod
    def __altSetSymbol(layer, symbol):
        if layer is not None:
            layer.renderer().symbol().changeSymbolLayer(0, symbol)
            iface.layerTreeView().refreshLayerSymbology(layer.id())
            layer.triggerRepaint()

    @staticmethod
    def __otherAltSetSymbol(layer, renderer):
        if layer is not None:
            layer.setRenderer(renderer)
            iface.layerTreeView().refreshLayerSymbology(layer.id())
            layer.triggerRepaint()

    @staticmethod
    def setAlternateFillSymbol(layer, color='black', patternDistance=1.0,
                               lineAngle=45, penstyle='solid', width='0.35'):
        lineSymbol = QgsLineSymbol.createSimple({
            'penstyle': penstyle, 'width': width, 'color': color})
        filled_pattern = QgsLinePatternFillSymbolLayer()
        filled_pattern.setLineAngle(lineAngle)
        filled_pattern.setDistance(patternDistance)
        filled_pattern.setSubSymbol(lineSymbol)
        SetSymbolLib.__altSetSymbol(layer, filled_pattern)

    @staticmethod
    def setAlternateFillSymbol2(layer, color='red', color_border='black',
                                name='diamond', size='3.0'):
        markerSymbol = QgsMarkerSymbol.createSimple({
            'color':color, 'color_border':color_border, 'name':name, 'size':size})
        filled_pattern = QgsPointPatternFillSymbolLayer()
        filled_pattern.setDistanceX(4.0)
        filled_pattern.setDistanceY(4.0)
        filled_pattern.setSubSymbol(markerSymbol)
        SetSymbolLib.__altSetSymbol(layer, filled_pattern)

    @staticmethod
    def setAlternateFillSymbol3(layer, color='black', style='b_diagonal'):
        # style = ['cross', 'b_diagonal', 'diagonal_x', 'f_diagonal', 
        # 'horizontal', 'solid', 'vertical']
        symbol_layer = QgsSimpleFillSymbolLayer.create({'color':color, 'style': style})
        SetSymbolLib.__altSetSymbol(layer, symbol_layer)

    @staticmethod
    def setArrowSymbol(layer, color='black', headType=QgsArrowSymbolLayer.HeadSingle,
                       width=0.60, headLength=2.05, headThickness=1.55,
                       arrowType=QgsArrowSymbolLayer.ArrowPlain):
        # headType = {QgsArrowSymbolLayer.HeadDouble, QgsArrowSymbolLayer.HeadReversed, QgsArrowSymbolLayer.HeadSingle}
        # arrowType = {QgsArrowSymbolLayer.ArrowPlain, QgsArrowSymbolLayer.ArrowLeftHalf, QgsArrowSymbolLayer.ArrowRightHalf}

        arrowSymbol = QgsArrowSymbolLayer()
        arrowSymbol.setColor(QColor(color))

        arrowSymbol.setArrowStartWidth(width)
        arrowSymbol.setArrowWidth(width)

        arrowSymbol.setArrowType(arrowType)

        arrowSymbol.setHeadType(headType)
        arrowSymbol.setHeadLength(headLength)
        arrowSymbol.setHeadThickness(headThickness)

        arrowSymbol.setIsCurved(False)
        arrowSymbol.setIsRepeated(True)

        SetSymbolLib.__altSetSymbol(layer, arrowSymbol)

    @staticmethod
    def setCategorizedSymbol(layer, fieldName, listOfValueColorLabels):
        '''
        listOfValueColorLabels = (
            ('cat', 'red'),
            ('dog', 'blue', 'Big dog'),
            ('sheep', 'green'),
            ('', 'yellow', 'Unknown')
        )
        '''
        # CREATE A CATEGORY FOR EACH ITEM IN 'fieldLookupTable'
        categories = []
        for item in listOfValueColorLabels:
            value, color, label = item if 3 == len(item) else [item[0], item[1], item[0]]
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setColor(QColor(color))
            categories.append(QgsRendererCategory(value, symbol, label))

        # CREATE THE RENDERER AND ASSIGN IT TO THE GIVEN LAYER
        renderer = QgsCategorizedSymbolRenderer(fieldName, categories)
        SetSymbolLib.__otherAltSetSymbol(layer, renderer)

    @staticmethod
    def setFillSymbol(layer, color='lightgrey', outline_color='darkgrey',
                      style_border='solid', width_border='0.75'):
        fillSymbol = QgsFillSymbol.createSimple({
            'color': color,
            'outline_color': outline_color,
            'width_border': width_border,
            'style_border' : style_border})
        SetSymbolLib.__setSymbol(layer, fillSymbol)

    @staticmethod
    def setHeatMap(layer, radius=20, rampName='Blues'):
        # To get a list of available color ramp names, use:
        # QgsStyle().defaultStyle().colorRampNames()
        ramp = QgsStyle().defaultStyle().colorRamp(rampName)
        heatmap = QgsHeatmapRenderer()
        heatmap.setRadius(radius)
        heatmap.setColorRamp(ramp)
        SetSymbolLib.__otherAltSetSymbol(layer, heatmap)

    @staticmethod
    def setLabelSymbol(layer, fieldName, overPoint=True, size='14',
                       color='black', positionX=None, positionY=None,
                       offsetX=None, offsetY=None):
        label = QgsPalLayerSettings()
        label.fieldName = fieldName
    
        textFormat = QgsTextFormat()
        # bgColor = QgsTextBackgroundSettings()
        # bgColor.setFillColor(QColor('white'))
        # bgColor.setEnabled(True)
        # textFormat.setBackground(bgColor )
        textFormat.setColor(QColor(color))
        textFormat.setSize(int(size))
        label.setFormat(textFormat)
        label.isExpression = True
    
        layer.setLabeling(QgsVectorLayerSimpleLabeling(label))
        layer.setLabelsEnabled(True)
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        layer.triggerRepaint()

    @staticmethod
    def setLineSymbol(layer, color='black', penstyle='solid', width='0.55'):
        lineSymbol = QgsLineSymbol.createSimple({
            'color': color, 'penstyle': penstyle, 'width': width})
        SetSymbolLib.__setSymbol(layer, lineSymbol)

    @staticmethod
    def setMarkerSymbol(layer, color='black', size='3.6', name='circle'):
        # circle, square, rectangle, diamond, pentagon, triangle, 
        # equilateral_triangle, star, regular_star, arrow 
        nodesSymbol = QgsMarkerSymbol.createSimple({
            'color': color, 'name': name, 'size': size, 'width_border': '0'})
        SetSymbolLib.__setSymbol(layer, nodesSymbol)

    @staticmethod
    def setSimpleOutlineFillSymbol(layer, color='red', width='1.1', penstyle='dot'):
        symbol_layer = QgsSimpleLineSymbolLayer.create(
            {'color': color, 'width': width, 'penstyle': penstyle})
        SetSymbolLib.__altSetSymbol(layer, symbol_layer)

    @staticmethod
    def setSvgSymbol(markerLayer, fieldName, svgSymbolDirname,
                     size='6', rotationFieldName=None):
        if markerLayer is not None:
            fni = markerLayer.dataProvider().fieldNameIndex(fieldName)
            uniqValues = markerLayer.dataProvider().uniqueValues(fni)

            categories = []
            for value in uniqValues:
                mySymbol = QgsSymbol.defaultSymbol(markerLayer.geometryType())

                svgStyle = { 'name': f'{svgSymbolDirname}/{value}.svg', 'size': size }
                svgSymbol = QgsSvgMarkerSymbolLayer.create(svgStyle)
                if rotationFieldName is not None:
                    svgSymbol.dataDefinedProperties().setProperty(
                        QgsSymbolLayer.PropertyAngle, QgsProperty.fromField(rotationFieldName))

                mySymbol.changeSymbolLayer(0, svgSymbol)

                category = QgsRendererCategory(value, mySymbol, str(value))
                categories.append(category)

            renderer = QgsCategorizedSymbolRenderer(fieldName, categories)
            markerLayer.setRenderer(renderer)
            iface.layerTreeView().refreshLayerSymbology(markerLayer.id())
            markerLayer.triggerRepaint()
