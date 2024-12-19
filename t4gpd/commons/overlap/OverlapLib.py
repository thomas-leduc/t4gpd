'''
Created on 23 aug. 2024

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
from geopandas import GeoDataFrame, sjoin
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.morph.STPolygonize import STPolygonize


class OverlapLib(object):
    '''
    classdocs
    '''

    @staticmethod
    def overlap(gdf, fieldnames, patchid="__PATCH_ID__"):
        if not isinstance(gdf, GeoDataFrame):
            raise IllegalArgumentTypeException(gdf, "GeoDataFrame")

        if (fieldnames is None) or (0 == len(fieldnames)):
            raise IllegalArgumentTypeException(
                fieldnames, "non empty list of fieldnames")
            # raise IllegalArgumentTypeException(
            #     fieldnames, "non empty list of primary keys")

        for fieldname in fieldnames:
            if (fieldname not in gdf):
                raise IllegalArgumentTypeException(
                    fieldname, "fieldname of gdf")
            # if ((pk not in gdf) or (pk in gdf) and (not gdf[pk].is_unique)):
                # raise IllegalArgumentTypeException(pk, "primary key of gdf")

        if patchid in gdf:
            raise IllegalArgumentTypeException(
                patchid, "fieldname unknown to gdf")

        patches = STPolygonize(gdf, patchid=patchid).run()

        representative_points = patches.copy(deep=True)
        representative_points.geometry = representative_points.geometry.apply(
            lambda geom: geom.representative_point())

        result = sjoin(representative_points, gdf,
                       how="inner", predicate="within")

        result = result.groupby(by=patchid, as_index=False).agg(
            {fieldname: list for fieldname in fieldnames})
        if "noverlays" not in result:
            result["noverlays"] = result[fieldnames[0]].apply(lambda v: len(v))

        result = result.merge(patches, on=patchid)
        result = GeoDataFrame(result, crs=gdf.crs, geometry="geometry")
        return result

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from datetime import datetime, timedelta, timezone
        from matplotlib.colors import ListedColormap
        from shapely import box

        dt0 = datetime(2024, 8, 23, 12, tzinfo=timezone.utc)
        gdf = GeoDataFrame([
            {"gid": 100+i, "geometry": box(0, 0, i, i),
             "timestamp": (dt0 + timedelta(hours=i)).time()}
            for i in range(1, 4)
        ])
        result = OverlapLib.overlap(
            gdf, ["gid", "timestamp"], patchid="patch_id")
        print(result)

        # MAPPING
        my_rgb_cmap = ListedColormap(["blue", "green", "red"])

        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(
            1.6 * 8.26, 0.8 * 8.26), squeeze=False)

        ax = axes[0, 0]
        gdf.plot(ax=ax, column="gid", alpha=0.3, cmap=my_rgb_cmap)
        ax.axis("off")

        ax = axes[0, 1]
        # gdf.plot(ax=ax, column="gid", alpha=0.3, cmap=my_rgb_cmap)
        HATCHES = ["o", ".", "x"]
        for i, patch_id in enumerate(result.patch_id.unique()):
            result[result.patch_id == patch_id].boundary.plot(
                ax=ax, hatch=HATCHES[i])
        ax.axis("off")

        plt.tight_layout()
        plt.show()
        plt.close(fig)

        return gdf, result


# igdf, ogdf = OverlapLib.test()
