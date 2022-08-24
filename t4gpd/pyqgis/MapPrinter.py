'''
Created on 10 juil. 2022

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

from qgis.PyQt.QtCore import QRectF
from qgis.PyQt.QtGui import QFont
from qgis.core import (QgsLayoutExporter, QgsLayoutItemLabel, QgsLayoutItemLegend,
                       QgsLayoutItemMap, QgsLayoutItemScaleBar,
                       QgsLayoutPoint, QgsLayoutSize, QgsLegendStyle,
                       QgsPrintLayout, QgsProject,
                       QgsUnitTypes)

from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
from t4gpd.pyqgis.AddMemoryLayer import AddMemoryLayer
from t4gpd.pyqgis.SetSymbolLib import SetSymbolLib
from t4gpd.pyqgis.ZoomLib import ZoomLib


class MapPrinter(object):
    '''
    classdocs
    '''
    PDF = 1
    PNG = 2
    SVG = 3

    @staticmethod
    def __getLayout(layerExtent, xOffset=0, yOffset=0, legendXOffset=238, legendYOffset=1, scaleBarXOffset=60,
        scaleBarYOffset=120, scaleBarNSegm=3, scalebarBg=False, fileFormat='a4landscape',
        textLabel=None, labelXOffset=10, labelYOffset=10, fontLabel=QFont('Cambria', 34, QFont.Bold),
        numUnitsPerSegment=None, scaleBarFontSize=QFont('Cambria', 24), fontLegend=None, symbolHeight=None,
        legendBg=None):
        if 'a4landscape' == fileFormat:
            width, height = 297, 210
        elif 'a4portrait' == fileFormat:
            width, height = 210, 297
        elif 'square' == fileFormat:
            width, height = 210, 210
        layoutSize = QgsLayoutSize(width=width, height=height, units=QgsUnitTypes.LayoutMillimeters)

        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.pageCollection().page(0).setPageSize(layoutSize)

        # CANVAS
        myMap = QgsLayoutItemMap(layout)
        myMap.setRect(QRectF(layerExtent.xMinimum(), layerExtent.yMinimum(), layerExtent.xMaximum(), layerExtent.yMaximum()))
        myMap.setExtent(layerExtent)
        layout.addItem(myMap)
        myMap.attemptResize(layoutSize)

        # TITLE
        if textLabel is not None:
            label = QgsLayoutItemLabel(layout)
            label.setText(textLabel)
            label.setFont(fontLabel)
            label.adjustSizeToText()
            layout.addItem(label)
            label.attemptMove(QgsLayoutPoint(labelXOffset, labelYOffset, QgsUnitTypes.LayoutMillimeters))
            label.setBackgroundEnabled(1)

        # LEGEND
        legend = QgsLayoutItemLegend(layout)
        legend.setTitle('Legend')
        legend.setLinkedMap(myMap)
        if fontLegend is not None:
            legend.setStyleFont(QgsLegendStyle.Title, fontLegend)
            legend.setStyleFont(QgsLegendStyle.Subgroup, fontLegend)
            legend.setStyleFont(QgsLegendStyle.SymbolLabel, fontLegend)
        if symbolHeight is not None:
            legend.setSymbolHeight(symbolHeight)
        layout.addItem(legend)
        legend.attemptMove(QgsLayoutPoint(legendXOffset, legendYOffset, QgsUnitTypes.LayoutMillimeters))
        # ## legend.setFrameEnabled(True)
        if (legendBg is not None) and legendBg:
            legend.setBackgroundEnabled(1)
        # legend.setBackgroundEnabled(1 if scalebarBg else 0)

        # SCALE BAR
        scaleBar = QgsLayoutItemScaleBar(layout)
        # Style possibilities are: 'Single Box', 'Double Box', 'Line Ticks Middle', 'Line Ticks Down', 'Line Ticks Up', 'Numeric'
        scaleBar.setStyle('Single Box')
        scaleBar.setLinkedMap(myMap)
        scaleBar.applyDefaultSize()
        scaleBar.setNumberOfSegmentsLeft(0)
        scaleBar.setNumberOfSegments(scaleBarNSegm)
        if numUnitsPerSegment is not None:
            scaleBar.setUnitsPerSegment(numUnitsPerSegment)
        # scaleBar.setFont(scaleBarFontSize)
        layout.addItem(scaleBar)
        scaleBar.attemptMove(QgsLayoutPoint(scaleBarXOffset, scaleBarYOffset, QgsUnitTypes.LayoutMillimeters))
        # ## scaleBar.setFrameEnabled(True)
        scaleBar.setBackgroundEnabled(1 if scalebarBg else 0)

        return layout

    @staticmethod
    def __outputTypeController(outputFileName):
        tmp = outputFileName.lower()
        if tmp.endswith('.pdf'):
            return MapPrinter.PDF
        elif tmp.endswith('.png'):
            return MapPrinter.PNG
        elif tmp.endswith('.svg'):
            return MapPrinter.SVG
        raise IllegalArgumentTypeException(outputFileName, '.png, .pdf or .svg filename suffix')

    @staticmethod
    def print(outputFileName, layerExtent, xOffset=0, yOffset=0, legendXOffset=238, legendYOffset=1,
                  scaleBarXOffset=15, scaleBarYOffset=185, scaleBarNSegm=3, scalebarBg=False,
                  fileFormat='a4landscape', textLabel=None, labelXOffset=10, labelYOffset=10,
                  fontLabel=QFont('Cambria', 34, QFont.Bold), numUnitsPerSegment=None,
                  scaleBarFontSize=QFont('Cambria', 24), fontLegend=None, symbolHeight=None,
                  legendBg=None):
        layout = MapPrinter.__getLayout(layerExtent, xOffset, yOffset,
                                        legendXOffset, legendYOffset, scaleBarXOffset,
                                        scaleBarYOffset, scaleBarNSegm, scalebarBg,
                                        fileFormat, textLabel, labelXOffset, labelYOffset,
                                        fontLabel, numUnitsPerSegment, scaleBarFontSize,
                                        fontLegend, symbolHeight, legendBg)
        layoutExporter = QgsLayoutExporter(layout)
        tmp = MapPrinter.__outputTypeController(outputFileName)

        if (MapPrinter.PDF == tmp):
            layoutExporter.exportToPdf(outputFileName, QgsLayoutExporter.PdfExportSettings())
        elif (MapPrinter.PNG == tmp):
            layoutExporter.exportToImage(outputFileName, QgsLayoutExporter.ImageExportSettings())
        elif (MapPrinter.SVG == tmp):
            layoutExporter.exportToSvg(outputFileName, QgsLayoutExporter.SvgExportSettings())

    @staticmethod
    def test():
        buildings = GeoDataFrameDemos.districtGraslinInNantesBuildings()
        roi = GeoDataFrameDemos.coursCambronneInNantes()
        path = GeoDataFrameDemos.coursCambronneInNantesPath()
        trees = GeoDataFrameDemos.districtGraslinInNantesTrees()

        for ext in ['pdf', 'png', 'svg']:
            QgsProject.instance().clear()

            buildings_layer = AddMemoryLayer(buildings, 'buildings').run()
            roi_layer = AddMemoryLayer(roi, 'Region of Interest').run()
            path_layer = AddMemoryLayer(path, 'Path').run()
            trees_layer = AddMemoryLayer(trees, 'Trees').run()

            SetSymbolLib.setFillSymbol(buildings_layer, color='black', width_border='0')
            SetSymbolLib.setSimpleOutlineFillSymbol(roi_layer, color='red', width='1.1', penstyle='dot')
            SetSymbolLib.setLineSymbol(path_layer, color='black', penstyle='solid', width='0.55')
            SetSymbolLib.setMarkerSymbol(trees_layer, color='green', size='1.9', name='circle')

            ZoomLib.setExtent(roi)

            roiExtent = roi_layer.extent().buffered(10.0)

            MapPrinter.print(f'/tmp/test.{ext}', roiExtent, xOffset=0, yOffset=0, legendXOffset=155,
                legendYOffset=155, scaleBarXOffset=5, scaleBarYOffset=192,
                scaleBarNSegm=3, scalebarBg=True, fileFormat='square',
                textLabel='Map title', labelXOffset=5, labelYOffset=10,
                fontLabel=QFont('Arial', 24, QFont.Bold), numUnitsPerSegment=None,
                scaleBarFontSize=QFont('Arial', 18), fontLegend=QFont('Arial', 16),
                symbolHeight=6)

'''
# COPY-PASTE TO TEST IN THE PYQGIS CONSOLE:
from t4gpd.pyqgis.MapPrinter import MapPrinter
MapPrinter.test()
'''
