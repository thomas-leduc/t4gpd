'''
Created on 3 mars 2021

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
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCastingLib import RayCastingLib
from t4gpd.commons.SVFLib import SVFLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class SkyViewFactorOnTopOfRoof(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, buildings, nRays=64, maxRayLen=100.0, elevationFieldname='HAUTEUR',
                 method=2018, background=True):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, 'GeoDataFrame')
        self.buildings = buildings
        self.spatialIndex = buildings.sindex

        self.shootingDirs = RayCastingLib.preparePanopticRays(nRays)
        self.maxRayLen = maxRayLen

        if elevationFieldname not in buildings:
            raise Exception('%s is not a relevant field name!' % elevationFieldname)
        self.elevationFieldname = elevationFieldname

        if (1981 == method):
            print('SVF calculation method: Oke (1981), nRays = %d, maxRayLen = %.1f' % (nRays, maxRayLen))
            self.method = SVFLib.svf1981
        else:
            print('SVF calculation method: Bernard et al. (2018), nRays = %d, maxRayLen = %.1f' % (nRays, maxRayLen))
            self.method = SVFLib.svf2018

        self.background = background

    def runWithArgs(self, row):
        viewpoint = row.geometry.centroid

        enclosingFeatures = GeomLib.getEnclosingFeatures(self.buildings, self.spatialIndex, viewpoint)

        if (0 == len(enclosingFeatures)):
            # OUTDOOR/STREET-LEVEL VIEWPOINT
            _, _, hitDists, hitMasks, _ = RayCastingLib.multipleRayCast25D(
                self.buildings, self.spatialIndex, viewpoint, self.shootingDirs,
                self.maxRayLen, self.elevationFieldname, self.background)

        else:
            # INDOOR/ROOFTOP VIEWPOINT

            # REMOVE enclosingFeatures FROM THE GeoDataFrame & SpatialIndex OF SURROUNDING MASKS
            enclosingFeaturesIndex = [f.name for f in enclosingFeatures]
            _buildings = self.buildings[~self.buildings.index.isin(enclosingFeaturesIndex)]
            _buildings.reset_index(drop=True, inplace=True)  # HANDLE POTENTIAL KeyError
            _sindex = _buildings.sindex

            # ASSESS THE SVF
            _, _, hitDists, hitMasks, _ = RayCastingLib.multipleRayCastOnTopOfRoof(
                _buildings, _sindex, viewpoint, self.shootingDirs,
                self.maxRayLen, enclosingFeatures, self.elevationFieldname, self.background)

        hitHeights = [0.0 if f is None else f[self.elevationFieldname] for f in hitMasks]

        return {
            # 'hit_heights': ArrayCoding.encode(hitHeights),
            'svf_roof': self.method(hitHeights, hitDists)
            }
