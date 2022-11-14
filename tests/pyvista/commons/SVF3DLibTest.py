'''
Created on 5 sept. 2022

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
import unittest

from geopandas import GeoDataFrame
from numpy import arange, arctan, arctan2, log, pi, sqrt
from pandas import DataFrame
from shapely.affinity import translate
from shapely.geometry import Polygon, LineString
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.GeomLib3D import GeomLib3D
from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
from t4gpd.pyvista.commons.SVF3DLib import SVF3DLib

import matplotlib.pyplot as plt


class SVF3DLibTest(unittest.TestCase):

    def setUp(self):
        h = 10
        self.h, self.f1 = h, Polygon([(0, 0, 0), (0, h, 0), (0, h, h), (0, 0, h)])

    def tearDown(self):
        pass

    def __plot(self, title, X, trios):
        plt.title(title)
        for Y, method, ls in trios:
            if (len(X) == len(Y)):
                plt.plot(X, Y, ls, label=method)
        plt.xlabel('Aspect ratio (H/W)')
        plt.ylabel('View factor')
        plt.grid()
        plt.legend()
        plt.show()

    def __analyticalAlignedParallelSquareFaces(self, h, w):
        '''
        Based on "Appendix D: View Factor Catalogue", (Modest and Mazumder, 2022, p. 932)

        Modest, M. F., and Mazumder, S. (2022). Radiative Heat Transfer. In Academic Press (Ed.), 
        Radiative Heat Transfer (4th Edition). Elsevier. https://doi.org/10.1016/c2018-0-03206-5

        see Section "Identical, parallel, directly opposed rectangles" in
        https://kanamesasaki.github.io/viewfactor/
        '''
        X = Y = h / w
        XX, YY = X ** 2, Y ** 2
        return (2 / (pi * X * Y)) * (
            log(sqrt(((1 + XX) * (1 + YY)) / (1 + XX + YY))) + 
            X * sqrt(1 + YY) * arctan2(X, sqrt(1 + YY)) + 
            Y * sqrt(1 + XX) * arctan2(Y, sqrt(1 + XX)) - 
            X * arctan(X) - 
            Y * arctan(Y)
            )

    def __analyticalPerpendicularRectanglesWithOneCommonEdge(self, h, w, l):
        '''
        Based on "Appendix D: View Factor Catalogue", (Modest and Mazumder, 2022, p. 932)

        Modest, M. F., and Mazumder, S. (2022). Radiative Heat Transfer. In Academic Press (Ed.), 
        Radiative Heat Transfer (4th Edition). Elsevier. https://doi.org/10.1016/c2018-0-03206-5

        see Section "Two rectangles with one common edge and 90$^o$ angle" in
        https://kanamesasaki.github.io/viewfactor/
        '''
        H, W = h / l, w / l
        HH, WW = H ** 2, W ** 2
        return (1 / (pi * W)) * (
            W * arctan2(1, W) + 
            H * arctan2(1, H) - 
            sqrt(HH + WW) * arctan2(1, sqrt(HH + WW)) + 
            0.25 * log(
                ((1 + WW) * (1 + HH)) / (1 + WW + HH)
                * ((WW * (1 + WW + HH)) / ((1 + WW) * (WW + HH))) ** WW
                * ((HH * (1 + WW + HH)) / ((1 + HH) * (WW + HH))) ** HH
                )
            )
    
    def testIsFiveTimeRuleTrue(self):
        epsilon = 1e-6

        w = 5 * sqrt(2) * self.h + epsilon
        f1, f2 = self.f1, translate(self.f1, xoff=w)
        self.assertTrue(SVF3DLib.isFiveTimeRuleTrue(f1, f2), 'Test isFiveTimeRuleTrue (1)')

        w = 5 * sqrt(2) * self.h - epsilon
        f1, f2 = self.f1, translate(self.f1, xoff=w)
        self.assertFalse(SVF3DLib.isFiveTimeRuleTrue(f1, f2), 'Test isFiveTimeRuleTrue (2)')

        '''
        from geopandas import GeoDataFrame
        from t4gpd.pyvista.ToUnstructuredGrid import ToUnstructuredGrid
        gdf = GeoDataFrame([ {'gid':1, 'geometry': f1}, {'gid':2, 'geometry': f2} ])
        ToUnstructuredGrid([gdf], fieldname='gid').run().plot()
        '''

    '''
    def testIsa(self):
        h, f1 = self.h, self.f1

        HW, ISA = [], []
        for w in arange(h, 10 * h, h):
            f2 = GeomLib.reverseRingOrientation(translate(f1, xoff=w))
            _isa = SVF3DLib.isa(f1, f2, optim=None)
            HW.append(h / w)
            ISA.append(_isa)

        self.__plot(HW, [(ISA, 'ISA (without optim.)', 'go--')])

    def testMonteCarlo(self):
        h, f1 = self.h, self.f1

        HW, MC1 = [], []
        for w in arange(h, 10 * h, h):
            f2 = GeomLib.reverseRingOrientation(translate(f1, xoff=w))
            _mc1 = SVF3DLib.monteCarlo(f1, f2, nrays=30000, optim=False)
            HW.append(h / w)
            MC1.append(_mc1)

        self.__plot(HW, [(MC1, 'Monte Carlo (without optim.)', 'cP-.')])
    '''

    def testSvfs1(self):
        #return  #############################################################
        nrays1, nrays2 = 5000, 1000
        h, f1 = self.h, self.f1

        for W in [arange(h, 10 * h, h), arange(0.1 * h, h, 0.1 * h)]:
            HW, ISA1, ISA2, ISA3, ISA4, MC1, MC2, MC3, ANALYTICAL = [], [], [], [], [], [], [], [], []
            for w in W:
                f2 = GeomLib.reverseRingOrientation(translate(f1, xoff=w))
                _isa1 = SVF3DLib.isa(f1, f2, optim=None)
                _isa2 = SVF3DLib.isa(f1, f2, optim='left')
                _isa3 = SVF3DLib.isa(f1, f2, optim='right')
                if (h <= w):
                    _isa4 = SVF3DLib.isa(f1, f2, optim='both')
                _mc1 = SVF3DLib.monteCarlo(f1, f2, nrays=nrays1, optim=False)
                _mc2 = SVF3DLib.monteCarlo(f1, f2, nrays=nrays1, optim=True)
                _mc3 = SVF3DLib.monteCarlo(f1, f2, nrays=nrays2, optim=False)
                _analytical = self.__analyticalAlignedParallelSquareFaces(h, w)
                HW.append(h / w)
                ISA1.append(_isa1)
                ISA2.append(_isa2)
                ISA3.append(_isa3)
                if (h <= w):
                    ISA4.append(_isa4)
                MC1.append(_mc1)
                MC2.append(_mc2)
                MC3.append(_mc3)
                ANALYTICAL.append(_analytical)

            self.__plot(
                'View factor between aligned parallel square faces',
                HW, [
                    (ISA1, 'ISA (without optim.)', 'go--'),
                    (ISA2, 'ISA (optim=left)', 'b*:'),
                    (ISA3, 'ISA (optim=right)', 'm*:'),
                    (ISA4, 'ISA (optim=both)', 'y*-'),
                    (MC1, f'Monte Carlo ({nrays1} nrays, without optim.)', 'cD:'),
                    (MC2, f'Monte Carlo ({nrays1} nrays, with optim.)', 'cD-'),
                    (MC3, f'Monte Carlo ({nrays2} nrays, without optim.)', 'mD--'),
                    (ANALYTICAL, 'Analytical solution', 'rP:'),
                    ])

    def testSvfs2(self):
        #return  #############################################################
        '''
        see Section "Two rectangles with one common edge and 90$^o$ angle" in
        https://kanamesasaki.github.io/viewfactor/
        '''
        nrays1, nrays2 = 5000, 1000
        h, w, l = 10, 10, 10
        for W in [arange(h, 10 * h, h), arange(0.1 * h, h, 0.1 * h)]:
            HW, ISA1, ISA2, ISA3, MC1, MC2, MC3, ANALYTICAL = [], [], [], [], [], [], [], []
            for w in W:
                f1 = Polygon([(0, 0, 0), (w, 0, 0), (w, l, 0), (0, l, 0)])
                f2 = Polygon([(0, 0, 0), (0, l, 0), (0, l, h), (0, 0, h)])

                _isa1 = SVF3DLib.isa(f1, f2, optim=None)
                _isa2 = SVF3DLib.isa(f1, f2, optim='left')
                _isa3 = SVF3DLib.isa(f1, f2, optim='right')
                _mc1 = SVF3DLib.monteCarlo(f1, f2, nrays=nrays1, optim=False)
                _mc2 = SVF3DLib.monteCarlo(f1, f2, nrays=nrays1, optim=True)
                _mc3 = SVF3DLib.monteCarlo(f1, f2, nrays=nrays2, optim=False)

                HW.append(h / w)
                ISA1.append(_isa1)
                ISA2.append(_isa2)
                ISA3.append(_isa3)
                MC1.append(_mc1)
                MC2.append(_mc2)
                MC3.append(_mc3)
                ANALYTICAL.append(self.__analyticalPerpendicularRectanglesWithOneCommonEdge(h, w, l))

            self.__plot(
                'View factor between two perpendicular rectangles with one common edge',
                HW, [
                    (ISA1, 'ISA (without optim.)', 'go--'),
                    (ISA2, 'ISA (optim=left)', 'b*:'),
                    (ISA3, 'ISA (optim=right)', 'm*:'),
                    (MC1, f'Monte Carlo ({nrays1} nrays, without optim.)', 'cD:'),
                    (MC2, f'Monte Carlo ({nrays1} nrays, with optim.)', 'cD-'),
                    (MC3, f'Monte Carlo ({nrays2} nrays, without optim.)', 'mD--'),
                    (ANALYTICAL, 'Analytical solution', 'rP:'),
                    ])

    def testSvfs3(self):
        nrays = 5000

        d = 10
        f1 = Polygon([(0, 0, 0), (0, d, 0), (0, d, d), (0, 0, d)])
        f2 = Polygon([(0, 0, 0), (0, 0, d), (d, 0, d), (d, 0, 0)])
        f3 = Polygon([(0, 0, 0), (d, 0, 0), (d, d, 0), (0, d, 0)])
        f4 = GeomLib.reverseRingOrientation(translate(f1, xoff=d))
        f5 = GeomLib.reverseRingOrientation(translate(f2, yoff=d))
        f6 = GeomLib.reverseRingOrientation(translate(f3, zoff=d))

        cube = [f1, f2, f3, f4, f5, f6]
        cube = GeoDataFrame([{'gid': i, 'geometry':f} for i, f in enumerate(cube, start=1)])

        rows = []
        for i, _f2 in enumerate([f2, f3, f4, f5, f6], start=2):
            _isa = SVF3DLib.isa(f1, _f2, optim='left')
            _mc = SVF3DLib.monteCarlo(f1, _f2, nrays=nrays, optim=False)
            _isaError = 100 * ((0.2 - _isa) / 0.2)
            _mcError = 100 * ((0.2 - _mc) / 0.2)
            rows.append({'gid': f'VF[1->{i}]', 'ISA': _isa, f'MC{nrays}': _mc,
                         'IsaError': _isaError, 'McError': _mcError})

        df = DataFrame(data=rows)
        print(df)

        _isaError = 100 * (1 - df.ISA.sum())
        _mcError = 100 * (1 - df[f'MC{nrays}'].sum())
        print(f'1 == sum(VF[1->*]); ISA error={_isaError:.1f}%; MC{nrays} error={_mcError:.1f}%')

        '''
        cube.geometry = cube.geometry.apply(lambda g: GeomLib.reverseRingOrientation(g))
        normals = cube.copy(deep=True)
        normals.gid = 6 - normals.gid
        normals.geometry = normals.geometry.apply(
            lambda g: LineString(GeomLib3D.getFaceNormalVector(g, anchored=True)))
        scene = ToUnstructuredGrid([cube, normals], fieldname='gid').run()
        scene.plot(show_edges=True)
        '''

    def testSubdivideLeft1(self):
        h, f1 = self.h, self.f1
        f2 = translate(f1, xoff=h)
        result = SVF3DLib.subdivideLeft(f1, f2)
        n = len(result)
        gdf = GeoDataFrame(
            [ {'gid':1, 'geometry': f1}, {'gid':2, 'geometry': f2} ] + 
            [ {'gid':1 + i / n, 'geometry': _f} for i, _f in enumerate(result) ]
            )
        scene = ToUnstructuredGrid([gdf], fieldname='gid').run()
        # scene.plot(show_edges=True)

    def testSubdivideLeft2(self):
        h = self.h
        f1 = Polygon([(0, 0, 0), (0, h, 0), (0, 0, h)])
        f2 = translate(f1, xoff=h)
        result = SVF3DLib.subdivideLeft(f1, f2)
        n = len(result)
        gdf = GeoDataFrame(
            [ {'gid':1, 'geometry': f1}, {'gid':2, 'geometry': f2} ] + 
            [ {'gid':1 + i / n, 'geometry': _f} for i, _f in enumerate(result) ]
            )
        scene = ToUnstructuredGrid([gdf], fieldname='gid').run()
        # scene.plot(show_edges=True)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
