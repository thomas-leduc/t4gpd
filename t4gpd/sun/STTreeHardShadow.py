"""
Created on 26 aug. 2020

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

import warnings
from datetime import timezone
from geopandas import GeoDataFrame
from shapely import MultiPoint, MultiPolygon, Point
from t4gpd.commons.DatetimeLib import DatetimeLib
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.commons.sun.ShadowLib import ShadowLib
from t4gpd.commons.sun.SunLib import SunLib
from t4gpd.sun.AbstractHardShadow import AbstractHardShadow


class STTreeHardShadow(AbstractHardShadow):
    """
    classdocs
    """

    def __init__(
        self,
        trees,
        datetimes,
        treeHeightFieldname,
        treeCrownRadiusFieldname,
        altitudeOfShadowPlane=0,
        aggregate=False,
        tz=timezone.utc,
        model="pysolar",
        npoints=32,
    ):
        """
        Constructor
        """
        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use STTreeShadow instead")

        if not isinstance(trees, GeoDataFrame):
            raise IllegalArgumentTypeException(trees, "GeoDataFrame")
        self.gdf = trees
        self.crs = trees.crs

        if treeHeightFieldname not in trees:
            raise Exception(f"{treeHeightFieldname} is not a relevant field name!")
        self.treeHeightFieldname = treeHeightFieldname

        if treeCrownRadiusFieldname not in trees:
            raise Exception(f"{treeCrownRadiusFieldname} is not a relevant field name!")
        self.treeCrownRadiusFieldname = treeCrownRadiusFieldname

        self.altitudeOfShadowPlane = altitudeOfShadowPlane
        self.aggregate = aggregate
        sunModel = SunLib(gdf=trees, model=model)

        self.sunPositions = DatetimeLib.fromDatetimesDictToListOfSunPositions(
            datetimes, sunModel, tz
        )

        self.npoints = npoints

    def _auxiliary(self, row, radDir, solarAlti, solarAzim):
        treeGeom = row.geometry
        treeHeight = row[self.treeHeightFieldname]
        treeCrownRadius = row[self.treeCrownRadiusFieldname]

        if isinstance(treeGeom, Point):
            _shadow = ShadowLib.projectSphericalTreeOntoShadowPlane(
                treeGeom,
                treeHeight,
                treeCrownRadius,
                None,
                radDir,
                solarAlti,
                solarAzim,
                self.altitudeOfShadowPlane,
                self.npoints,
            )
            return _shadow

        elif isinstance(treeGeom, MultiPoint):
            _shadows = []
            for g in treeGeom.geoms:
                _shadow = ShadowLib.projectSphericalTreeOntoShadowPlane(
                    g,
                    treeHeight,
                    treeCrownRadius,
                    None,
                    radDir,
                    solarAlti,
                    solarAzim,
                    self.altitudeOfShadowPlane,
                    self.npoints,
                )
                if _shadow is not None:
                    _shadows.append(_shadow)
            return None if (0 == len(_shadows)) else MultiPolygon(_shadows)

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from geopandas import clip
        from matplotlib.colors import ListedColormap
        from pandas import Timestamp
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        # LOAD DATASETS
        trees = GeoDataFrameDemos.districtGraslinInNantesTrees()
        roi = GeoDataFrameDemos.coursCambronneInNantes()
        trees = clip(trees, roi)
        trees = trees.head(1)
        ids = [
            "1937451436",
            "1937451458",
            "1937451469",
            "1937451497",
            "1937451525",
            "1937451548",
            "1937451563",
            "1937451582",
        ]
        h1, a1 = 15.0, 5.0
        h2, a2 = 9.0, 3.0
        trees["h_arbre"] = trees.osm_id.apply(lambda _id: h1 if _id in ids else h2)
        trees["r_houppier"] = trees.osm_id.apply(lambda _id: a1 if _id in ids else a2)

        dts = [
            Timestamp(f"2025-07-21 {h}:00", tz="Europe/Paris").tz_convert("UTC")
            for h in [9, 12, 15]
        ]
        shadows = STTreeHardShadow(
            trees,
            dts,
            treeHeightFieldname="h_arbre",
            treeCrownRadiusFieldname="r_houppier",
            altitudeOfShadowPlane=0.0,
            aggregate=False,
            model="pysolar",
            npoints=32,
        ).run()

        # PLOTTING
        # shadows.datetime = shadows.datetime.apply(lambda dt: dt.strftime("%H:%M"))
        my_cmap = ListedColormap(["red", "green", "blue"])

        fig, ax = plt.subplots(figsize=(1 * 8.26, 1 * 8.26))
        shadows.plot(ax=ax, column="datetime", cmap=my_cmap, alpha=0.25, legend=True)
        trees.plot(ax=ax, color="red")
        roi.boundary.plot(ax=ax, color="red")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

        return trees, shadows, dts


# trees, shadows, dts = STTreeHardShadow.test()
# trees.to_file("/tmp/DEBUG.gpkg", layer="trees1")
# shadows.to_file("/tmp/DEBUG.gpkg", layer="shadows1")
