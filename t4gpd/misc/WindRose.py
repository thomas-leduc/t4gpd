'''
Created on 16 feb. 2021

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
from pandas import DataFrame
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from windrose.windrose import WindroseAxes

import matplotlib.pyplot as plt 


class WindRose(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, windDirectionFieldname='WindDirection', windSpeedFieldname='WindSpeed',
                 title=None, outputFile=None, nsector=16, speedClasses=6):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, (DataFrame, GeoDataFrame)):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        for fieldname in (windSpeedFieldname, windDirectionFieldname):
            if fieldname not in inputGdf:
                raise Exception('%s is not a relevant field name!' % fieldname)
        self.windDirection = windDirectionFieldname
        self.windSpeed = windSpeedFieldname

        self.title = title
        self.outputFile = outputFile
        self.nsector = nsector
        self.speedClasses = speedClasses

    def run(self):
        ws = self.inputGdf[self.windSpeed]
        wd = self.inputGdf[self.windDirection]

        ax = WindroseAxes.from_ax()
        if self.title is not None:
            ax.set_title(self.title)
        ax.bar(wd, ws, normed=True, opening=0.8, edgecolor='white', cmap=None,
               bins=self.speedClasses, nsector=self.nsector)
        ax.set_legend(title="Wind speed (m.s$^{-1}$)")
        ax.set_xticklabels(['E', 'N-E', 'N', 'N-W', 'W', 'S-W', 'S', 'S-E'])

        if self.outputFile is None:
            plt.show()
        else:
            plt.savefig(self.outputFile, format='pdf', bbox_inches='tight')

'''
from random import randrange

rows = [{'WindDirection': randrange(0, 360), 'WindSpeed': randrange(0, 10)} for _ in range(100)]
df = DataFrame(rows)

df = DataFrame(data={
    'WindDirection': [0, 0, 0, 90],
    'WindSpeed': [8, 6, 7, 4],
    })
WindRose(df, title='XXX', nsector=16, speedClasses=3).run()
'''
