"""
Created on 7 May 2026

@author: tleduc

Copyright 2020-2026 Thomas Leduc

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
"""

from pandas import cut, qcut
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans, MiniBatchKMeans
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


class ClusteringLib(object):
    """
    classdocs
    """

    @staticmethod
    def kmeans(df, columns, n_clusters, random_state=None):
        X = df[columns].values

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
        labels = kmeans.fit_predict(X_scaled)

        return labels

    @staticmethod
    def dbscan(df, columns, eps, min_samples):
        X = df[columns].values

        # Perform DBSCAN clustering
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X)

        return labels

    @staticmethod
    def equal_size_bin(df, column, n_clusters, labels=False):
        return qcut(df[column], n_clusters, labels=labels)

    @staticmethod
    def equal_width_bin(df, column, n_clusters, labels=False):
        return cut(df[column], bins=n_clusters, labels=labels)

    @staticmethod
    def gmm(df, columns, n_clusters, covariance_type="full", random_state=None):
        X = df[columns].values

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Perform GMM clustering
        gm = GaussianMixture(
            n_components=n_clusters,
            covariance_type=covariance_type,
            random_state=random_state,
        )
        labels = gm.fit_predict(X_scaled)

        return labels

    @staticmethod
    def agglomerativeClustering(df, columns, n_clusters):
        # https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster_comparison.html
        X = df[columns].values

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Perform agglomerative clustering
        ac = AgglomerativeClustering(
            n_clusters=n_clusters, metric="euclidean", linkage="ward"
        )
        labels = ac.fit_predict(X_scaled)

        return labels

    @staticmethod
    def elbow(df, columns, ofile=None):
        """
        Finding a "Kneedle" in a Haystack: Detecting Knee Points in System Behavior
        DOI: 10.1109/ICDCSW.2011.20
        https://raghavan.usc.edu//papers/kneedle-simplex11.pdf

        The point of maximum curvature is well-matched to the adhoc methods
        operators use to select a knee, since curvature is a mathematical
        measure of how much a function differs from a straight line.
        """
        from matplotlib import pyplot as plt

        X = df[columns].values

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        inertia = []
        k_values = range(1, 11)

        for k in k_values:
            # kmeans = KMeans(n_clusters=k, init='k-means++', random_state=42)
            kmeans = MiniBatchKMeans(n_clusters=k, batch_size=1024, random_state=42)
            kmeans.fit(X_scaled)
            inertia.append(kmeans.inertia_)

        # Plot the Elbow graph
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(k_values, inertia, marker="o", linestyle="--")
        ax.set_xlabel("Number of clusters [-]")
        ax.set_ylabel("Inertia [-]")
        ax.set_title("The Elbow Method for Determining the Optimal Number of Clusters")
        ax.set_xticks(k_values)
        ax.grid()
        fig.tight_layout()
        if ofile:
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)

    @staticmethod
    def silhouette(df, columns, ofile=None):
        """ """
        from matplotlib import pyplot as plt
        from sklearn.metrics import silhouette_score

        X = df[columns].values

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        silhouette_scores = []
        k_values = range(2, 11)

        for k in k_values:
            # kmeans = KMeans(n_clusters=k, init='k-means++', random_state=42)
            kmeans = MiniBatchKMeans(n_clusters=k, batch_size=1024, random_state=42)
            cluster_labels = kmeans.fit_predict(X_scaled)

            # Calculate the silhouette score
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(silhouette_avg)

        # Plot the silhouette graph
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(k_values, silhouette_scores, marker="o", linestyle="--")
        ax.set_xlabel("Number of clusters [-]")
        ax.set_ylabel("Average silhouette score [-]")
        ax.set_title(
            "The Silhouette Method for Determining the Optimal Number of Clusters"
        )
        ax.set_xticks(k_values)
        ax.grid()
        fig.tight_layout()
        if ofile:
            plt.savefig(ofile, bbox_inches="tight")
        else:
            plt.show()
        plt.close(fig)

    @staticmethod
    def _test():
        from geopandas import GeoDataFrame
        from matplotlib import pyplot as plt
        from matplotlib.colors import ListedColormap
        from numpy import asarray
        from numpy.random import default_rng
        from shapely import points

        n = 500
        rng = default_rng(seed=1234)
        centers = asarray([(1, 3), (3, 1), (3, 3)])
        indices = rng.choice(len(centers), size=n)
        xy = rng.normal(loc=centers[indices], scale=0.2)
        gdf = GeoDataFrame(data=xy, columns=["A", "B"], geometry=points(xy))
        gdf["cluster"] = ClusteringLib.kmeans(gdf, ["A", "B"], n_clusters=3)
        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        gdf.plot(
            ax=ax,
            column="cluster",
            cmap=my_cmap,
            categorical=True,
            legend=True,
            marker="+",
            markersize=100,
        )
        ax.grid()
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return gdf

    @staticmethod
    def _test2():
        from geopandas import GeoDataFrame
        from matplotlib import pyplot as plt
        from matplotlib.colors import ListedColormap
        from numpy import cos, sin, pi
        from numpy.random import default_rng
        from shapely import points

        n = 500
        rng = default_rng(seed=1234)
        thetas = rng.uniform(low=0, high=2 * pi, size=n)
        radii = 5 * rng.choice([1, 2, 3], size=n)
        radii = rng.normal(loc=radii, scale=0.25)

        xy = [(x, y) for x, y in zip(radii * cos(thetas), radii * sin(thetas))]
        gdf = GeoDataFrame(data=xy, columns=["A", "B"], geometry=points(xy))
        # gdf["cluster"] = ClusteringLib.kmeans(gdf, ["A", "B"], n_clusters=3)
        gdf["cluster"] = ClusteringLib.dbscan(gdf, ["A", "B"], eps=2.5, min_samples=5)

        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        gdf.plot(
            ax=ax,
            column="cluster",
            cmap=my_cmap,
            categorical=True,
            legend=True,
            marker="+",
            markersize=100,
        )
        ax.grid()
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return gdf

    @staticmethod
    def _test3(equal_width_bin=True):
        from geopandas import GeoDataFrame
        from matplotlib import pyplot as plt
        from matplotlib.colors import ListedColormap
        from numpy.random import default_rng
        from shapely import points

        n = 100
        rng = default_rng(seed=1234)
        xy = rng.normal(loc=[1, 1], scale=[1, 1e-1], size=(n, 2))
        gdf = GeoDataFrame(data=xy, columns=["A", "B"], geometry=points(xy))

        if equal_width_bin:
            gdf["cluster"] = ClusteringLib.equal_width_bin(
                gdf, "A", n_clusters=3, labels=None
            )
        else:
            gdf["cluster"] = ClusteringLib.equal_size_bin(
                gdf, "A", n_clusters=3, labels=None
            )

        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1.3 * 8.26, 0.6 * 8.26))
        ax.axis([-2, 4, 0, 4])
        gdf.plot(
            ax=ax,
            column="cluster",
            cmap=my_cmap,
            categorical=True,
            legend=True,
            marker="+",
            markersize=100,
        )

        df = gdf.groupby(by="cluster", as_index=False).agg({"A": "count"})
        table = ax.table(cellText=df, cellLoc="center", loc="center")
        table.scale(0.8, 0.8)

        ax.grid()
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return gdf

    @staticmethod
    def _test4():
        from geopandas import GeoDataFrame
        from matplotlib import pyplot as plt
        from matplotlib.colors import ListedColormap
        from numpy import array
        from numpy.random import default_rng
        from shapely import points

        n = 3 * 200
        rng = default_rng(seed=1234)

        F = rng.choice([lambda x: -x, lambda x: -x - 2, lambda x: -x + 2], size=n)

        X = rng.uniform(low=[3, 6, 9], high=[9, 12, 15], size=(n // 3, 3)).ravel()

        Y = array([f(x) for f, x in zip(F, X)])
        Y = rng.normal(loc=Y, scale=0.2, size=n)

        xy = [(x, y) for x, y in zip(X, Y)]
        gdf = GeoDataFrame(data=xy, columns=["A", "B"], geometry=points(xy))
        # gdf["cluster"] = ClusteringLib.kmeans(gdf, ["A", "B"], n_clusters=3)
        # gdf["cluster"] = ClusteringLib.dbscan(gdf, ["A", "B"], eps=0.5, min_samples=5)
        gdf["cluster"] = ClusteringLib.gmm(
            gdf,
            ["A", "B"],
            n_clusters=3,
            covariance_type="full",
            # "full", "tied", "diag", "spherical",
        )
        # gdf["cluster"] = ClusteringLib.agglomerativeClustering(
        #     gdf,
        #     ["A", "B"],
        #     n_clusters=3,
        # )

        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        gdf.plot(
            ax=ax,
            column="cluster",
            cmap=my_cmap,
            categorical=True,
            legend=True,
            marker="+",
            markersize=100,
        )
        ax.grid()
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return gdf

    @staticmethod
    def _test5():
        from numpy import asarray
        from numpy.random import default_rng
        from pandas import DataFrame

        n = 500
        rng = default_rng(seed=1234)
        centers = asarray([(1, 3), (3, 1), (3, 3), (5, 0)])
        indices = rng.choice(len(centers), size=n)
        xy = rng.normal(loc=centers[indices], scale=0.2)
        df = DataFrame(data=xy, columns=["A", "B"])
        ClusteringLib.elbow(df, ["A", "B"])
        ClusteringLib.silhouette(df, ["A", "B"])


# gdf = ClusteringLib._test()
# gdf2 = ClusteringLib._test2()
# gdf3 = ClusteringLib._test3(equal_width_bin=True)
# gdf3 = ClusteringLib._test3(equal_width_bin=False)
# gdf4 = ClusteringLib._test4()
# ClusteringLib._test5()
