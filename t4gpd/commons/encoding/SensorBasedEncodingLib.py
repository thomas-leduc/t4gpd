"""
Created on 16 Oct. 2025

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

from geopandas import GeoDataFrame
from numpy import allclose, arctan2
from pandas import Series, concat
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
    def __commons(
        sensors: GeoDataFrame, buildings: GeoDataFrame, rayLength: float, nRays: int
    ):
        if not isinstance(sensors, GeoDataFrame):
            raise IllegalArgumentTypeException(sensors, "GeoDataFrame")

        if not isinstance(buildings, GeoDataFrame):
            raise IllegalArgumentTypeException(buildings, "GeoDataFrame")

        if not GeoDataFrameLib.shareTheSameCrs(sensors, buildings):
            raise ValueError(
                "sensors and buildings are expected to share the same crs!"
            )

        irays = PanopticRaysLib.get2DGeoDataFrame(sensors, rayLength, nRays)
        orays = OverlayLib.intersection1(buildings, irays, keep_geom_type=False)
        # orays = OverlayLib.intersection2(buildings, irays)
        if ("raylen" not in irays.columns) or ("raylen" != rayLength):
            irays["raylen"] = (
                irays[rayLength] if rayLength in irays.columns else rayLength
            )

        orays["raylen"] = orays.apply(
            lambda row: distance(*nearest_points(row.viewpoint, row.geometry)), axis=1
        )
        return irays, orays

    @staticmethod
    def encode2D(
        sensors: GeoDataFrame,
        buildings: GeoDataFrame,
        rayLength: float = 100.0,
        nRays: int = 64,
    ) -> GeoDataFrame:

        irays, orays = SensorBasedEncodingLib.__commons(
            sensors, buildings, rayLength, nRays
        )

        # Rename ray lengths for the 2D encoding.
        irays.rename(columns={"raylen": "raylen2D"}, inplace=True)
        orays.rename(columns={"raylen": "raylen2D"}, inplace=True)

        # For each ray, keep the closest building intersection.
        idx = orays.groupby(by=["__VPT_ID__", "__RAY_ID__"]).raylen2D.idxmin()
        orays = orays.loc[idx]

        # Restore rays with no building intersection.
        orays = DataFrameLib.fillWithMissingRows(
            orays, irays, on=["__VPT_ID__", "__RAY_ID__"]
        )

        orays.sort_values(by=["__VPT_ID__", "__RAY_ID__"], inplace=True)

        # Aggregate ray lengths into one list per sensor.
        orays = orays.groupby(by="__VPT_ID__").agg({"raylen2D": list})

        # Avoid duplicating an existing output column.
        if "raylen2D" in sensors:
            osensors = concat([sensors.drop(columns="raylen2D"), orays], axis=1)
        else:
            osensors = concat([sensors, orays], axis=1)
        return osensors

    @staticmethod
    def __validate25DParameters(
        sensors: GeoDataFrame,
        buildings: GeoDataFrame,
        elevationFieldname: str,
        h0: float | str,
    ) -> None:
        if elevationFieldname not in buildings.columns:
            raise ValueError(f"{elevationFieldname!r} is not a relevant field name!")

        if isinstance(h0, str):
            if h0 not in sensors.columns:
                raise ValueError(f"{h0!r} is not a valid field name in sensors.")
        elif not isinstance(h0, (int, float)):
            raise TypeError(
                f"h0 must be either a number or a column name (str), "
                f"got {type(h0).__name__}."
            )

    @staticmethod
    def __encode25D(
        irays: GeoDataFrame,
        orays: GeoDataFrame,
        elevationFieldname: str,
        h0: float | str,
    ) -> GeoDataFrame:
        """Compute the 25D encoding from input and output rays."""

        irays = irays.rename(columns={"raylen": "raylen25D"}).copy()
        orays = orays.rename(columns={"raylen": "raylen25D"}).copy()

        # If h0 is a column name, the corresponding sensor attribute
        # has been propagated to the rays by get2DGeoDataFrame().
        h0_values = orays[h0] if isinstance(h0, str) else h0

        # Keep only building intersections located above the viewpoint.
        orays.drop(
            index=orays[orays[elevationFieldname] <= h0_values].index,
            inplace=True,
        )

        # Compute the height-to-distance ratio used to select the
        # highest angular obstruction along each ray.
        orays["h_over_w"] = (orays[elevationFieldname] - h0_values) / orays["raylen25D"]

        # For each ray, keep the obstruction with the largest
        # height-to-distance ratio. In case of equality, keep
        # the closest obstruction.
        idx = (
            orays.sort_values(
                ["h_over_w", "raylen25D"],
                ascending=[False, True],
            )
            .groupby(
                ["__VPT_ID__", "__RAY_ID__"],
                as_index=False,
            )
            .head(1)
            .index
        )
        orays = orays.loc[idx]

        # Compute the vertical angle of the selected obstruction.
        h0_selected = (
            h0_values.loc[orays.index] if isinstance(h0_values, Series) else h0_values
        )

        orays["angles"] = arctan2(
            orays[elevationFieldname] - h0_selected,
            orays["raylen25D"],
        )

        # Restore rays with no building intersection.
        orays = DataFrameLib.fillWithMissingRows(
            orays,
            irays,
            on=["__VPT_ID__", "__RAY_ID__"],
        )

        # A missing intersection means that the ray is unobstructed.
        idx = orays["h_over_w"].isna()
        orays.loc[idx, elevationFieldname] = 0
        orays.loc[idx, "h_over_w"] = 0
        orays.loc[idx, "angles"] = 0

        orays.sort_values(
            by=["__VPT_ID__", "__RAY_ID__"],
            inplace=True,
        )

        # Aggregate ray-based values into one list per sensor.
        return orays.groupby(by="__VPT_ID__").agg(
            {
                elevationFieldname: list,
                "raylen25D": list,
                "h_over_w": list,
                "angles": list,
            }
        )

    @staticmethod
    def encode25D(
        sensors: GeoDataFrame,
        buildings: GeoDataFrame,
        elevationFieldname: str = "HAUTEUR",
        h0: float | str = 0,
        rayLength: float = 100.0,
        nRays: int = 64,
    ) -> GeoDataFrame:
        SensorBasedEncodingLib.__validate25DParameters(
            sensors, buildings, elevationFieldname, h0
        )

        irays, orays = SensorBasedEncodingLib.__commons(
            sensors, buildings, rayLength, nRays
        )

        orays = SensorBasedEncodingLib.__encode25D(
            irays,
            orays,
            elevationFieldname,
            h0,
        )

        # Remove intermediate/output columns already present in sensors
        # to avoid useless or duplicate column names in the final GeoDataFrame
        colsToDrop = [
            col
            for col in [elevationFieldname, "raylen25D", "h_over_w", "angles"]
            if col in sensors
        ]
        _sensors = sensors.drop(columns=colsToDrop) if colsToDrop else sensors
        osensors = concat([_sensors, orays], axis=1)
        return osensors

    @staticmethod
    def encode2D25D(
        sensors: GeoDataFrame,
        buildings: GeoDataFrame,
        elevationFieldname: str = "HAUTEUR",
        h0: float | str = 0,
        rayLength: float = 100.0,
        nRays: int = 64,
    ) -> GeoDataFrame:
        SensorBasedEncodingLib.__validate25DParameters(
            sensors, buildings, elevationFieldname, h0
        )

        irays, orays = SensorBasedEncodingLib.__commons(
            sensors, buildings, rayLength, nRays
        )

        # ==================== 2D ====================
        irays2D = irays.rename(columns={"raylen": "raylen2D"}).copy()
        orays2D = orays.rename(columns={"raylen": "raylen2D"}).copy()

        # Keep the closest building intersection for each ray.
        idx = orays2D.groupby(["__VPT_ID__", "__RAY_ID__"])["raylen2D"].idxmin()
        orays2D = orays2D.loc[idx]

        # Restore rays with no building intersection.
        orays2D = DataFrameLib.fillWithMissingRows(
            orays2D,
            irays2D,
            on=["__VPT_ID__", "__RAY_ID__"],
        )

        orays2D.sort_values(
            by=["__VPT_ID__", "__RAY_ID__"],
            inplace=True,
        )
        orays2D = orays2D.groupby(by="__VPT_ID__").agg({"raylen2D": list})

        # Avoid duplicating an existing output column.
        osensors = (
            sensors.drop(columns="raylen2D")
            if "raylen2D" in sensors.columns
            else sensors
        )
        osensors = concat(
            [osensors, orays2D],
            axis=1,
        )

        # ==================== 25D ====================
        orays25D = SensorBasedEncodingLib.__encode25D(
            irays,
            orays,
            elevationFieldname,
            h0,
        )

        colsToDrop = [
            col
            for col in [elevationFieldname, "raylen25D", "h_over_w", "angles"]
            if col in osensors.columns
        ]

        if colsToDrop:
            osensors = osensors.drop(columns=colsToDrop)

        osensors = concat([osensors, orays25D], axis=1)

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

    def test4():
        import matplotlib.pyplot as plt
        from shapely import Point
        from t4gpd.commons.encoding.EncodingIndices import EncodingIndices
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        dw = 10
        h0 = 1.1
        buildings = GeoDataFrameDemos.regularGridOfPlots(2, 2, dw=dw)
        buildings = buildings.head(3)
        buildings["HAUTEUR"] = dw
        sensors = GeoDataFrame(
            [{"gid": 1, "geometry": Point(0, 0, h0)}], crs=buildings.crs
        )

        rayLength = 100.0
        nRays = 360
        projectionName = "Stereographic"
        size = dw

        osensors = SensorBasedEncodingLib.encode25D(
            sensors, buildings, "HAUTEUR", h0, rayLength, nRays
        )
        osensors = EncodingIndices.svf_indices(osensors, "angles")
        print(osensors[["geometry", "svf_geom", "svf_rad"]])

        smaps = SkymapBuilder.build(
            osensors, "angles", projectionName, size, epsilon=0.1
        )

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_title(f"h0 = {h0} m", fontsize=20)
        buildings.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.1)
        osensors.plot(ax=ax, color="black", marker="P")
        osensors.apply(
            lambda x: ax.annotate(
                text=f"geom={x.svf_geom:.3f}\n\nrad={x.svf_rad:.3f}",
                xy=x.geometry.coords[0][:2],
                color="black",
                size=12,
                ha="center",
                va="center",
            ),
            axis=1,
        )
        smaps.plot(ax=ax, color="red", linewidth=0.5)
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return osensors

    def test5():
        import matplotlib.pyplot as plt
        from geopandas import sjoin
        from t4gpd.commons.PointsInPolygonsLib import PointsInPolygonsLib
        from t4gpd.commons.encoding.EncodingIndices import EncodingIndices
        from t4gpd.commons.encoding.SkymapBuilder import SkymapBuilder
        from t4gpd.commons.grid.FastGridLib import FastGridLib
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        dx, rayLength, nRays = 100, 45, 64

        buildings = GeoDataFrameDemos.ensaNantesBuildings()
        sensors = FastGridLib.grid(
            buildings, dx, dy=None, intoPoint=True, withRowsCols=False
        )
        sensors = sjoin(
            sensors,
            buildings[["HAUTEUR", "geometry"]].rename(columns={"HAUTEUR": "h0"}),
            how="left",
            predicate="within",
        )
        sensors.drop(columns=["index_right"], inplace=True)
        sensors["h0"] = sensors["h0"].fillna(0)
        # sensors = PointsInPolygonsLib.indoors(sensors, buildings)

        h0 = 0.0
        h0 = "h0"
        sensors = SensorBasedEncodingLib.encode2D25D(
            sensors, buildings, "HAUTEUR", h0, rayLength, nRays
        )
        sensors = EncodingIndices.svf_indices(sensors, angles="angles")

        projectionName, size = "Stereographic", 10
        smaps = SkymapBuilder.build(
            sensors, "angles", projectionName, size, epsilon=0.1
        )

        # MAPPING
        fig, ax = plt.subplots(figsize=(10, 10))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.1)
        smaps.plot(ax=ax, color="yellow", edgecolor="orange", alpha=0.8)
        sensors.plot(ax=ax, color="black", marker="+")
        sensors.apply(
            lambda x: ax.annotate(
                text=f"{x.h0:.2f}\n{x.svf_geom:.3f}",
                xy=x.geometry.coords[0],
                color="black",
                size=12,
                ha="right",
                va="top",
            ),
            axis=1,
        )
        ax.axis("off")

        fig.tight_layout()
        plt.show()
        plt.close(fig)
        return sensors


# SensorBasedEncodingLib.test()
# SensorBasedEncodingLib.test2()
# SensorBasedEncodingLib.test3()
# osensors = SensorBasedEncodingLib.test4()
# sensors = SensorBasedEncodingLib.test5()
