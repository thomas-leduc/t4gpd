'''
Created on 11 oct. 2022

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
import re

from fiona import listlayers
from geopandas import read_file
from pandas import concat
from t4gpd.commons.Epsilon import Epsilon
from t4gpd.commons.GeoProcess import GeoProcess


class TracksWaypointsReader(GeoProcess):
    '''
    classdocs
    '''
    RE1 = re.compile(r'^track(\d*)$')
    RE2 = re.compile(r'^waypoints(\d*)$')

    def __init__(self, inputFile):
        '''
        Constructor
        '''
        self.inputFile = inputFile

    def run(self):
        static, tracks, waypoints = None, [], []
        layernames = sorted(listlayers(self.inputFile))
        for layer in layernames:
            if layer.startswith('static'):
                static = read_file(self.inputFile, layer=layer)

            elif layer.startswith('track'):
                num = int(self.RE1.search(layer).group(1))
                df = read_file(self.inputFile, layer=layer)
                df['id'] = num
                df = df[['id', 'geometry']].copy(deep=True)
                tracks.append(df)

            elif layer.startswith('waypoints'):
                num = int(self.RE2.search(layer).group(1))
                df = read_file(self.inputFile, layer=layer)
                df = df[['id', 'geometry']].copy(deep=True)
                idMin, idMax = df.id.min(), df.id.max()
                df['minTagName'], df['maxTagName'] = idMin, idMax
                assert (num == idMin // 100) and (num == idMax // 100), f'inconsistent ids in the waypoints{num} layer'
                df.sort_values(by='id', inplace=True)
                waypoints.append(df)

        if (len(tracks) != len(waypoints)):
            raise Exception("The number of tracks does not equal the number of waypoints layers!")

        for i in range(len(tracks)):
            _trackId, _trackGeom, _waypoints = tracks[i].id.squeeze(), tracks[i].geometry.squeeze(), waypoints[i]
            _waypoints['curv_absc'] = _waypoints.geometry.apply(
                lambda g: _trackGeom.project(g, normalized=True))

            if not _waypoints.curv_absc.is_monotonic_increasing:
                raise Exception(f"The abscissa of the \
waypoints should be increasing. Check the direction of track #{_trackId}, which should \
be consistent with the direction of the waypoints.")

            _waypoints['delta_curv_absc'] = _waypoints.curv_absc.diff(periods=1)
            _waypoints.delta_curv_absc = _waypoints.delta_curv_absc.shift(periods=-1)

        assert Epsilon.isZero(_waypoints.curv_absc.min()), f'Track {_trackId}: The min. curv. absc. must be equal to 0'
        assert Epsilon.equals(1.0, _waypoints.curv_absc.max()), f'Track {_trackId}: The max. curv. absc. must be equal to 1'

        tracks = concat(tracks, ignore_index=True)
        waypoints = concat(waypoints, ignore_index=True)
        return static, tracks, waypoints
