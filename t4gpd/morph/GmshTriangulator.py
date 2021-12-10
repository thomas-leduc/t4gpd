'''
Created on 17 juin 2020

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
from os import getpid, path
from subprocess import call
import tempfile

from geopandas.geodataframe import GeoDataFrame

from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.io.GeoWriter import GeoWriter
from t4gpd.io.MshReader import MshReader


class GmshTriangulator(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, inputGdf, characteristicLength=10.0, gmsh=None):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, GeoDataFrame):
            raise IllegalArgumentTypeException(inputGdf, 'GeoDataFrame')
        self.inputGdf = inputGdf

        self.characteristicLength = characteristicLength

        if gmsh is None:
            if path.exists('c:/Program Files (x86)/gmsh-2.11.0/gmsh.exe'):
                self.gmsh = 'c:/Program Files (x86)/gmsh-2.11.0/gmsh.exe'
            elif path.exists('/usr/local/bin/gmsh'):
                self.gmsh = '/usr/local/bin/gmsh'
            elif path.exists('/usr/bin/gmsh'):
                self.gmsh = '/usr/bin/gmsh'
            elif path.exists('/bin/gmsh'):
                self.gmsh = '/bin/gmsh'
            else:
                raise Exception('You must specify Gmsh location!')
        else:
            self.gmsh = gmsh

    def run(self):
        # sys.path.append('d:/bin/gmsh-2.11.0')
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpBasename = '_%d' % (getpid())
            geoTmpFile = '%s/%s.geo' % (tmpdir, tmpBasename)
            mshTmpFile = '%s/%s.msh' % (tmpdir, tmpBasename)

            GeoWriter(self.inputGdf, geoTmpFile, self.characteristicLength, True).run()
            print('GmshTriangulator:: write %s' % geoTmpFile)

            exitStatus = call([self.gmsh, '-2', geoTmpFile], stdin=None, stdout=None, stderr=None, shell=False)
            if 0 == exitStatus:
                print('GmshTriangulator:: gmsh -2 %s' % geoTmpFile)
    
                mshLayer = MshReader(mshTmpFile, self.inputGdf.total_bounds, self.inputGdf.crs).run()
                print('GmshTriangulator:: read %s' % mshTmpFile)
                return mshLayer
