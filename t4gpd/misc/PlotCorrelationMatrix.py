'''
Created on 30 oct. 2024

@author: tleduc

Copyright 2020-2024 Thomas Leduc

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
from numpy import ones_like, triu
from pandas import DataFrame
from t4gpd.commons.CorrelationLib import CorrelationLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class PlotCorrelationMatrix(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, df, tri=True, pval=True, figsize=None,
                 method="pearson", ofile=None):
        '''
        Constructor
        '''
        if not isinstance(df, DataFrame):
            raise IllegalArgumentTypeException(df, "DataFrame")
        self.df = df
        self.tri = tri
        self.pval = pval
        self.figsize = (2.5*8.26, 2.2*8.26) if figsize is None else figsize
        self.method = method
        self.ofile = ofile

    @staticmethod
    def __assign_pvalue_annotations(ax, corr, pval, tri):
        from numpy import isnan, max, min

        # ones_like(): return an array of ones (i.e. True) with the
        # same shape and type as a given array
        # triu(): return a copy of an array with the elements below
        # the k-th diagonal zeroed
        mask_pvalues = triu(ones_like(pval), k=1)

        max_corr, min_corr = max(corr.max()), min(corr.min())

        for i in range(pval.shape[0]):
            for j in range(pval.shape[1]):
                if mask_pvalues[i, j]:
                    p_value = pval.iloc[i, j]
                    if not isnan(p_value):
                        corr_value = corr.iloc[i, j]
                        text_color = "black" if ((min_corr + 0.36) <= corr_value <= (
                            max_corr - 0.4)) else "white"

                        label = f"(p = {p_value:.2f})"
                        if p_value <= 0.01:
                            # include double asterisks for p-value <= 0.01
                            label += "**"
                        elif p_value <= 0.05:
                            # include single asterisk for p-value <= 0.05
                            label += "*"
                        ax.text(i + 0.5, j + 0.8, label,
                                ha="center", va="center",
                                fontsize=8, color=text_color)
                        if not tri:
                            ax.text(j + 0.5, i + 0.8, label,
                                    ha="center", va="center",
                                    fontsize=8, color=text_color)

    def __plot(self, corr, pval):
        import matplotlib.pyplot as plt
        from seaborn import heatmap

        if self.tri:
            # ones_like(): return an array of ones (i.e. True) with the
            # same shape and type as a given array
            # triu(): return a copy of an array with the elements below
            # the k-th diagonal zeroed
            mask = triu(ones_like(corr, dtype=bool), k=1)
        else:
            mask = None

        fig, ax = plt.subplots(figsize=self.figsize)

        # Create the Correlation Heatmap
        # Data will not be shown in cells where mask is True
        heatmap = heatmap(corr,
                          annot=True,
                          annot_kws={"fontsize": 10},
                          fmt=".2f",
                          linewidths=0.5,
                          cmap="RdBu",
                          mask=mask,
                          ax=ax)
        # Assign p-value annotations with asterisks for significance
        if self.pval:
            PlotCorrelationMatrix.__assign_pvalue_annotations(
                ax, corr, pval, self.tri)

        if self.ofile is None:
            plt.show()
        else:
            plt.savefig(self.ofile, bbox_inches="tight")
        plt.close(fig)

    def run(self):
        # https://tosinharold.medium.com/enhancing-correlation-matrix-heatmap-plots-with-p-values-in-python-41bac6a7fd77
        corr, pval = CorrelationLib.correlation_with_pvalues(
            self.df, method=self.method)

        self.__plot(corr, pval)
        return corr, pval

    @staticmethod
    def test():
        from numpy.random import default_rng

        nrows, rng = 10, default_rng(123)
        df = DataFrame(
            data=rng.uniform(low=0, high=1, size=(nrows, 4)),
            columns=["X1", "X2", "X3", "X4"])
        df = df.assign(
            Y1=lambda row: (10 * row.X1 + 0.5 * row.X2 + 0.4 * row.X3) / 10.9,
            Y2=lambda row: (10 * row.X1 + 1.5 * row.X2 + 1.4 * row.X4) / 12.9,
        )

        PlotCorrelationMatrix(df, tri=True, ofile=None).run()
        return df


# df = PlotCorrelationMatrix.test()
