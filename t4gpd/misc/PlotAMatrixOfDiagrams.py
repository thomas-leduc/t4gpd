'''
Created on 12 nov. 2021

@author: tleduc

Copyright 2020-2021 Thomas Leduc

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
import matplotlib.pyplot as plt
from numpy import inf, max, min, zeros
from t4gpd.commons.GeoProcess import GeoProcess


class PlotAMatrixOfDiagrams(GeoProcess):
    '''
    classdocs
    '''

    def __getYRanges(self, XY):
        _y0, _y1 = inf, -inf
        for k in range(1, len(XY)):
            _y0 = min([_y0, *XY[k]])
            _y1 = max([_y1, *XY[k]])
        return _y0, _y1

    def __init__(self, matrixOfXY, xlim=None, ylim=None, xLbls=None, yLbls=None,
                 suptitle=None, titles=None, bar=False, grid=True, bottom=False,
                 magn=1, outputFile=None):
        '''
        Constructor
        '''
        self.matrixOfXY = matrixOfXY
        self.ncols, self.nrows = len(self.matrixOfXY[0]), len(self.matrixOfXY)
        _COLS, _ROWS = range(self.ncols), range(self.nrows)

        _magn = 0.05
        if isinstance(xlim, (tuple, list)) and (0 == len(xlim)):
            _x0 = min([ min(self.matrixOfXY[l][c][0]) for c in _COLS for l in _ROWS])
            _x1 = max([ max(self.matrixOfXY[l][c][0]) for c in _COLS for l in _ROWS])
            _offX = _magn * (_x1 - _x0)
            xlim = [_x0 - _offX, _x1 + _offX]
        self.xlim = xlim

        if isinstance(ylim, (tuple, list)) and (0 == len(ylim)):
            _y0 = min([ self.__getYRanges(self.matrixOfXY[l][c])[0] for c in _COLS for l in _ROWS ])
            _y1 = max([ self.__getYRanges(self.matrixOfXY[l][c])[1] for c in _COLS for l in _ROWS ])
            _offY = _magn * (_y1 - _y0)
            ylim = [_y0 - _offY, _y1 + _offY]
        self.ylim = ylim

        if isinstance(xLbls, str):
            _matrix = []
            for _l in _ROWS:
                _row = []
                for _c in _COLS:
                    _row.append(xLbls if (self.nrows - 1 == _l) else None)
                _matrix.append(_row)
            xLbls = _matrix
        self.xLbls = xLbls

        if isinstance(yLbls, str):
            _matrix = []
            for _l in _ROWS:
                _row = []
                for _c in _COLS:
                    _row.append(yLbls if (0 == _c) else None)
                _matrix.append(_row)
            yLbls = _matrix
        self.yLbls = yLbls

        self.suptitle = suptitle

        if isinstance(titles, str):
            _matrix = []
            for _l in _ROWS:
                _row = []
                for _c in _COLS:
                    _row.append(titles if (0 == _l) else None)
                _matrix.append(_row)
            titles = _matrix
        self.titles = titles

        self.bar = bar
        self.grid = grid
        self.bottom = bottom
        self.magn = magn * 8.26  # 21 cm ~ 8.26 inches
        self.outputFile = outputFile

    def run(self):
        mainFig = plt.figure(figsize=(self.ncols * self.magn, self.nrows * self.magn))
        mainFig.clear()

        if not self.suptitle is None:
            mainFig.suptitle(self.suptitle)

        for fignum in range(self.nrows * self.ncols):
            nr = fignum // self.ncols
            nc = fignum % self.ncols
            plt.subplot(self.nrows, self.ncols, fignum + 1)  # numrows, numcols, fignum

            _myplot = plt.bar if self.bar else plt.plot

            _bottom = zeros(len(self.matrixOfXY[nr][nc][0]))
            for _k in range(1, len(self.matrixOfXY[nr][nc])):
                _myplot(self.matrixOfXY[nr][nc][0], self.matrixOfXY[nr][nc][_k],
                        bottom=_bottom)
                if self.bottom:
                    _bottom += self.matrixOfXY[nr][nc][_k]

            if not self.titles is None:
                plt.title(self.titles[nr][nc])
            if not self.xLbls is None:
                plt.xlabel(self.xLbls[nr][nc])
            if not self.yLbls is None:
                plt.ylabel(self.yLbls[nr][nc])
            if not self.xlim is None:
                plt.xlim(self.xlim)
            if not self.ylim is None:
                plt.ylim(self.ylim)

            plt.grid(self.grid)

        if self.outputFile is None:
            mainFig.tight_layout()
            plt.show()
        else:
            plt.savefig(self.outputFile, format='pdf', bbox_inches='tight')
        plt.close(mainFig)

'''
'''
from numpy import abs, cos, linspace, pi, sin

nr, nc = 2, 3
n = 50
X = linspace(0, 2 * pi, n)
m = [
    [(X, (l + c) * abs(sin(X)), abs(cos(X))) for c in range(nc)] for l in range(nr)
    ]
PlotAMatrixOfDiagrams(m, xlim=[], ylim=[],
                      xLbls='Absc.', yLbls='Ord.',
                      suptitle='SIN', titles='Sin',
                      bar=True, grid=True, bottom=False,
                      magn=0.25, outputFile=None).run()
'''
'''
