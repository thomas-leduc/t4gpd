"""
Created on 18 Nov. 2025

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

from geopandas import read_file
from os import path
from py7zr import SevenZipFile
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from t4gpd.commons.GeoProcess import GeoProcess


class ArchiveReader(GeoProcess):
    """
    Generic spatial archive reader:
    - ZIP / 7z
    - shapefile / geojson / gpkg / parquet
    """

    VECTOR_EXTENSIONS = (".shp", ".geojson", ".gpkg", ".parquet", ".geoparquet")

    def __init__(self, inputFile, layers, bbox=None, mask=None):
        """
        Constructor
        """
        self.inputFile = inputFile
        self.layers = layers
        self.bbox = bbox
        self.mask = mask

    # -------------------------------------------------
    # ARCHIVE OPENING
    # -------------------------------------------------
    @staticmethod
    def __open_archive(inputFile):
        try:
            return ZipFile(inputFile, "r")
        except Exception:
            pass
        try:
            return SevenZipFile(inputFile, mode="r")
        except Exception:
            pass
        raise ValueError("Unsupported archive format (ZIP / 7z only).")

    # -------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------
    def run(self):
        with self.__open_archive(self.inputFile) as archive:
            is_zip = isinstance(archive, ZipFile)

            with TemporaryDirectory() as tmp:
                # -------------------------
                # EXTRACTION UNIFIÉE
                # -------------------------
                if is_zip:
                    archive.extractall(path=tmp)
                    get_names = archive.namelist()
                else:
                    archive.extract(path=tmp, targets=archive.getnames())
                    get_names = archive.getnames()

                candidates = self.__scan(get_names)

                result = {}

                # -------------------------
                # SHAPEFILES / GEOJSON
                # -------------------------
                for ds in candidates["vector_files"]:
                    name = self.__dataset_name(ds)

                    if name not in self.layers:
                        continue

                    result[name] = read_file(
                        path.join(tmp, ds), bbox=self.bbox, mask=self.mask
                    )

                # -------------------------
                # GPKG
                # -------------------------
                for gpkg in candidates["gpkg"]:
                    result.update(self.__read_gpkg(tmp, gpkg))

            return result

    # -------------------------------------------------
    # SCANNING
    # -------------------------------------------------
    def __scan(self, files):
        vector_files = []
        gpkg = []

        for f in files:
            lf = f.lower()

            if lf.endswith(".gpkg"):
                gpkg.append(f)

            elif lf.endswith(self.VECTOR_EXTENSIONS):
                vector_files.append(f)

        return {"vector_files": vector_files, "gpkg": gpkg}

    # -------------------------------------------------
    # GPKG HANDLING
    # -------------------------------------------------
    def __read_gpkg(self, tmp, gpkg_file):
        import fiona

        gpkg_path = path.join(tmp, gpkg_file)
        available_layers = fiona.listlayers(gpkg_path)

        out = {}

        for layer in available_layers:
            if layer not in self.layers:
                continue

            key = f"{path.basename(gpkg_file)}::{layer}"
            key = (
                key if layer in out else layer
            )  # avoid layer name collision across GPKG files

            out[key] = read_file(gpkg_path, layer=layer, bbox=self.bbox, mask=self.mask)

        return out

    # -------------------------------------------------
    # UTIL
    # -------------------------------------------------
    @staticmethod
    def __dataset_name(file):
        return path.splitext(path.basename(file))[0]

    @staticmethod
    def test():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        actual = ArchiveReader(
            "/home/tleduc/data/bdtopo/BDTOPO_3-5_TOUSTHEMES_SHP_LAMB93_D044_2025-06-15.7z",
            ["BATIMENT", "TRONCON_DE_ROUTE"],
            bbox=GeoDataFrameDemos.ensaNantesBuildings(),
        ).run()

        buildings = actual["BATIMENT"]
        roads = actual["TRONCON_DE_ROUTE"]

        fig, ax = plt.subplots(figsize=(10, 10))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="black")
        roads.plot(ax=ax, color="blue")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)

    @staticmethod
    def test2():
        import matplotlib.pyplot as plt
        from t4gpd.demos.GeoDataFrameDemos import GeoDataFrameDemos

        actual = ArchiveReader(
            "/home/tleduc/data/bdtopo/BDTOPO_3-5_TOUSTHEMES_GPKG_LAMB93_D044_2025-12-15.7z",
            ["batiment", "troncon_de_route"],
            bbox=GeoDataFrameDemos.ensaNantesBuildings(),
        ).run()

        buildings = actual["batiment"]
        roads = actual["troncon_de_route"]

        fig, ax = plt.subplots(figsize=(10, 10))
        buildings.plot(ax=ax, color="lightgrey", edgecolor="black")
        roads.plot(ax=ax, color="blue")
        ax.axis("off")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


# ArchiveReader.test()
# ArchiveReader.test2()
