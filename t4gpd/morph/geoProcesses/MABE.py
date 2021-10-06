'''
Created on 23 juin 2020

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
from numpy import isnan, pi

from t4gpd.commons.AngleLib import AngleLib
from t4gpd.commons.ellipse.EllipseLib import EllipseLib
from t4gpd.commons.ellipse.EllipticHullLib import EllipticHullLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class MABE(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, npoints=40, threshold=None, debug=False):
        '''
        Constructor
        '''
        self.npoints = npoints
        self.mabe = EllipticHullLib(threshold, debug)

    def runWithArgs(self, row):
        geom = row.geometry
        if geom is None:
            return None

        centre, semiXAxis, semiYAxis, azim, _, _ = self.mabe.getMinimumAreaBoundingEllipse(geom)
        mabe = EllipseLib.getEllipseContour(centre, semiXAxis, semiYAxis, azim, self.npoints)

        if mabe is None:
            raise Exception('Minimum-area bounding ellipse is None!')

        mabeArea = pi * semiXAxis * semiYAxis
        if (isnan(mabeArea)) or (mabeArea < geom.area):
            raise Exception('Minimum-area bounding ellipse is %s (input geom area: %.1f)!' % (str(mabeArea), geom.area()))
        mabePerim = EllipseLib.getEllipsePerimeter(semiXAxis, semiYAxis)

        axis = EllipseLib.getEllipseMainAxis(centre, semiXAxis, semiYAxis, azim)

        return {
            'mabe_centre': str(centre),
            'mabe_axis': str(axis),
            'mabe_area': mabeArea,
            'mabe_perim': mabePerim,
            'mabe_xaxis': semiXAxis,
            'mabe_yaxis': semiYAxis,
            'mabe_azim': AngleLib.toDegrees(azim),
            'geometry': mabe
            }
