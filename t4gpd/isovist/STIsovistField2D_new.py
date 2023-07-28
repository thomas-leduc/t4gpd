'''
Created on 24 jul. 2023

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
from geopandas import GeoDataFrame
from shapely import Polygon
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.RayCasting4Lib import RayCasting4Lib


class STIsovistField2D_new(GeoProcess):
    '''
    classdocs
    '''

    def __init__(self, buildings, viewpoints, nRays=64, rayLength=100.0, withIndices=False):
        '''
        Constructor
        '''
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(
                buildings, "buildings GeoDataFrame")
        if not isinstance(viewpoints, GeoDataFrame):
            raise IllegalArgumentTypeException(
                viewpoints, "viewpoints GeoDataFrame")

        if not GeoDataFrameLib.shareTheSameCrs(buildings, viewpoints):
            raise Exception(
                "Illegal argument: buildings and viewpoints must share shames CRS!")

        self.buildings = buildings
        # CLEAN GEOMETRIES
        self.buildings.geometry = self.buildings.geometry.apply(
            lambda g: g.buffer(0))

        self.rays = RayCasting4Lib.get2DPanopticRaysGeoDataFrame(
            viewpoints, rayLength, nRays)
        self.nRays = nRays
        self.withIndices = withIndices

    def __buildIsovist(self, viewpoint, ray_ids, mls):
        _ctrPts1 = [ls.coords[-1] for ls in mls.geoms]
        if (self.nRays == len(_ctrPts1)):
            return Polygon(_ctrPts1)

        viewpoint = viewpoint.coords[0][0:2]
        assert len(ray_ids) == len(_ctrPts1)
        assert ray_ids == sorted(ray_ids)
        _ctrPts2 = []
        for i, ray_id in enumerate(ray_ids):
            if (0 == i):
                if (0 != ray_id):
                    _ctrPts2.append(viewpoint)
                _ctrPts2.append(_ctrPts1[i])
            else:
                if (ray_ids[i-1]+1 < ray_id):
                    _ctrPts2.append(viewpoint)
                _ctrPts2.append(_ctrPts1[i])
        return Polygon(_ctrPts2)

    def run(self):
        isovRaysField = RayCasting4Lib.multipleRayCast2D(
            self.buildings, self.rays)

        if self.withIndices:
            isovRaysField = RayCasting4Lib.addIndicesToIsovRaysField2D(
                isovRaysField)

        isovField = isovRaysField.copy(deep=True)
        # isovField.geometry = isovField.geometry.apply(
        #     lambda mls: Polygon([ls.coords[-1] for ls in mls.geoms]))
        if (0 < len(isovField)):
            isovField.geometry = isovField.apply(lambda row: self.__buildIsovist(
                row.viewpoint, row.__RAY_ID__, row.geometry), axis=1)

        isovRaysField.drop(columns=["__RAY_ID__"], inplace=True)
        isovField.drop(columns=["__RAY_ID__"], inplace=True)
        return isovRaysField, isovField


"""
# buildings = GeoDataFrameDemos.ensaNantesBuildings()
# buildings = GeoDataFrameDemos4.comfortPathInNantesBuildings()
# sensors = STGrid(buildings, 50, dy=None, indoor=False, intoPoint=True).run()
# sensors = sensors.loc[sensors[sensors.gid.isin([86, 100, 117])].index, [
#     "gid", "geometry"]]

buildings = GeoDataFrame([{"gid": x, "geometry": Polygon(
    [(-x, x, h), (x, x, h), (x, x+1, h), (-x, x+1, h)]), "H": h} for x, h in [(4, 4), (8, 8.1), (12, 12.1)]])
sensors = GeoDataFrame([
    {"id": y, "geometry": Point([0, y])} for y in [0, 10, 15]
])

nRays, rayLength = 64, 10.0
isovRaysField, isovField = STIsovistField2D_new(
    buildings, sensors, nRays, rayLength, withIndices=True).run()

_, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
buildings.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.3)
sensors.apply(lambda x: ax.annotate(
    text=x["id"], xy=x.geometry.coords[0],
    color="red", size=12, ha="left", va="top"), axis=1)
isovRaysField.plot(ax=ax, color="blue", linewidth=0.3)
isovField.plot(ax=ax, color="yellow", alpha=0.4)
plt.axis("off")
plt.tight_layout()
plt.show()
"""
