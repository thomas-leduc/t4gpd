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
from pandas import DataFrame
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from scipy.stats import kendalltau, pearsonr, spearmanr


class CorrelationLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def correlation_with_pvalues(df, method="pearson"):
        def __get_pvalues_dataframe(df, corr, method):
            from numpy import full, isnan, logical_or, nan, sum

            # Return a new array of given shape, filled with nan values
            pval = full(corr.shape, nan)
            for i in range(corr.shape[0]):
                for j in range(i, corr.shape[1]):
                    x = df.iloc[:, i]
                    y = df.iloc[:, j]
                    mask = ~logical_or(isnan(x), isnan(y))
                    if sum(mask) > 0:
                        # Get Pearson correlation p-value
                        pval[i, j] = pval[j, i] = method(x[mask], y[mask])[1]

            pval = DataFrame(pval, columns=corr.columns, index=corr.index)
            return pval

        if not isinstance(df, DataFrame):
            raise IllegalArgumentTypeException(df, "DataFrame")
        if "pearson" == method:
            _method = pearsonr
        elif "kendall" == method:
            _method = kendalltau
        elif "spearman" == method:
            _method = spearmanr
        else:
            raise IllegalArgumentTypeException(
                method, "pearson, kendall or spearman")

        _df = df.select_dtypes("number")
        corr = _df.corr(method=method)
        pval = __get_pvalues_dataframe(_df, corr, method=_method)

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
            Z=[f"z{i}" for i in range(len(df))]
        )

        corr, pval = CorrelationLib.correlation_with_pvalues(df)
        return df, corr, pval


# df, corr, pval = CorrelationLib.test()
