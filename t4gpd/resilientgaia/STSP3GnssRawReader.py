"""
Created on 15 Jan. 2026

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

import gzip
from glob import glob
from os.path import isdir, isfile
from pandas import DataFrame, concat, date_range, to_datetime
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException
from t4gpd.resilientgaia.SatelliteLib import SatelliteLib


class STSP3GnssRawReader(GeoProcess):
    """
    classdocs
    """

    __slots__ = ("sp3_files_or_dirname", "freq", "filter", "format")

    def __init__(self, sp3_files_or_dirname, freq=None, filter=None, format="long"):
        """
        Constructor
        """
        self.sp3_files_or_dirname = sp3_files_or_dirname
        self.freq = freq  # "5min", "1h"
        self.filter = filter
        if format not in ("long", "wide"):
            raise IllegalArgumentTypeException(format, '"long" or "wide"')
        self.format = format  # "long" or "wide"

    @staticmethod
    def __read_aux(sp3_filename):
        with gzip.open(sp3_filename, "rt") as f:
            lines = f.readlines()

        # Reading satellite positions in SP3
        sat_positions = []
        for line in lines:
            if line.startswith("*"):
                dt = " ".join(line[1:-3].split())

            elif line.startswith("P"):
                satname, x, y, z, clock_corr = line[1:].split()[:5]
                # Convert kilometer coordinates to meters
                x, y, z = 1e3 * float(x), 1e3 * float(y), 1e3 * float(z)

                sat_positions.append(
                    {
                        "sat_dt": dt,
                        "sat_name": satname,
                        "x": x,
                        "y": y,
                        "z": z,
                    }
                )
        sat_positions = DataFrame(sat_positions)
        sat_positions.sat_dt = to_datetime(
            sat_positions.sat_dt,
            format="%Y %m %d %H %M %S.%f",
            errors="raise",
        ).dt.tz_localize("UTC")
        return sat_positions

    @staticmethod
    def _read(sp3_files_or_dirname, freq=None, filter=None):
        if isinstance(sp3_files_or_dirname, (list, tuple)):
            sp3 = []
            for sp3_filename in sp3_files_or_dirname:
                if isfile(sp3_filename):
                    _sp3 = STSP3GnssRawReader.__read_aux(sp3_filename)
                sp3.append(_sp3)
            sp3 = concat(sp3, ignore_index=True)

        elif isfile(sp3_files_or_dirname):
            sp3 = STSP3GnssRawReader.__read_aux(sp3_files_or_dirname)

        elif isdir(sp3_files_or_dirname):
            sp3 = []
            for sp3_filename in glob(f"{sp3_files_or_dirname}/*.SP3.gz"):
                _sp3 = STSP3GnssRawReader.__read_aux(sp3_filename)
                sp3.append(_sp3)
            sp3 = concat(sp3, ignore_index=True)

        else:
            raise IllegalArgumentTypeException(
                sp3_files_or_dirname, "filename, list of filenames or dirname"
            )

        if freq is not None:
            dt0, dt1 = sp3.sat_dt.min(), sp3.sat_dt.max()
            dts = date_range(start=dt0, end=dt1, freq=freq)
            sp3 = sp3.query("sat_dt.isin(@dts)").copy(deep=True)

        if filter is not None:
            sp3 = sp3.query(filter).copy(deep=True)

        sp3.sort_values(by="sat_dt", inplace=True)
        return sp3

    @staticmethod
    def _transform_wide(sp3):
        # PIVOT: long -> wide
        df = sp3.pivot_table(
            index="sat_dt",
            columns="sat_name",
            values=["x", "y", "z"],
            aggfunc="first",  # au cas où doublons
        )

        # RENAME COLUMNS
        df.columns = [f"satcoord{coord.upper()}_{sat}" for coord, sat in df.columns]

        # EXPLICIT ORDERING COLUMNS
        all_cols = [
            f"satcoord{coord}_{sat}"
            for sat in SatelliteLib.get_satellite_names(version=2)
            for coord in ["X", "Y", "Z"]
        ]
        # ADD MISSING COLUMNS (FILLED WITH NaN VALUES)
        df = df.reindex(columns=all_cols)

        # RESET INDEX
        df = df.reset_index()
        # ADD "gid" COLUMN
        # df.insert(0, "gid", range(len(df)))
        return df

    def run(self):
        sat_positions = STSP3GnssRawReader._read(
            self.sp3_files_or_dirname, self.freq, self.filter
        )
        if self.format == "wide":
            sat_positions = STSP3GnssRawReader._transform_wide(sat_positions)

        return sat_positions

    @staticmethod
    def test():
        rootdir = "/home/tleduc/prj/anr_resilientgaia_2024-2028/cddis/2026"
        df = STSP3GnssRawReader(
            sp3_files_or_dirname=f"{rootdir}/COD0OPSULT_20260010000_02D_05M_ORB.SP3.gz",
            # sp3_files_or_dirname=rootdir,
            freq=None,
            filter=None,
            format="long",
        ).run()
        assert (2 * 24 * 12 + 1) * 80 == len(df)
        return df

    @staticmethod
    def test2():
        rootdir = "/home/tleduc/prj/anr_resilientgaia_2024-2028/cddis/2026"
        df = STSP3GnssRawReader(
            sp3_files_or_dirname=f"{rootdir}/COD0OPSULT_20260010000_02D_05M_ORB.SP3.gz",
            # sp3_files_or_dirname=rootdir,
            freq=None,
            filter=None,
            format="wide",
        ).run()
        assert df.sat_dt.is_unique
        assert (2 * 24 * 12 + 1) == len(df)
        return df


# df1 = STSP3GnssRawReader.test()
# df2 = STSP3GnssRawReader.test2()
