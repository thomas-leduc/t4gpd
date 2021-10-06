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
from numpy import arctan, tan
from shapely.geometry import LineString, Point
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class AbstractSunshineDuration(AbstractGeoprocess):
    '''
    classdocs
    '''

    def _getAllSunPositions(self, datetimes, maxElevation):
        result = []

        for dt in datetimes:
            alti, _ = self.sunModel.getSolarAnglesInRadians(dt)
            radDir = self.sunModel.getRadiationDirection(dt)
            if (0 < alti):
                rayLen = maxElevation / tan(alti)
                result.append((alti, radDir, rayLen))

        return result

    def _beingInTheSun(self, viewpoint, radDir, rayLen, sunAlti):
        # To avoid: "Inconsistent coordinate dimensionality"
        viewpoint = Point((viewpoint.x, viewpoint.y))
        remotePoint = Point((viewpoint.x + rayLen * radDir[0], viewpoint.y + rayLen * radDir[1]))
        sunRay = LineString([viewpoint, remotePoint])

        masksIds = list(self.masksSIdx.intersection(sunRay.bounds))
        for maskId in masksIds:
            mask = self.masksGdf.loc[maskId]
            maskGeom = mask.geometry
            maskElevation = mask[self.maskElevationFieldname]

            if sunRay.crosses(maskGeom):
                tmpGeom = maskGeom.intersection(sunRay)
                gc = tmpGeom.geoms if GeomLib.isMultipart(tmpGeom) else [tmpGeom]

                for geom in gc:
                    for vertex in geom.coords:
                        hitPoint = Point(vertex)
                        _dist = viewpoint.distance(hitPoint)
                        _angle = arctan(maskElevation / _dist)
                        if (_angle >= sunAlti):
                            return False

        return True
