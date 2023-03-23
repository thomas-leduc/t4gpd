'''
Created on 12 jav. 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from numpy import cos, hstack, linspace, pi, sin 
from pandas import DataFrame
from shapely.geometry import Polygon
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

import matplotlib as mpl, matplotlib.pyplot as plt


class RoseMappingTool(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, df, label='label', color='color', solid=False, power=10, radius=1, npts=75):
        '''
        Constructor
        '''
        if not isinstance(df, DataFrame):
            raise IllegalArgumentTypeException(df, 'DataFrame')
        self.df = df

        if not label in df:
            raise Exception('%s is not a relevant field name!' % label)
        self.label = label

        if not (color is None or (color in df)):
            raise Exception('%s is not a relevant field name!' % color)
        self.color = color

        if not (isinstance(solid, bool) or (solid in df)):
            raise Exception('%s is not a relevant field name!' % solid)
        self.solid = solid

        self.npetals = len(df)
        self.power = power
        self.radius = radius
        self.npts = npts

    def _petal_old(self, npetal, npts=100):
        # npetal: 0 -> self.npetals - 1
        deltaTheta = pi / (2 * self.npetals)

        if (0 == npetal):
            n0, n1 = 0, 2 * len(self.df) - 1
        else:
            n0, n1 = 2 * npetal - 1, 2 * npetal

        theta = hstack([
            linspace(n0 * deltaTheta, (n0 + 1) * deltaTheta, npts),
            linspace(n1 * deltaTheta, (n1 + 1) * deltaTheta, npts),
            ])
        x = self.radius * cos(self.npetals * theta) * cos(theta)
        y = self.radius * cos(self.npetals * theta) * sin(theta)

        return x, y

    def _petal(self, npetal, npts=100):
        # npetal: 0 -> self.npetals - 1
        deltaTheta = pi / self.npetals

        if (0 == npetal):
            n0, n1 = 0, 2 * len(self.df) - 1
        else:
            n0, n1 = 2 * npetal - 1, 2 * npetal

        theta = hstack([
            linspace(n0 * deltaTheta, (n0 + 1) * deltaTheta, npts),
            linspace(n1 * deltaTheta, (n1 + 1) * deltaTheta, npts),
            ])
        _tmp = self.radius * (1 - sin((self.npetals / 2) * theta) ** self.power)
        x = _tmp * cos(theta - pi / 2)
        y = _tmp * sin(theta - pi / 2)

        return x, y

    @staticmethod
    def plot(gdf, fontsize=13, hatch='x', hatchwidth=0.1, oFile=None):
        foo = lambda s: '\n'.join(s.split(' '))

        fig, ax = plt.subplots(figsize=(8.26, 8.26))
        for solid, color in zip(gdf.solid, gdf.color):
            _gdf = gdf[gdf.color == color]
            if solid:
                _gdf.plot(ax=ax, color=color, alpha=0.5)
                _gdf.apply(lambda x: ax.annotate(
                    text=foo(x.label), xy=x.geometry.centroid.coords[0],
                    color='black', size=fontsize, weight='bold',
                    ha='center', va='center'), axis=1);
            else:
                mpl.rcParams['hatch.linewidth'] = hatchwidth
                _gdf.boundary.plot(ax=ax, color=color, hatch=hatch)
                _gdf.apply(lambda x: ax.annotate(
                    text=foo(x.label), xy=x.geometry.centroid.coords[0],
                    color=color, size=fontsize, weight='bold',
                    ha='center', va='center'), axis=1);
        ax.axis('off')
        if oFile is None:
            plt.show()
        else:
            plt.savefig(oFile, bbox_inches='tight')            
        plt.close(fig)
        
    def run(self):
        # ~ https://fr.wikipedia.org/wiki/Rosace_(math%C3%A9matiques)
        rows = []
        for npetal, row in self.df.iterrows():
            color, label = row[self.color], row[self.label]
            solid = self.solid if isinstance(self.solid, bool) else row[self.solid]
            x, y = self._petal(npetal, self.npts)
            rows.append({
                'npetal': npetal,
                'geometry': Polygon([(_x, _y) for _x, _y in zip(x, y)]),
                'label': label,
                'color': color,
                'solid': solid
                })
        return GeoDataFrame(rows)

'''
from io import StringIO
from pandas import read_csv

_sio = StringIO("""label;color;solid
Géographie, aménagement et développement;red;True
Études urbaines;grey;False
Énergies renouvelables, développement durable et environnement;green;False
Sciences de l'environnement;orange;True
Informatique;magenta;False
""")
df = read_csv(_sio, sep=';')

gdf = RoseMappingTool(df, label='label', color='color', solid='solid', power=10).run()
print(gdf)
RoseMappingTool.plot(gdf, fontsize=12, hatch='x',
                     hatchwidth=0.1, oFile=None)
'''
