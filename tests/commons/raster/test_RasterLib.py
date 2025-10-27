"""
Created on 3 Oct. 2025

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

import unittest

from numpy import ndarray
from t4gpd.commons.grid.FastGridLib import FastGridLib
from t4gpd.commons.raster.RasterLib import RasterLib
from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos


class RasterLibTest(unittest.TestCase):
    def setUp(self):
        self.buildings = GeoDataFrameDemos.ensaNantesBuildings()

    def tearDown(self):
        pass

    def __common_tests(self, actual_data, actual_profile):
        self.assertIsInstance(actual_data, ndarray, "Is a ndarray")
        self.assertIsInstance(actual_profile, dict, "Is a dict")
        self.assertEqual(
            (actual_profile.get("height"), actual_profile.get("width")),
            actual_data.shape,
            "Check raster_data shape",
        )
        self.assertEqual(
            actual_profile.get("crs"),
            self.buildings.crs,
            "Check raster_profile CRS",
        )
        self.assertEqual(
            str(actual_data.dtype),
            actual_profile.get("dtype"),
            "Check raster_profile dtype",
        )

    def __plot(self, actual_data, actual_profile, title=None):
        import matplotlib.pyplot as plt
        from rasterio.plot import show

        memraster = RasterLib.raster_data_profile_2_memory_raster(
            actual_data, actual_profile
        )

        fig, ax = plt.subplots(figsize=(1.5 * 8.26, 1.5 * 8.26))
        if title is not None:
            ax.set_title(title, fontsize=20)
        with memraster.open() as dataset:
            show(dataset, ax=ax, cmap="Blues_r", alpha=0.8)
        self.buildings.boundary.plot(ax=ax, color="red")
        self.buildings.apply(
            lambda x: ax.annotate(
                text=x.HAUTEUR,
                xy=x.geometry.centroid.coords[0],
                color="blue",
                size=12,
                ha="center",
            ),
            axis=1,
        )

        ax.axis("off")
        fig.tight_layout()
        # plt.show()
        plt.savefig(f"/tmp/RasterLibTest.{title}.png", bbox_inches="tight")
        plt.close(fig)

    def testFastRasterize(self):
        actual_data, actual_profile = RasterLib.fast_rasterize(
            self.buildings,
            dx=5,
            attr="HAUTEUR",
            roi=None,
            ndv=0,
        )
        self.__common_tests(actual_data, actual_profile)
        self.assertEqual(2, actual_data.ndim, "Check raster_data ndim")
        self.assertEqual(1, actual_profile.get("count"), "Check raster_profile count")
        self.assertEqual(
            str(self.buildings.HAUTEUR.dtype),
            actual_profile.get("dtype"),
            "Check raster_profile dtype",
        )
        self.__plot(actual_data, actual_profile, title="testFastRasterize")

    def testFrom_grid_to_raster(self):
        grid = FastGridLib.grid(
            self.buildings, dx=5, dy=None, intoPoint=True, withRowsCols=True
        )
        grid = grid.sjoin(self.buildings[["geometry", "HAUTEUR"]], how="inner")
        grid.HAUTEUR = 100 * grid.HAUTEUR.astype(int)
        actual_data, actual_profile = RasterLib.from_grid_to_raster(grid, "HAUTEUR")
        self.__common_tests(actual_data, actual_profile)
        self.assertEqual(
            "uint16",
            actual_profile.get("dtype"),
            "Check raster_profile dtype",
        )

    def testFrom_uint16_to_uint8(self):
        grid = FastGridLib.grid(
            self.buildings, dx=5, dy=None, intoPoint=True, withRowsCols=True
        )
        grid = grid.sjoin(self.buildings[["geometry", "HAUTEUR"]], how="inner")
        grid.HAUTEUR = 100 * grid.HAUTEUR.astype(int)
        raster_data, raster_profile = RasterLib.from_grid_to_raster(grid, "HAUTEUR")
        actual_data, actual_profile = RasterLib.from_uint16_to_uint8(
            raster_data, raster_profile
        )
        self.__common_tests(actual_data, actual_profile)
        self.assertEqual(
            "uint8",
            actual_profile.get("dtype"),
            "Check raster_profile dtype",
        )

    def testRasterize(self):
        actual_data, actual_profile = RasterLib.rasterize(
            self.buildings,
            dx=5,
            attr="HAUTEUR",
            roi=None,
            ndv=0,
        )
        self.__common_tests(actual_data, actual_profile)
        self.assertEqual(2, actual_data.ndim, "Check raster_data ndim")
        self.assertEqual(1, actual_profile.get("count"), "Check raster_profile count")
        self.assertEqual(
            str(self.buildings.HAUTEUR.dtype),
            actual_profile.get("dtype"),
            "Check raster_profile dtype",
        )
        self.__plot(actual_data, actual_profile, title="testRasterize")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
