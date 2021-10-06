'''
Created on 29 sept. 2020

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
from t4gpd.commons.GeoProcess import GeoProcess
from geopandas.geodataframe import GeoDataFrame
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
import matplotlib.pyplot as plt


class FrequencyHistogram(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, fieldnames, nClusters, minValues=None, maxValues=None, outputFile='',
                 density=False, cumulative=False):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        if isinstance(fieldnames, str):
            self.fieldnames = [fieldnames]
        elif isinstance(fieldnames, (list, tuple)):
            self.fieldnames = fieldnames
        else:
            raise IllegalArgumentTypeException(fieldnames, 'must be a list or tuple of fieldnames')
        for fieldname in self.fieldnames:
            if fieldname not in self.inputGdf:
                raise Exception('%s is not a relevant field name!' % (fieldname))
        self.nFields = len(self.fieldnames)

        self.nClusters = nClusters if isinstance(nClusters, (list, tuple)) else [nClusters] * self.nFields

        if minValues is None:
            self.minValues = [None] * self.nFields
        else:
            self.minValues = minValues if isinstance(minValues, (list, tuple)) else [minValues] * self.nFields
        if maxValues is None:
            self.maxValues = [None] * self.nFields
        else:
            self.maxValues = maxValues if isinstance(maxValues, (list, tuple)) else [maxValues] * self.nFields

        if (self.nFields != len(self.nClusters)):
            raise IllegalArgumentTypeException(
                self.nClusters, 'nClusters must be either an int or a list of %d items' % self.nFields)
        if (self.nFields != len(self.minValues)):
            raise IllegalArgumentTypeException(
                self.minValues, 'minValues must be either a float or a list of %d items' % self.nFields)
        if (self.nFields != len(self.maxValues)):
            raise IllegalArgumentTypeException(
                self.maxValues, 'maxValues must be either a float or a list of %d items' % self.nFields)

        self.outputFile = outputFile
        self.density = density
        self.cumulative = cumulative

    def run(self):
        values = [list(self.inputGdf[fieldname]) for fieldname in self.fieldnames]

        numcols, numrows, pairsOfWeightsAndRanges = 1, self.nFields, []

        mainFig = plt.figure(figsize=(numcols * 8.26, numrows * 8.26))  # 21 cm ~ 8.26 inches
        mainFig.clear()

        for fignum in range(self.nFields):
            plt.subplot(numrows, numcols, fignum + 1)  # numrows, numcols, fignum     
            plt.title('Histogram of %s' % self.fieldnames[fignum])
            plt.xlabel(self.fieldnames[fignum])
            if self.density:
                plt.ylabel('Probability density')
            else:
                plt.ylabel('Number of values')
            plt.grid(True)

            n, bins, _ = plt.hist(values[fignum], bins=self.nClusters[fignum],
                                  density=self.density, cumulative=self.cumulative,
                                  range=(self.minValues[fignum], self.maxValues[fignum]),
                                  facecolor='gray', edgecolor='black', orientation='vertical',
                                  hatch='', histtype='bar', align='mid', rwidth=1.0)
            x = [(bins[i] + bins[i + 1]) / 2.0 for i in range(len(bins) - 1)]
            pairsOfWeightsAndRanges.append([n, bins])
            plt.plot(x, n, 'ro', x, n, 'r--')

        if self.outputFile is not None:
            if ('' == self.outputFile):
                plt.show()
            else:
                plt.savefig(self.outputFile, format='pdf', bbox_inches='tight')  # , facecolor='w', edgecolor='k', pad_inches=0.15)

        return pairsOfWeightsAndRanges
