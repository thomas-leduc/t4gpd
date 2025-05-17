"""
Created on 10 mar. 2025

@author: tleduc

Copyright 2020-2025 Thomas Leduc

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

from numpy import asarray, nan
from shapely import LineString
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.commons.morph.AbstractIndicesLib import AbstractIndicesLib


class LinearRegressionLib(AbstractIndicesLib):
    """
    classdocs
    """

    @staticmethod
    def _getColumns():
        return ["slope", "intercept", "score", "mae", "mse"]

    @staticmethod
    def _indices(row, with_geom=False):
        geom = row.geometry
        result = {
            "slope": nan,
            "intercept": nan,
            "score": nan,
            "mae": nan,
            "mse": nan,
        }
        pts = GeomLib.getListOfShapelyPoints(geom, withoutClosingLoops=True)

        if 1 < len(pts):
            X = asarray([pt.x for pt in pts]).reshape(-1, 1)
            y = asarray([pt.y for pt in pts])
            reg = LinearRegression().fit(X, y)

            y_pred = reg.predict(X)
            slope, intercept = reg.coef_[0], reg.intercept_
            score = reg.score(X, y)
            mae = mean_absolute_error(y, y_pred)
            mse = mean_squared_error(y, y_pred)

            result = {
                "slope": slope,
                "intercept": intercept,
                "score": score,
                "mae": mae,
                "mse": mse,
            }

            if with_geom:
                X_minmax = asarray([X.min(), X.max()]).reshape(-1, 1)
                y_minmax_pred = reg.predict(X_minmax)
                geom = LineString(
                    [
                        (X_minmax[0, 0], y_minmax_pred[0]),
                        (X_minmax[1, 0], y_minmax_pred[1]),
                    ]
                )
                result.update({"geometry": geom})

            return result

        if with_geom:
            result.update({"geometry": LineString()})
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from numpy.random import default_rng
        from shapely import MultiPoint
        from shapely.affinity import rotate
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        rng = default_rng(1234)
        from geopandas import GeoDataFrame

        gdf = GeoDataFrame(
            {
                "geometry": [
                    MultiPoint(
                        rng.normal(
                            loc=[(i, i) for i in range(10)], scale=0.5, size=(10, 2)
                        )
                    )
                ]
            }
        )

        # gdf = GeoDataFrameDemos.theChineseCharacterForReach()
        # gdf = GeoDataFrameDemos.singleBuildingInNantes()
        # gdf.geometry = gdf.geometry.apply(
        #     lambda geom: rotate(geom, angle=-45, origin="center", use_radians=False)
        # )
        lrl = LinearRegressionLib.indices(gdf, with_geom=True, merge_by_index=True)

        fig, ax = plt.subplots()
        gdf.plot(ax=ax, color="grey")
        lrl.plot(ax=ax, color="red")
        ax.axis("square")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return lrl


# lrl = LinearRegressionLib.test()
