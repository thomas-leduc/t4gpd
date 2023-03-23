'''
Created on 5 janv. 2021

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
from pandas import DataFrame
from sklearn.cluster import KMeans
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class STKMeans(GeoProcess):
    '''
    classdocs
    '''
    NUMERICS = ["int16", "int32", "int64", "float16", "float32", "float64"]

    def __init__(self, inputGdf, nclusters, verbose=True):
        '''
        Constructor
        '''
        if not isinstance(inputGdf, DataFrame):
            raise IllegalArgumentTypeException(inputGdf, "DataFrame")
        self.inputGdf = inputGdf
        self.data = inputGdf.select_dtypes(include=self.NUMERICS)

        if not isinstance(nclusters, int):
            raise IllegalArgumentTypeException(nclusters, "int")
        self.kmeans = KMeans(n_clusters=nclusters, init="k-means++", n_init=10, max_iter=300)

        _fieldnames = list(self.data.columns)
        if (0 == len(_fieldnames)):
            raise Exception("There are no numeric (float) fields in the DataFrame!")
        if verbose:
            print(f"The following fields are taken into account when processing KMeans: {_fieldnames}")

    def run(self):
        _kmeans = self.kmeans.fit(self.data)

        result = self.inputGdf.copy(deep=True)
        result["kmeans_lbl"] = _kmeans.predict(self.data)
        return result
