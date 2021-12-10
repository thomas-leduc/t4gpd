'''
Created on 1 oct. 2021

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
import matplotlib.pyplot as plt
from numpy import histogram
from pandas import DataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PopulationPyramid(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, male_df, female_df, commonFieldname, nClusters='auto',
                 outputFile=None, title=None):
        '''
        Constructor
        '''
        for _gdf in (male_df, female_df):
            if not isinstance(_gdf, DataFrame):
                raise IllegalArgumentTypeException(_gdf, 'DataFrame')
            if commonFieldname not in _gdf:
                raise Exception('%s is not a relevant field name!' % commonFieldname)
        self.males = male_df[commonFieldname] 
        self.females = female_df[commonFieldname] 
        self.nClusters = nClusters
        self.outputFile = outputFile
        self.title = title

    def run(self):
        m_hist, m_bin_edges = histogram(self.males, bins=self.nClusters)
        f_hist, _ = histogram(self.females, bins=len(m_hist))
        xmin, xmax = min(min(m_hist), min(f_hist)), 1.01 * max(max(m_hist), max(f_hist))

        fig, axes = plt.subplots(ncols=2, sharey=True, figsize=(9, 6))
        if self.title is None:
            plt.suptitle('Population Pyramid', fontsize=20, ha='center')
        else:
            plt.suptitle(self.title, fontsize=20, ha='center')
        # y = [(m_bin_edges[i + 1] + m_bin_edges[i]) / 2.0 for i in range(len(m_hist))]
        yLbls = ['%.1f-%.1f' % (m_bin_edges[i], m_bin_edges[i + 1]) for i in range(len(m_hist))]

        axes[0].barh(yLbls, m_hist, align='center', color='darkgrey')
        axes[0].set(title='Males')
        axes[0].set_xlim([xmin, xmax])
        axes[0].set(yticks=yLbls, yticklabels=yLbls)
        axes[0].invert_xaxis()
        axes[0].grid()

        axes[1].barh(yLbls, f_hist, align='center', color='lightgrey')
        axes[1].set(title='Females')
        axes[1].set_xlim([xmin, xmax])
        axes[1].grid()

        if self.outputFile is None:
            fig.tight_layout()
            plt.show()
        else:
            plt.savefig(self.outputFile, format='pdf', bbox_inches='tight')
        plt.close(fig)
