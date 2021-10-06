'''
Created on 12 sept. 2020

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
from t4gpd.commons.AngleLib import AngleLib


class AbstractHardShadow(GeoProcess):
    '''
    classdocs
    '''

    def run(self):
        rows = []

        for _dt, _radDir, _solarAlti, _solarAzim in self.sunPositions:
            # Hypothesis: the shadow cast by a 1m high mask is at most 10m long (arctan(0.1)=5.71) 
            if (_solarAlti < AngleLib.toRadians(5.71)):
                print('Solar height less than 5.71 degrees (%.1f degrees) on %s!' % (
                    AngleLib.toDegrees(_solarAlti), _dt))
            else:
                for _, row in self.gdf.iterrows():
                    _shadow = self._auxiliary(row, _radDir, _solarAlti, _solarAzim)
                    if _shadow is not None:
                        _row = self.updateOrAppend(row, {'datetime': str(_dt), 'geometry': _shadow})
                        rows.append(_row)

        result = GeoDataFrame(rows, crs=self.crs)

        if self.aggregate:
            result = result[['datetime', 'geometry']].dissolve(by='datetime')
            # Use a buffer to avoid slivers
            result.geometry = result.buffer(0.001, -1)
            result.reset_index(inplace=True)

        return result
