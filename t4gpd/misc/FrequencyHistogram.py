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
from pandas import DataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

import matplotlib.pyplot as plt


class FrequencyHistogram(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, fieldnames, nClusters='auto', rangeValues=None, outputFile='',
                 density=False, cumulative=False, title=None, fontsize=20):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, DataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'DataFrame')
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

        if rangeValues is None:
            self.rangeValues = [None] * self.nFields
        elif isinstance(rangeValues, (list, tuple)):
            if ((2 == len(rangeValues)) and 
                isinstance(rangeValues[0], (int, float)) and
                isinstance(rangeValues[1], (int, float))):
                self.rangeValues = [rangeValues] * self.nFields
            else:
                self.rangeValues = rangeValues

        if (self.nFields != len(self.nClusters)):
            raise IllegalArgumentTypeException(
                self.nClusters, 'nClusters must be either an int or a list of %d items' % self.nFields)
        if (self.nFields != len(self.rangeValues)):
            raise IllegalArgumentTypeException(
                self.rangeValues, 'rangeValues must be either a float or a list of %d items' % self.nFields)

        self.outputFile = outputFile
        self.density = density
        self.cumulative = cumulative
        self.title = title
        self.fontsize = fontsize

    def run(self):
        values = [list(self.inputGdf[fieldname]) for fieldname in self.fieldnames]

        numcols, numrows, pairsOfWeightsAndRanges = 1, self.nFields, []

        mainFig = plt.figure(figsize=(numcols * 8.26, numrows * 8.26))  # 21 cm ~ 8.26 inches
        mainFig.clear()

        for fignum in range(self.nFields):
            plt.subplot(numrows, numcols, fignum + 1)  # numrows, numcols, fignum     
            plt.xlabel(self.fieldnames[fignum], fontsize=self.fontsize)
            if self.density:
                plt.ylabel('Probability density', fontsize=self.fontsize)
            else:
                plt.ylabel('Number of values', fontsize=self.fontsize)
            plt.grid(True)

            n, bins, _ = plt.hist(values[fignum], bins=self.nClusters[fignum],
                                  density=self.density, cumulative=self.cumulative,
                                  range=self.rangeValues[fignum],
                                  facecolor='gray', edgecolor='black', orientation='vertical',
                                  hatch='', histtype='bar', align='mid', rwidth=1.0)
            x = [(bins[i] + bins[i + 1]) / 2.0 for i in range(len(bins) - 1)]
            pairsOfWeightsAndRanges.append([n, bins])
            if self.title is None:
                plt.title('Histogram of %s (%d bins)' % (self.fieldnames[fignum], len(n)),
                          fontsize=self.fontsize + 4)
            else:
                plt.title(self.title, fontsize=self.fontsize + 4)
            # plt.plot(x, n, 'ro', x, n, 'r--')

        if self.outputFile is not None:
            if ('' == self.outputFile):
                plt.show()
            else:
                plt.savefig(self.outputFile, format='pdf', bbox_inches='tight')  # , facecolor='w', edgecolor='k', pad_inches=0.15)

        plt.close(mainFig)
        return pairsOfWeightsAndRanges
