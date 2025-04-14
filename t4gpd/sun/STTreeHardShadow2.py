"""
Created on 10 sept. 2020

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


class STTreeHardShadow2(AbstractHardShadow):
    """
    classdocs
    """

    def __init__(
        self,
        trees,
        datetimes,
        treeHeightFieldname,
        treeCrownHeightFieldname,
        treeUpperCrownRadiusFieldname,
        treeLowerCrownRadiusFieldname,
        altitudeOfShadowPlane=0,
        aggregate=False,
        tz=timezone.utc,
        model="pysolar",
        npoints=32,
    ):
        """
        Constructor
        """
        if not isinstance(trees, GeoDataFrame):
            raise IllegalArgumentTypeException(trees, "GeoDataFrame")

        warnings.formatwarning = WarnUtils.format_Warning_alt
        warnings.warn("Deprecated class: Use STTreeShadow2 instead")

        self.gdf = trees
        self.crs = trees.crs

        if treeHeightFieldname not in trees:
            raise Exception("%s is not a relevant field name!" % (treeHeightFieldname))
        self.treeHeightFieldname = treeHeightFieldname

        if treeCrownHeightFieldname not in trees:
            raise Exception(
                "%s is not a relevant field name!" % (treeCrownHeightFieldname)
            )
        self.treeCrownHeightFieldname = treeCrownHeightFieldname

        if treeUpperCrownRadiusFieldname not in trees:
            raise Exception(
                "%s is not a relevant field name!" % (treeUpperCrownRadiusFieldname)
            )
        self.treeUpperCrownRadiusFieldname = treeUpperCrownRadiusFieldname

        if treeLowerCrownRadiusFieldname not in trees:
            raise Exception(
                "%s is not a relevant field name!" % (treeLowerCrownRadiusFieldname)
            )
        self.treeLowerCrownRadiusFieldname = treeLowerCrownRadiusFieldname

        self.altitudeOfShadowPlane = altitudeOfShadowPlane
        self.aggregate = aggregate
        sunModel = SunLib(gdf=trees, model=model)

        self.sunPositions = DatetimeLib.fromDatetimesDictToListOfSunPositions(
            datetimes, sunModel, tz
        )

        if not (0 == (npoints % 4)):
            raise IllegalArgumentTypeException(npoints, "multiple of 4")
        self.npoints = npoints

    def _auxiliary(self, row, radDir, solarAlti, solarAzim):
        treeGeom = row.geometry
        treeHeight = row[self.treeHeightFieldname]
        treeCrownHeight = row[self.treeCrownHeightFieldname]
        treeUpperCrownRadius = row[self.treeUpperCrownRadiusFieldname]
        treeLowerCrownRadius = row[self.treeLowerCrownRadiusFieldname]

        if isinstance(treeGeom, Point):
            _shadow = ShadowLib.projectConicalTreeOntoShadowPlane(
                treeGeom,
                treeHeight,
                treeCrownHeight,
                treeUpperCrownRadius,
                treeLowerCrownRadius,
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
                _shadow = ShadowLib.projectConicalTreeOntoShadowPlane(
                    g,
                    treeHeight,
                    treeCrownHeight,
                    treeUpperCrownRadius,
                    treeLowerCrownRadius,
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
        trees["h_houppier"] = trees.osm_id.apply(
            lambda _id: 2 * (a1 if _id in ids else a2)
        )
        trees["up_rad"] = trees.osm_id.apply(lambda _id: a1 if _id in ids else a2)
        trees["down_rad"] = trees.osm_id.apply(lambda _id: a1 if _id in ids else a2)

        dts = [
            Timestamp(f"2025-07-21 {h}:00", tz="Europe/Paris").tz_convert("UTC")
            for h in [9, 12, 15]
        ]
        shadows = STTreeHardShadow2(
            trees,
            dts,
            treeHeightFieldname="h_arbre",
            treeCrownHeightFieldname="h_houppier",
            treeUpperCrownRadiusFieldname="up_rad",
            treeLowerCrownRadiusFieldname="down_rad",
            altitudeOfShadowPlane=0.0,
            aggregate=False,
            tz=timezone.utc,
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


# trees, shadows, dts = STTreeHardShadow2.test()
# trees.to_file("/tmp/DEBUG.gpkg", layer="trees1")
# shadows.to_file("/tmp/DEBUG.gpkg", layer="shadows1")
