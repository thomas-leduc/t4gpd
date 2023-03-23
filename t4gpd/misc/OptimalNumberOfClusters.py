'''
Created on 23 mars 2023

@author: tleduc

Copyright 2020-2023 Thomas Leduc

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
from numpy import asarray, gradient, unique
from pandas import DataFrame
from scipy.cluster.hierarchy import dendrogram, linkage 
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException

import matplotlib.pyplot as plt


class OptimalNumberOfClusters(GeoProcess):
    '''
    classdocs
    '''
    NUMERICS = ["int16", "int32", "int64", "float16", "float32", "float64"]

    def __init__(self, df, method="elbow", maxNumber=10, verbose=True):
        '''
        Constructor
        '''
        if not isinstance(df, DataFrame):
            raise IllegalArgumentTypeException(df, "DataFrame")
        self.df = df
        self.data = df.select_dtypes(include=self.NUMERICS)

        _fieldnames = list(self.data.columns)
        if (0 == len(_fieldnames)):
            raise Exception("There are no numeric fields in the DataFrame!")
        if verbose:
            print(f"The following fields are taken into account: {_fieldnames}")

        if not method in ("elbow", "silhouette", "bic", "dendrogram"):
            raise IllegalArgumentTypeException(method, "'elbow', 'silhouette', 'bic', or 'dendrogram'")
        self.method = method
        self.maxNumber = maxNumber
        self.verbose = verbose
        self.K = range(2, self.maxNumber + 1)
        self.sum_squared_dists = None
        self.silhouette_avg = None

    def _iterate_over_K(self):
        self.sum_squared_dists = []
        self.silhouette_avg = []

        for nclusters in self.K:
            kmeans = KMeans(n_clusters=nclusters, n_init="auto")
            kmeans.fit(self.data)

            self.sum_squared_dists.append(kmeans.inertia_)
            self.silhouette_avg.append(silhouette_score(self.data, kmeans.labels_))

        self.silhouette_avg = asarray(self.silhouette_avg)

    def _elbow(self):
        """
        Finding a "Kneedle" in a Haystack: Detecting Knee Points in System Behavior
        DOI: 10.1109/ICDCSW.2011.20
        https://raghavan.usc.edu//papers/kneedle-simplex11.pdf

        The point of maximum curvature is well-matched to the adhoc methods 
        operators use to select a knee, since curvature is a mathematical 
        measure of how much a function differs from a straight line. 
        """
        if self.sum_squared_dists is None:
            self._iterate_over_K()

        ssd = self.sum_squared_dists
        curvature = gradient(gradient(ssd)) / (1 + gradient(ssd) ** 2) ** 1.5
        nclusters = 1 + curvature.argmax()

        if self.verbose:
            plt.plot(self.K, ssd, "bx-")
            plt.xlabel("Nb of clusters") 
            plt.ylabel("Sum of squared distances / Inertia") 
            plt.title(f"Elbow Method For Optimal k ({nclusters})")
            plt.show()

        return nclusters

    def _silhouette(self):
        if self.silhouette_avg is None:
            self._iterate_over_K()
        nclusters = self.K[self.silhouette_avg.argmax()]

        if self.verbose:
            plt.plot(self.K, self.silhouette_avg, "bx-")
            plt.xlabel("Values of K") 
            plt.ylabel("Silhouette score") 
            plt.title(f"Silhouette analysis For Optimal k ({nclusters})")
            plt.show()

        return nclusters

    def _BICscore(self):
        """
        BAYESIAN INFORMATION CRITERION (BIC) SCORE
        The lower the BIC score, better is the model.
        We can use the BIC score for the Gaussian Mixture Modelling approach for clustering.
        """
        covariance_type = ["spherical", "tied", "diag", "full"]
        scores = []
        for cov in covariance_type:
            for nclusters in self.K:
                gmm = GaussianMixture(n_components=nclusters, covariance_type=cov)
                gmm.fit(self.data)
                scores.append((cov, nclusters, gmm.bic(self.data)))

        scores = DataFrame(scores, columns=["cov_type", "nclusters", "BIC"])
        idx = scores.groupby(by="cov_type").BIC.idxmin()
        scores = scores.loc[idx]
        if self.verbose:
            print(scores)

        return scores.loc[scores.BIC.idxmin(), "nclusters"]

    def _dendrogram(self):
        if self.verbose:
            plt.figure(figsize=(10, 7))  
            plt.title("Dendrogram")  
            dend = dendrogram(linkage(self.data, method='ward'))
            plt.show()
        else:
            dend = dendrogram(linkage(self.data, method='ward'))
        return len(unique(dend["leaves_color_list"]))

    def run(self):
        if ("elbow" == self.method):
            nclusters = self._elbow()
        elif ("silhouette" == self.method):
            nclusters = self._silhouette()
        elif ("bic" == self.method):
            nclusters = self._BICscore()
        elif ("dendrogram" == self.method):
            nclusters = self._dendrogram()

        return DataFrame(data=[{"method": self.method, "nclusters": nclusters}])
