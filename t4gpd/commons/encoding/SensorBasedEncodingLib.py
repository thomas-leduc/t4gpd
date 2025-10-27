"""
Created on 16 Oct. 2025

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

from geopandas import GeoDataFrame
from numpy import allclose, arctan2
from pandas import concat
from shapely import distance
from shapely.ops import nearest_points
from t4gpd.commons.DataFrameLib import DataFrameLib
from t4gpd.commons.GeoDataFrameLib import GeoDataFrameLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.OverlayLib import OverlayLib
from t4gpd.commons.raycasting.PanopticRaysLib import PanopticRaysLib


class SensorBasedEncodingLib(object):
    """
    classdocs
    """

    @staticmethod
    def __commons(sensors, buildings, rayLength, nRays):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")
        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, "GeoDataFrame")
        if not GeoDataFrameLib.shareTheSameCrs(sensors, buildings):
            raise Exception(
                "Illegal argument: sensors and buildings are expected to share the same crs!"
            )
        irays = PanopticRaysLib.get2DGeoDataFrame(sensors, rayLength, nRays)
        orays = OverlayLib.intersection1(buildings, irays, keep_geom_type=False)
        # orays = OverlayLib.intersection2(buildings, irays)
        if ("raylen" not in irays) or ("raylen" != rayLength):
            irays["raylen"] = irays[rayLength] if rayLength in irays else rayLength
        orays["raylen"] = orays.apply(
            lambda row: distance(*nearest_points(row.viewpoint, row.geometry)), axis=1
        )
        return irays, orays

    @staticmethod
    def encode2D(sensors, buildings, rayLength=100.0, nRays=64):
        irays, orays = SensorBasedEncodingLib.__commons(
            sensors, buildings, rayLength, nRays
        )
        irays.rename(columns={"raylen": "raylen2D"}, inplace=True)
        orays.rename(columns={"raylen": "raylen2D"}, inplace=True)

        idx = orays.groupby(by=["__VPT_ID__", "__RAY_ID__"]).raylen2D.idxmin()
        orays = orays.loc[idx]

        orays = DataFrameLib.fillWithMissingRows(
            orays, irays, on=["__VPT_ID__", "__RAY_ID__"]
        )

        orays.sort_values(by=["__VPT_ID__", "__RAY_ID__"], inplace=True)
        orays = orays.groupby(by="__VPT_ID__").agg({"raylen2D": list})

        if "raylen2D" in sensors:
            osensors = concat([sensors.drop(columns="raylen2D"), orays], axis=1)
        else:
            osensors = concat([sensors, orays], axis=1)
        return osensors

    @staticmethod
    def encode25D(
        sensors,
        buildings,
        elevationFieldname="HAUTEUR",
        h0=0,
        rayLength=100.0,
        nRays=64,
    ):
        if elevationFieldname not in buildings:
            raise Exception(f"{elevationFieldname} is not a relevant field name!")

        irays, orays = SensorBasedEncodingLib.__commons(
            sensors, buildings, rayLength, nRays
        )
        irays.rename(columns={"raylen": "raylen25D"}, inplace=True)
        orays.rename(columns={"raylen": "raylen25D"}, inplace=True)

        orays["h_over_w"] = (orays[elevationFieldname] - h0) / orays.raylen25D
        idx = (
            orays.sort_values(["h_over_w", "raylen25D"], ascending=[False, True])
            .groupby(["__VPT_ID__", "__RAY_ID__"], as_index=False)
            .head(1)
            .index
        )
        orays = orays.loc[idx]
        orays["angles"] = arctan2(orays[elevationFieldname], orays.raylen25D)

        orays = DataFrameLib.fillWithMissingRows(
            orays, irays, on=["__VPT_ID__", "__RAY_ID__"]
        )
        idx = orays[orays.h_over_w.isna()].index
        orays.loc[idx, elevationFieldname] = 0
        orays.loc[idx, "h_over_w"] = 0
        orays.loc[idx, "angles"] = 0

        orays.sort_values(by=["__VPT_ID__", "__RAY_ID__"], inplace=True)
        orays = orays.groupby(by="__VPT_ID__").agg(
            {
                elevationFieldname: list,
                "raylen25D": list,
                "h_over_w": list,
                "angles": list,
            }
        )

        colsToDrop = [
            col
            for col in [elevationFieldname, "raylen25D", "h_over_w", "angles"]
            if col in sensors
        ]
        _sensors = sensors.drop(columns=colsToDrop) if 0 < len(colsToDrop) else sensors
        osensors = concat([_sensors, orays], axis=1)
        return osensors

    @staticmethod
    def encode2D25D(
        sensors,
        buildings,
        elevationFieldname="HAUTEUR",
        h0=0,
        rayLength=100.0,
        nRays=64,
    ):
        if elevationFieldname not in buildings:
            raise Exception(f"{elevationFieldname} is not a relevant field name!")

        irays, orays = SensorBasedEncodingLib.__commons(
            sensors, buildings, rayLength, nRays
        )

        # ==================== 2D ====================
        iraysCopy = irays.copy(deep=True)
        oraysCopy = orays.copy(deep=True)
        iraysCopy.rename(columns={"raylen": "raylen2D"}, inplace=True)
        oraysCopy.rename(columns={"raylen": "raylen2D"}, inplace=True)

        idx = oraysCopy.groupby(by=["__VPT_ID__", "__RAY_ID__"]).raylen2D.idxmin()
        oraysCopy = oraysCopy.loc[idx]

        oraysCopy = DataFrameLib.fillWithMissingRows(
            oraysCopy, iraysCopy, on=["__VPT_ID__", "__RAY_ID__"]
        )

        oraysCopy.sort_values(by=["__VPT_ID__", "__RAY_ID__"], inplace=True)
        oraysCopy = oraysCopy.groupby(by="__VPT_ID__").agg({"raylen2D": list})

        if "raylen2D" in sensors:
            osensors = concat([sensors.drop(columns="raylen2D"), oraysCopy], axis=1)
        else:
            osensors = concat([sensors, oraysCopy], axis=1)

        # ==================== 25D ====================
        irays.rename(columns={"raylen": "raylen25D"}, inplace=True)
        orays.rename(columns={"raylen": "raylen25D"}, inplace=True)

        orays["h_over_w"] = (orays[elevationFieldname] - h0) / orays.raylen25D
        idx = (
            orays.sort_values(["h_over_w", "raylen25D"], ascending=[False, True])
            .groupby(["__VPT_ID__", "__RAY_ID__"], as_index=False)
            .head(1)
            .index
        )
        orays = orays.loc[idx]
        orays["angles"] = arctan2(orays[elevationFieldname], orays.raylen25D)

        orays = DataFrameLib.fillWithMissingRows(
            orays, irays, on=["__VPT_ID__", "__RAY_ID__"]
        )
        idx = orays[orays.h_over_w.isna()].index
        orays.loc[idx, elevationFieldname] = 0
        orays.loc[idx, "h_over_w"] = 0
        orays.loc[idx, "angles"] = 0

        orays.sort_values(by=["__VPT_ID__", "__RAY_ID__"], inplace=True)
        orays = orays.groupby(by="__VPT_ID__").agg(
            {
                elevationFieldname: list,
                "raylen25D": list,
                "h_over_w": list,
                "angles": list,
            }
        )
        colsToDrop = [
            col
            for col in [elevationFieldname, "raylen25D", "h_over_w", "angles"]
            if col in sensors
        ]
        _osensors = (
            osensors.drop(columns=colsToDrop) if 0 < len(colsToDrop) else osensors
        )
        osensors = concat([_osensors, orays], axis=1)

        # ==================== allclose(2D, 25D) ====================
        osensors["allclose"] = osensors.apply(
            lambda row: allclose(row.raylen2D, row.raylen25D), axis=1
        )

        return osensors

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.encoding.IsovistBuilder import IsovistBuilder
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.isovist.STIsovistField2D import STIsovistField2D

        dx, rayLength, nRays = 100, 45, 64

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        sensors = FastGridLib.grid(buildings, dx, intoPoint=True, withRowsCols=False)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)

        osensors = SensorBasedEncodingLib.encode2D(sensors, buildings, rayLength, nRays)
        isov = IsovistBuilder.build(osensors, "raylen2D")

        _, ref = STIsovistField2D(buildings, sensors, nRays, rayLength).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))

        buildings.plot(ax=ax, color="lightgrey")
        sensors.plot(ax=ax, color="black", marker="P")
        ref.boundary.plot(ax=ax, color="red", linewidth=1.0)
        isov.plot(ax=ax, color="yellow", alpha=0.5)
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)

    @staticmethod
    def test2():
        import matplotlib.pyplot as plt
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.skymap.STSkyMap25D import STSkyMap25D

        dx, rayLength, nRays = 100, 100, 64
        projectionName, size = "Stereographic", 10
        elevationFieldname, h0 = "HAUTEUR", 0.0

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        sensors = FastGridLib.grid(buildings, dx, intoPoint=True, withRowsCols=False)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)

        osensors = SensorBasedEncodingLib.encode25D(
            sensors, buildings, rayLength=rayLength, nRays=nRays
        )
        osensors = SensorBasedEncodingLib.encode25D(
            sensors, buildings, elevationFieldname, h0, rayLength, nRays
        )
        smaps = SkymapBuilder.build(osensors, "angles", proj=projectionName, size=size)

        ref = STSkyMap25D(
            buildings,
            sensors,
            nRays,
            rayLength,
            elevationFieldname,
            h0=0.0,
            size=size,
            epsilon=1e-1,
            projectionName=projectionName,
            withIndices=False,
            withAngles=True,
        ).run()

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))

        buildings.plot(ax=ax, color="lightgrey")
        sensors.plot(ax=ax, color="black", marker="P")
        ref.boundary.plot(ax=ax, color="red", linewidth=1.0)
        smaps.plot(ax=ax, color="yellow", edgecolor="green", alpha=0.5)
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)

    @staticmethod
    def test3():
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.encoding.IsovistBuilder import IsovistBuilder
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        dx, rayLength, nRays = 100, 50, 64
        elevationFieldname, h0 = "HAUTEUR", 0.0

        buildings = GeoDataFrameDemos.ensaNantesBuildings()

        sensors = FastGridLib.grid(buildings, dx, intoPoint=True, withRowsCols=False)
        sensors = PointsInPolygonsLib.outdoors(sensors, buildings)

        osensors2D = SensorBasedEncodingLib.encode2D(
            sensors, buildings, rayLength=rayLength, nRays=nRays
        )
        osensors25D = SensorBasedEncodingLib.encode25D(
            sensors, buildings, elevationFieldname, h0, rayLength, nRays
        )
        osensors2D25D = SensorBasedEncodingLib.encode2D25D(
            sensors, buildings, elevationFieldname, h0, rayLength, nRays
        )

        assert osensors2D.raylen2D.equals(osensors2D25D.raylen2D)
        assert osensors25D.raylen25D.equals(osensors2D25D.raylen25D)

        isov2D = IsovistBuilder.build(osensors2D25D, "raylen2D", copy=True)
        isov25D = IsovistBuilder.build(osensors2D25D, "raylen25D", copy=True)

        # MAPPING
        my_cmap = ListedColormap(["red", "green"])

        fig, ax = plt.subplots(figsize=(10, 10))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.1)
        # buildings.apply(
        #     lambda x: ax.annotate(
        #         text=f"{x[elevationFieldname]:.1f}",
        #         xy=x.geometry.centroid.coords[0],
        #         color="black",
        #         size=12,
        #         ha="center",
        #     ),
        #     axis=1,
        # )
        osensors2D25D.plot(ax=ax, cmap=my_cmap, column="allclose", marker="P")
        isov2D.boundary.plot(ax=ax, color="green", linewidth=0.5, label="2D")
        isov25D.boundary.plot(ax=ax, color="red", linewidth=0.5, label="25D")
        ax.legend()
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)


# SensorBasedEncodingLib.test()
# SensorBasedEncodingLib.test2()
# SensorBasedEncodingLib.test3()
