'''
Created on 18 nov. 2020

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
from numpy import pi
from shapely.coords import CoordinateSequence
from shapely.geometry import LinearRing, LineString, Polygon
from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

import matplotlib.pyplot as plt


class StreetOrientationHistogram(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, nClusters, outputFile='', title=None, density=False, cumulative=False):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.nClusters = nClusters
        self.outputFile = outputFile
        self.title = title
        self.density = density
        self.cumulative = cumulative

    def __fromShapelyGeometryToAzimuthsAndLengths(self, obj):
        result = []

        if GeomLib.isMultipart(obj):
            for g in obj.geoms:
                result += self.__fromShapelyGeometryToAzimuthsAndLengths(g)
            return result

        elif isinstance(obj, (LinearRing, LineString)):
            return self.__fromShapelyGeometryToAzimuthsAndLengths(obj.coords)

        elif isinstance(obj, Polygon):
            result = self.__fromShapelyGeometryToAzimuthsAndLengths(obj.exterior.coords)
            for hole in obj.interiors:
                result += self.__fromShapelyGeometryToAzimuthsAndLengths(hole.coords)
            return result

        elif isinstance(obj, (list, tuple, CoordinateSequence)):
            for i in range(1, len(obj)):
                _azim = AngleLib.angleBetweenNodes((obj[i - 1][0] + 1, obj[i - 1][1]), obj[i - 1], obj[i])
                _azim = AngleLib.toDegrees(_azim if (_azim < pi) else _azim - pi)
                _len = GeomLib.distFromTo(obj[i - 1], obj[i])
                result.append([_azim, _len])

        return result

    def run(self):
        items, totalLen = [], 0.0
        for geom in self.inputGdf.geometry:
            items += self.__fromShapelyGeometryToAzimuthsAndLengths(geom)
            totalLen += geom.length

        x = [_azim for _azim, _ in items]
        weights = [_len for _, _len in items]

        mainFig = plt.figure(1)
        mainFig.clear()

        if self.title is None:
            plt.title('Street orientation histogram\nRotation in the counter clockwise direction starting from full East',
                      fontsize=14)
        else:
            plt.title(self.title, fontsize=14)
        plt.xlabel('Orientation (0 - 180$^0$)')
        if self.density:
            plt.ylabel('Probability density')
        else:
            plt.ylabel('Cumulative road length (m)')
        plt.grid(True)

        n, bins, _ = plt.hist(x, bins=self.nClusters, density=self.density, cumulative=self.cumulative,
                              range=(0, 180),
                              weights=weights,
                              facecolor='gray', edgecolor='black', orientation='vertical',
                              hatch='', histtype='bar', align='mid', rwidth=1.0)

        xx = [(bins[i] + bins[i + 1]) / 2.0 for i in range(len(bins) - 1)]
        plt.plot(xx, n, 'ro', xx, n, 'r--')

        if self.outputFile is not None:
            if ('' == self.outputFile):
                plt.show()
            else:
                plt.savefig(self.outputFile, format='pdf', bbox_inches='tight')  # , facecolor='w', edgecolor='k', pad_inches=0.15)

        return [n, bins]
