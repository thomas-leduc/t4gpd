"""
Created on 27 Apr. 2026

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

import numpy as np
from geopandas import GeoDataFrame
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class GeographicallyWeightedCorrelationLib(object):
    """
    classdocs
    """

    @staticmethod
    def __build_knn_sparse(coords, k=10, sigma="adaptive"):
        """
        Returns sparse weight matrix W (CSR)
        """
        n = coords.shape[0]

        nn = NearestNeighbors(n_neighbors=k + 1, algorithm="kd_tree")
        nn.fit(coords)

        distances, indices = nn.kneighbors(coords)

        # FLATTEN STRUCTURE
        row_idx = np.repeat(np.arange(n), k + 1)
        col_idx = indices.flatten()
        dist = distances.flatten()

        # poids gaussiens locaux
        if sigma == "adaptive":
            # sigma = np.median(dist)
            # EXCLUDE SELF-DISTANCE (= 0, ONE PER POINT)
            self_mask = np.ones(len(dist), dtype=bool)
            self_mask[np.arange(n) * (k + 1)] = False
            sigma = np.median(dist[self_mask])  # CORRECTED

        weights = np.exp(-(dist**2) / (sigma**2))

        W = csr_matrix((weights, (row_idx, col_idx)), shape=(n, n))

        # LINE NORMALIZATION
        W = W.multiply(1 / W.sum(axis=1).A1[:, None])

        return W

    def gwc(gdf, colA, colB, k=10):
        """
        Geographically Weighted Correlation
        """
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if colA not in gdf:
            raise Exception(f"{colA} is not a relevant field name!")
        if colB not in gdf:
            raise Exception(f"{colB} is not a relevant field name!")
        if gdf[colA].isnull().any() or gdf[colB].isnull().any():
            raise ValueError(f"The '{colA}' or '{colB}' columns contain NaNs.")

        coords = np.array([(geom.x, geom.y) for geom in gdf.geometry])
        A = gdf[colA].values.astype(float)
        B = gdf[colB].values.astype(float)

        # sparse weights
        W = GeographicallyWeightedCorrelationLib.__build_knn_sparse(coords, k=k)

        # local means (streaming via sparse matvec)
        A_mean = W @ A
        B_mean = W @ B

        # centered variables
        # A_c = A - A_mean
        # B_c = B - B_mean

        # local covariance & variances
        # cov = W @ (A_c * B_c)
        # varA = W @ (A_c ** 2)
        # varB = W @ (B_c ** 2)

        # Huygens' identity — correct centering through the focal point i
        # cov = (W @ (A * B)) - A_mean * B_mean
        # varA = np.maximum(0.0, (W @ (A**2)) - A_mean**2)  # CORRECTED
        # varB = np.maximum(0.0, (W @ (B**2)) - B_mean**2)  # CORRECTED

        rows, cols = W.nonzero()
        weights = W.data

        cov = np.zeros(len(A))
        varA = np.zeros(len(A))
        varB = np.zeros(len(A))

        for idx in range(len(weights)):
            i = rows[idx]
            j = cols[idx]
            w = weights[idx]

            da = A[j] - A_mean[i]
            db = B[j] - B_mean[i]

            cov[i] += w * da * db
            varA[i] += w * da**2
            varB[i] += w * db**2

        denom = np.sqrt(varA * varB)

        r = np.divide(
            cov, denom, out=np.full_like(cov, np.nan, dtype=float), where=denom > 0
        )

        return np.asarray(r).ravel()

    def gwc_with_pvalues(gdf, colA, colB, k=10, n_perm=199):
        """
        Geographically Weighted Correlation with permutation-based p-values

        Parameters
        ----------
        gdf    : GeoDataFrame with point geometry (projected CRS recommended)
        colA   : name of the first column (variable A)
        colB   : name of the second column (variable B)
        k      : number of neighbors for KNN weights
        n_perm : number of permutations (>= 999 recommended for p < 0.01)

        Returns
        -------
        r_obs : ndarray (n,) --- observed local correlations
        p     : ndarray (n,) --- two-sided permutation p-values
        """
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")
        if colA not in gdf:
            raise Exception(f"{colA} is not a relevant field name!")
        if colB not in gdf:
            raise Exception(f"{colB} is not a relevant field name!")
        if gdf[colA].isnull().any() or gdf[colB].isnull().any():
            raise ValueError(f"The '{colA}' or '{colB}' columns contain NaNs.")

        coords = np.array([(geom.x, geom.y) for geom in gdf.geometry])
        A = gdf[colA].values.astype(float)
        B = gdf[colB].values.astype(float)

        # poids calculés une seule fois
        W = GeographicallyWeightedCorrelationLib.__build_knn_sparse(coords, k=k)

        def compute_r(A, B):
            W_dense = W.toarray()  # (n, n)

            # Moyennes locales propres à chaque point focal i
            A_mean = W_dense @ A  # shape (n,)
            B_mean = W_dense @ B  # shape (n,)

            # Déviations : A_dev[i, j] = A[j] - A_mean[i]
            A_dev = A[np.newaxis, :] - A_mean[:, np.newaxis]  # (n, n)
            B_dev = B[np.newaxis, :] - B_mean[:, np.newaxis]  # (n, n)

            # Covariance et variances locales pondérées
            cov = np.einsum("ij,ij,ij->i", W_dense, A_dev, B_dev)
            varA = np.einsum("ij,ij->i", W_dense, A_dev**2)
            varB = np.einsum("ij,ij->i", W_dense, B_dev**2)

            denom = np.sqrt(varA * varB)
            r = np.where(denom < 1e-10, np.nan, cov / denom)
            return r

        r_obs = compute_r(A, B)

        n = len(A)
        r_perm = np.zeros((n_perm, n))

        for i in range(n_perm):
            B_perm = np.random.permutation(B)
            r_perm[i] = compute_r(A, B_perm)

        p = (np.sum(np.abs(r_perm) >= np.abs(r_obs), axis=0) + 1) / (n_perm + 1)

        return r_obs, p

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from numpy.random import default_rng
        from shapely import points

        rng = default_rng(1234)
        n = 200
        x, y, A = rng.normal(size=(3, n))
        x *= 100
        y *= 100
        B = np.zeros(n)

        # ZONE 1: CORRELATION
        mask = x < 120
        B[mask] = A[mask] + rng.normal(loc=0, scale=0.01, size=mask.sum())

        # zone 2: NOISE
        B[~mask] = rng.normal(loc=0, scale=0.1, size=(~mask).sum())

        gdf = GeoDataFrame({"A": A, "B": B}, geometry=points(x, y))

        r = GeographicallyWeightedCorrelationLib.gwc(gdf, "A", "B", k=10)
        gdf["gwc"] = r

        assert np.nanmean(r[mask]) > np.nanmean(r[~mask])
        assert np.all((r >= -1) & (r <= 1) | np.isnan(r))

        # PLOTTING
        fig, ax = plt.subplots(figsize=(12, 8))
        gdf.plot(ax=ax, column="gwc", cmap="RdBu_r", legend=True, vmin=-1, vmax=1)
        gdf.apply(
            lambda x: ax.annotate(
                text=f"{x.gwc:.2}",
                xy=x.geometry.coords[0],
                color="black",
                size=8,
                ha="left",
                va="top",
            ),
            axis=1,
        )
        ax.grid()
        fig.tight_layout()
        # plt.savefig("/tmp/gwc.pdf")
        plt.show()
        plt.close(fig)
        return gdf

    @staticmethod
    def test2():
        import matplotlib.pyplot as plt
        from numpy.random import default_rng
        from shapely import points

        rng = default_rng(1234)
        n = 200
        x, y, A = rng.normal(size=(3, n))
        x *= 100
        y *= 100
        B = np.zeros(n)

        # ZONE 1: CORRELATION
        mask = x < 120
        B[mask] = A[mask] + rng.normal(loc=0, scale=0.01, size=mask.sum())

        # zone 2: NOISE
        B[~mask] = rng.normal(loc=0, scale=0.1, size=(~mask).sum())

        gdf = GeoDataFrame({"A": A, "B": B}, geometry=points(x, y))

        r, p = GeographicallyWeightedCorrelationLib.gwc_with_pvalues(
            gdf, "A", "B", k=10
        )
        gdf["gwc"] = r
        gdf["gwc_pvalues"] = p

        assert np.nanmean(r[mask]) > np.nanmean(r[~mask])
        assert np.all((r >= -1) & (r <= 1) | np.isnan(r))

        # PLOTTING
        fig, ax = plt.subplots(figsize=(12, 8))
        gdf.plot(ax=ax, column="gwc", cmap="RdBu_r", legend=True, vmin=-1, vmax=1)
        gdf.apply(
            lambda x: ax.annotate(
                text=f"{x.gwc:.2f}\np={x.gwc_pvalues:.3f}",
                xy=x.geometry.coords[0],
                color="black",
                size=8,
                ha="left",
                va="top",
            ),
            axis=1,
        )
        ax.grid()
        fig.tight_layout()
        # plt.savefig("/tmp/gwc.pdf")
        plt.show()
        plt.close(fig)
        return gdf


# gdf = GeographicallyWeightedCorrelationLib.test()
# gdf = GeographicallyWeightedCorrelationLib.test2()
