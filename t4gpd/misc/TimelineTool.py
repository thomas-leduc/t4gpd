'''
Created on 9 dec. 2022

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

from geopandas import GeoDataFrame
from numpy import arange, isnan
from pandas import DataFrame
from shapely.geometry import CAP_STYLE, LineString, Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

import matplotlib.pyplot as plt


class TimelineTool(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, df, label='label', start='start', stop='stop',
                 color=None, fontsize=16, xrotation=0, oFile=None):
        '''
        Constructor
        '''
        if not isinstance(df, DataFrame):
            raise IllegalArgumentTypeException(df, 'DataFrame')
        self.df = df

        for fieldname in [label, start, stop]:
            if not fieldname in df:
                raise Exception('%s is not a relevant field name!' % fieldname)
        self.label = label
        self.start = start
        self.stop = stop

        if not (color is None or (color in df)):
            raise Exception('%s is not a relevant field name!' % color)
        self.color = color
        self.fontsize = fontsize
        self.xrotation = xrotation
        self.oFile = oFile

    def __build(self):
        self.df[self.stop] = list(zip(self.df[self.start], self.df[self.stop]))
        self.df[self.stop] = self.df[self.stop].apply(
            lambda t: t[0] + 1 if (isnan(t[1])) else t[1])
        self.df['y'] = -arange(1, len(self.df) + 1)

        x0, x1 = self.df[self.start].min(), self.df[self.stop].max()
        x0, x1 = x0 - 1, x1 + 1

        # ARROW GEODATAFRAME
        d = 0.35
        arrow = GeoDataFrame([
            {'geometry': LineString([ (x0, 0), (x1, 0) ])},
            {'geometry': LineString([ (x1 - d, d), (x1, 0), (x1 - d, -d) ])},
            ])
        arrow.geometry = arrow.geometry.apply(
            lambda g: g.buffer(0.05, cap_style=CAP_STYLE.flat))

        # RECT GEODATAFRAME
        dy = 0.45
        rect = GeoDataFrame([
            {
                'geometry': Polygon([
                    (row[self.start], row.y - dy),
                    (row[self.stop], row.y - dy),
                    (row[self.stop], row.y + dy),
                    (row[self.start], row.y + dy) ]),
                'color': None if (self.color is None) else row[self.color]
            }
            for _, row in self.df.iterrows()
            ])
        return arrow, rect

    def run(self):
        arrow, rect = self.__build()

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))

        arrow.plot(ax=ax, edgecolor='dimgrey', color='grey')
        if (self.color is None):
            rect.plot(ax=ax, edgecolor='black', color='grey')
        else:
            for color in rect[self.color].unique():
                _rect = rect[ rect[self.color] == color ]
                _rect.plot(ax=ax, edgecolor=color, color=color)

        # ax.yaxis.set_visible(False)
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(0.0)
        ax.tick_params(axis='x', labelsize=self.fontsize, rotation=self.xrotation)
        ax.set_yticks(self.df.y, self.df[self.label], fontsize=self.fontsize)
        ax.grid(color='lightgrey', linestyle=':', linewidth=0.7)

        if self.oFile is None:
            plt.show()
        else:
            plt.savefig(self.oFile, bbox_inches='tight')            
        plt.close(fig)

'''
from io import StringIO
from pandas import read_csv

_sio = StringIO("""label;start;stop;color
Abc;2003;;red
Def;2007;2012;green
Ghi;2014;;blue
""")
df = read_csv(_sio, sep=';')

# TimelineTool(df).run()
TimelineTool(df, color='color', oFile='/tmp/timeline.pdf').run()
'''
