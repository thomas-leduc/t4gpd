'''
Created on 20 nov. 2024

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
from numpy import asarray
from shapely import LineString
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from t4gpd.commons.GeomLib import GeomLib
from t4gpd.morph.geoProcesses.AbstractGeoprocess import AbstractGeoprocess


class LinearRegressionIndices(AbstractGeoprocess):
    '''
    classdocs
    '''

    def __init__(self, with_geom=False):
        self.with_geom = with_geom

    def runWithArgs(self, row):
        pts = GeomLib.getListOfShapelyPoints(
            row.geometry, withoutClosingLoops=True)

        X = asarray([pt.x for pt in pts]).reshape(-1, 1)
        y = asarray([pt.y for pt in pts])
        reg = LinearRegression().fit(X, y)

        y_pred = reg.predict(X)
        slope, intercept = reg.coef_[0], reg.intercept_
        score = reg.score(X, y)
        mae = mean_absolute_error(y, y_pred)
        mse = mean_squared_error(y, y_pred)

        if self.with_geom:
            X_minmax = asarray([X.min(), X.max()]).reshape(-1, 1)
            y_minmax_pred = reg.predict(X_minmax)
            geom = LineString(
                [(X_minmax[0, 0], y_minmax_pred[0]), (X_minmax[1, 0], y_minmax_pred[0])])

            return {
                "geometry": geom,
                "slope": slope,
                "intercept": intercept,
                "score": score,
                "mae": mae,
                "mse": mse
            }
        return {
            "slope": slope,
            "intercept": intercept,
            "score": score,
            "mae": mae,
            "mse": mse
        }


"""
import matplotlib.pyplot as plt
from geopandas import GeoDataFrame
from shapely import box
from shapely.affinity import rotate
from t4gpd.morph.geoProcesses.STGeoProcess import STGeoProcess

gpd = GeoDataFrame({"geometry": [rotate(box(0, 0, 10, 10), angle=30)]})
op = LinearRegressionIndices(with_geom=True)
gpd2 = STGeoProcess(op, gpd).run()

fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
gpd.boundary.plot(ax=ax, color="black")
gpd2.plot(ax=ax, color="red")
plt.show()
"""
