'''
Created on 10 sept. 2020

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
from shapely.geometry import MultiPoint, MultiPolygon, Point
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.sun.ShadowLib import ShadowLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.sun.AbstractHardShadow import AbstractHardShadow


class STTreeHardShadow2(AbstractHardShadow):
    '''
    classdocs
    '''

    def __init__(self, treesGdf, datetimes, treeHeightFieldname, treeCrownHeightFieldname,
                 treeUpperCrownRadiusFieldname, treeLowerCrownRadiusFieldname,
                 altitudeOfShadowPlane=0, aggregate=False, tz=None, model='pysolar',
                 npoints=32):
        '''
        Constructor
        '''
        if not isinstance(treesGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(treesGdf, 'GeoDataFrame')
        self.gdf = treesGdf
        self.crs = treesGdf.crs

        if treeHeightFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (treeHeightFieldname))
        self.treeHeightFieldname = treeHeightFieldname

        if treeCrownHeightFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (treeCrownHeightFieldname))
        self.treeCrownHeightFieldname = treeCrownHeightFieldname

        if treeUpperCrownRadiusFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (treeUpperCrownRadiusFieldname))
        self.treeUpperCrownRadiusFieldname = treeUpperCrownRadiusFieldname

        if treeLowerCrownRadiusFieldname not in treesGdf:
            raise Exception('%s is not a relevant field name!' % (treeLowerCrownRadiusFieldname))
        self.treeLowerCrownRadiusFieldname = treeLowerCrownRadiusFieldname

        self.altitudeOfShadowPlane = altitudeOfShadowPlane
        self.aggregate = aggregate
        sunModel = SunLib(gdf=treesGdf, model=model)

        self.sunPositions = DatetimeLib.fromDatetimesDictToListOfSunPositions(
            datetimes, sunModel, tz)

        if not (0 == (npoints % 4)):
            raise IllegalArgumentTypeException(npoints, 'multiple of 4')
        self.npoints = npoints

    def _auxiliary(self, row, radDir, solarAlti, solarAzim):
        treeGeom = row.geometry
        treeHeight = row[self.treeHeightFieldname]
        treeCrownHeight = row[self.treeCrownHeightFieldname]
        treeUpperCrownRadius = row[self.treeUpperCrownRadiusFieldname]
        treeLowerCrownRadius = row[self.treeLowerCrownRadiusFieldname]

        if isinstance(treeGeom, Point):
            _shadow = ShadowLib.projectConicalTreeOntoShadowPlane(
                treeGeom, treeHeight, treeCrownHeight, treeUpperCrownRadius,
                treeLowerCrownRadius, None, radDir, solarAlti, solarAzim,
                self.altitudeOfShadowPlane, self.npoints)
            return _shadow

        elif isinstance(treeGeom, MultiPoint):
            _shadows = []
            for g in treeGeom.geoms:
                _shadow = ShadowLib.projectConicalTreeOntoShadowPlane(
                    g, treeHeight, treeCrownHeight, treeUpperCrownRadius,
                    treeLowerCrownRadius, None, radDir, solarAlti, solarAzim,
                    self.altitudeOfShadowPlane, self.npoints)
                if _shadow is not None:
                    _shadows.append(_shadow)
            return None if (0 == len(_shadows)) else MultiPolygon(_shadows)
