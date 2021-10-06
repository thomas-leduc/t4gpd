'''
Created on 17 janv. 2021

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
from datetime import datetime

from geopandas.geodataframe import GeoDataFrame
from numpy import cos, sin
from shapely.affinity import translate
from shapely.geometry import LineString
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.SunLib import SunLib


class STSunMap2D(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, viewpointsGdf, datetimes, size=4.0, projectionName='Stereographic',
                 tz=None, model='pysolar'):
        '''
        Constructor
        '''
        if not isinstance(viewpointsGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(viewpointsGdf, 'GeoDataFrame')
        self.viewpointsGdf = viewpointsGdf

        self.datetimes = DatetimeLib.generate(datetimes, tz)

        self.size = size

        if not projectionName in ['Stereographic']:
            raise IllegalArgumentTypeException(projectionName, 'spherical projection as "Stereographic"')
        self.proj = STSunMap2D.__stereographic
        self.sunModel = SunLib(gdf=viewpointsGdf, model=model)

    @staticmethod
    def __stereographic(lat, lon, size=1.0):
        radius = (size * cos(lat)) / (1.0 + sin(lat))
        return (radius * cos(lon), radius * sin(lon))

    def run(self):
        # BUILD THE SUNPATHS
        sunpaths = []
        for _lbl, _dt in self.datetimes.items():
            if isinstance(_dt, datetime):
                alti, azim = self.sunModel.getSolarAnglesInRadians(_dt, self.lat, self.lon)
                if (0 <= alti):
                    sunpaths.append({'geometry': self.proj(alti, azim, self.size),
                                     'label': str(_lbl) })

            elif isinstance(_dt, list):
                _xy = []
                for __dt in _dt:
                    alti, azim = self.sunModel.getSolarAnglesInRadians(__dt)
                    if (0 <= alti):
                        _xy.append(self.proj(alti, azim, self.size))
                if (2 <= len(_xy)):
                    sunpaths.append({'geometry': LineString(_xy),
                                     'label': str(_lbl) })

        # -----        
        rows = []
        for _, row in self.viewpointsGdf.iterrows():

            # BUILD THE FRAMEWORK
            viewPoint = row.geometry.centroid
            east = translate(viewPoint, xoff=-self.size)
            west = translate(viewPoint, xoff=self.size)
            north = translate(viewPoint, yoff=self.size)
            south = translate(viewPoint, yoff=-self.size)
            rows += [ 
                {'geometry': viewPoint.buffer(self.size).exterior, 'label': 'framework'},
                {'geometry': LineString([east, west]), 'label': 'framework'},
                {'geometry': LineString([south, north]), 'label': 'framework'},
                ]

            # ADAPT THE SUNPATHS ALREADY BUILT
            for _sunpath in sunpaths:
                _geom, _lbl = _sunpath['geometry'], _sunpath['label']
                _geom = translate(_geom, xoff=viewPoint.x, yoff=viewPoint.y)
                rows.append({'geometry': _geom, 'label': _lbl})

        return GeoDataFrame(rows, crs=self.viewpointsGdf.crs)
