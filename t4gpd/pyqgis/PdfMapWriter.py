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

from qgis.PyQt.QtCore import QRectF
from qgis.PyQt.QtGui import QFont
from qgis.core import (QgsLayoutExporter, QgsLayoutItemLabel, QgsLayoutItemLegend,
                       QgsLayoutItemMap, QgsLayoutItemScaleBar,
                       QgsLayoutPoint, QgsLayoutSize, QgsLegendStyle,
                       QgsPrintLayout, QgsProject,
                       QgsUnitTypes)


class PdfMapWriter(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, outputFileName, layerExtent, xOffset=0, yOffset=0,
                 legendXOffset=238, legendYOffset=1, scaleBarXOffset=60,
                 scaleBarYOffset=120, scaleBarNSegm=3, scalebarBg=False,
                 fileFormat='a4landscape', textLabel=None, labelXOffset=10,
                 labelYOffset=10, fontLabel=QFont('Cambria', 34, QFont.Bold),
                 numUnitsPerSegment=None, scaleBarFontSize=QFont('Cambria', 24),
                 fontLegend=None, symbolHeight=None, legendBg=None):
        '''
        Constructor
        '''
        self.outputFileName = outputFileName
        _layout = PdfMapWriter.__getLayout(layerExtent, xOffset, yOffset,
            legendXOffset, legendYOffset,
            scaleBarXOffset, scaleBarYOffset, scaleBarNSegm, scalebarBg,
            fileFormat, textLabel, labelXOffset, labelYOffset,
            fontLabel, numUnitsPerSegment, scaleBarFontSize,
            fontLegend, symbolHeight, legendBg)
        self.layoutExporter = QgsLayoutExporter(_layout)

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
        scaleBar.setFont(scaleBarFontSize)
        layout.addItem(scaleBar)
        scaleBar.attemptMove(QgsLayoutPoint(scaleBarXOffset, scaleBarYOffset, QgsUnitTypes.LayoutMillimeters))
        # ## scaleBar.setFrameEnabled(True)
        scaleBar.setBackgroundEnabled(1 if scalebarBg else 0)

        return layout

    def run(self):
        self.layoutExporter.exportToPdf(self.outputFileName,
                                        QgsLayoutExporter.PdfExportSettings())
