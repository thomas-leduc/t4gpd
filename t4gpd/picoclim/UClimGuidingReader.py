'''
Created on 28 avr. 2023

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
from datetime import timedelta, timezone
from io import StringIO
from os.path import basename
import re
import warnings
from zoneinfo import ZoneInfo

from geopandas import GeoDataFrame
from pandas import DataFrame, to_datetime
from shapely import LineString, Point
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.io.AbstractReader import AbstractReader


class UClimGuidingReader(AbstractReader):
    '''
    classdocs
    '''

    def __init__(self, inputFile, generateTrackAndWaypoints=False, crs="EPSG:4326"):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning_alt
        self.inputFile = inputFile
        self.generateTrackAndWaypoints = generateTrackAndWaypoints
        self.crs = crs
        self.dfUclim = None

    def __getVersion(self):
        RE_VERSION = re.compile(r"^#\s*CODING\s+VERSION\s+(\d+)$")
        with UClimGuidingReader.opener(self.inputFile) as f:
            for line in f:
                line = line.strip().upper()
                if RE_VERSION.match(line):
                    return int(RE_VERSION.search(line).group(1))
        return 1

    def __check(self):
        df = self.getDfUclim()

        assert df.wp1.is_monotonic_increasing, "The wp1 column is not increasing"
        assert df.wp1.is_unique, "The wp1 column is not strictly increasing"

        assert df.wp2.is_monotonic_increasing, "The wp2 column is not increasing"
        assert df.wp2.is_unique, "The wp2 column is not strictly increasing"

        assert df.timestamps.explode().is_monotonic_increasing, "Timestamps are not ascending"
        assert df.timestamps.explode().is_unique, "Timestamps are not strictly ascending"

    def __generateTrackAndWaypoints(self, points, waypoints):
        waypoints = [{"id": 100 + i, "geometry": points[waypoints[i]]} for i in sorted(waypoints.keys())]
        waypoints = GeoDataFrame(waypoints, crs=self.crs)

        points = [points[i] for i in sorted(points.keys())]
        track = LineString([(p.x, p.y) for p in points])
        track = GeoDataFrame([{"geometry": track}], crs=self.crs)

        return track, waypoints

    @staticmethod
    def _timestamp2datetime(ts, tzinfo=ZoneInfo("Europe/Paris")):
        return to_datetime(int(ts), unit="ms").\
            tz_localize(timezone.utc).tz_convert(tzinfo)

    def __readV1(self):
        RE_ROUTE_ID = re.compile(r"^#\s*ROUTE_ID\s+(.*)$")
        RE_COMMENT = re.compile(r"^#")
        RE_CANCELING = re.compile(r"^.*CANCELING")
        RE_PREPARING = re.compile(r"^PREPARING\s+MOVE\s+FROM\s+WP_(\d+)\s+TO\s+WP_(\d+)$")
        RE_STARTING = re.compile(r"^STARTING AT\s+\d{13}\s+(STOPPING\s+AT\s+\d{13}\s+RESUMING\s+AT\s+\d{13}\s+)*ARRIVING\s+AT\s+\d{13}$")
        RE_WP = re.compile(r"^WP_(\d+)\s+PT_(\d+)$")
        RE_PT = re.compile(r"^PT_(\d+)\s+(\d+[\.]?\d*)\s+(\d+[\.]?\d*)$")
        RE_TIMESTAMP = re.compile(r"\d{13}")

        tzinfo = ZoneInfo("Europe/Paris")
        waypoints, points, df = {}, {}, {}
        with UClimGuidingReader.opener(self.inputFile) as f:
            for nline, line in enumerate(f, start=1):
                line = line.strip().upper()

                if RE_ROUTE_ID.match(line):
                    route_id = RE_ROUTE_ID.search(line).group(1)

                elif RE_COMMENT.match(line) or RE_CANCELING.match(line) or (0 == len(line)):
                    # There is nothing to do
                    pass

                elif RE_PREPARING.match(line):
                    wp1, wp2 = RE_PREPARING.search(line).groups()
                    wp1, wp2 = int(wp1), int(wp2) 
                    assert wp2 == 1 + wp1

                elif RE_STARTING.match(line):
                    dts = RE_TIMESTAMP.findall(line)
                    dts = [self._timestamp2datetime(dt, tzinfo) for dt in dts]
                    # dts = [dt.strftime("%X") for dt in dts]
                    df[wp1] = dts

                elif RE_WP.match(line):
                    wp, pt = RE_WP.search(line).groups()
                    waypoints[int(wp)] = int(pt)

                elif RE_PT.match(line):
                    pt, x, y = RE_PT.search(line).groups()
                    points[int(pt)] = Point((x, y))

                else:
                    raise Exception(f"Syntax error line {nline}")

        rows = []
        for wp1 in sorted(df.keys()):
            rows.append({"route_id": route_id, "wp1": wp1, "wp2": wp1 + 1, "timestamps": df[wp1]})
        df = DataFrame(rows)

        if self.generateTrackAndWaypoints:
            track, waypoints = self.__generateTrackAndWaypoints(points, waypoints)
            return df, track, waypoints
        return df

    def __readV2(self):
        RE_ROUTE_ID = re.compile(r"^#\s*ROUTE_ID\s+(.*)$", flags=re.IGNORECASE)
        RE_TIMEZONE = re.compile(r"^#\s*TIMEZONE\s+(.*)$", flags=re.IGNORECASE)
        RE_COMMENT = re.compile(r"^#")
        RE_CANCELING = re.compile(r"^.*CANCELING", flags=re.IGNORECASE)
        RE_PREPARING = re.compile(r"^MOVING\s+FROM\s+WP_(\d+)\s+TO\s+WP_(\d+)$", flags=re.IGNORECASE)
        RE_STARTING = re.compile(r"^STARTING AT\s+\d{13}\s+(PAUSING\s+AT\s+\d{13}\s+RESUMING\s+AT\s+\d{13}\s+)*ARRIVING\s+AT\s+\d{13}$", flags=re.IGNORECASE)
        RE_WARNING = re.compile(r"^WARNING\s*:(.*)$", flags=re.IGNORECASE)
        RE_WP = re.compile(r"^WP_(\d+)\s+PT_(\d+)$", flags=re.IGNORECASE)
        RE_PT = re.compile(r"^PT_(\d+)\s+(\d+[\.]?\d*)\s+(\d+[\.]?\d*)$", flags=re.IGNORECASE)
        RE_TIMESTAMP = re.compile(r"\d{13}")

        tzinfo = None
        waypoints, points, df = {}, {}, {}
        with UClimGuidingReader.opener(self.inputFile) as f:
            for nline, line in enumerate(f, start=1):
                line = line.strip()

                if RE_ROUTE_ID.match(line):
                    route_id = RE_ROUTE_ID.search(line).group(1)

                elif RE_TIMEZONE.match(line):
                    tzinfo = ZoneInfo(RE_TIMEZONE.search(line).group(1))

                elif RE_COMMENT.match(line) or RE_CANCELING.match(line) or (0 == len(line)):
                    # There is nothing to do
                    pass

                elif RE_PREPARING.match(line):
                    warning_msg = None
                    wp1, wp2 = RE_PREPARING.search(line).groups()
                    wp1, wp2 = int(wp1), int(wp2) 
                    assert wp2 == 1 + wp1

                elif RE_STARTING.match(line):
                    dts = RE_TIMESTAMP.findall(line)
                    dts = [self._timestamp2datetime(dt, tzinfo) for dt in dts]
                    # dts = [dt.strftime("%X") for dt in dts]
                    df[wp1] = {"timestamps": dts}

                elif RE_WARNING.match(line):
                    warning_msg = RE_WARNING.search(line).group(1).strip()
                    df[wp1]["warning"] = warning_msg

                elif RE_WP.match(line):
                    wp, pt = RE_WP.search(line).groups()
                    waypoints[int(wp)] = int(pt)

                elif RE_PT.match(line):
                    pt, x, y = RE_PT.search(line).groups()
                    points[int(pt)] = Point((x, y))

                else:
                    raise Exception(f"Syntax error line {nline}\n\t{line}")

        rows = []
        for wp1 in sorted(df.keys()):
            _timestamps = df[wp1]["timestamps"]
            _warning = df[wp1]["warning"] if ("warning" in df[wp1]) else None
            rows.append({"route_id": route_id, "wp1": wp1, "wp2": wp1 + 1,
                         "timestamps": _timestamps, "warning": _warning})
        df = DataFrame(rows)

        if self.generateTrackAndWaypoints:
            track, waypoints = self.__generateTrackAndWaypoints(points, waypoints)
            return df, track, waypoints
        return df

    def __readV3(self):
        RE_ROUTE_ID = re.compile(r"^#\s*ROUTE_ID\s+(.*)$", flags=re.IGNORECASE)
        RE_TRACK_ID = re.compile(r"^#\s*TRACK\s+(.*)$", flags=re.IGNORECASE)
        RE_TIMEZONE = re.compile(r"^#\s*TIMEZONE\s+(.*)$", flags=re.IGNORECASE)
        RE_COMMENT = re.compile(r"^#")
        RE_CANCELING = re.compile(r"^.*CANCELING", flags=re.IGNORECASE)
        RE_PREPARING = re.compile(r"^MOVING\s+FROM\s+WP_(\d+)\s+TO\s+WP_(\d+)$", flags=re.IGNORECASE)
        RE_STARTING = re.compile(r"^STARTING AT\s+\d{13}\s+(PAUSING\s+AT\s+\d{13}\s+RESUMING\s+AT\s+\d{13}\s+)*ARRIVING\s+AT\s+\d{13}$", flags=re.IGNORECASE)
        RE_WARNING = re.compile(r"^WARNING\s*:(.*)$", flags=re.IGNORECASE)
        RE_TIMESTAMP = re.compile(r"\d{13}")

        tzinfo = None
        df = {}
        with UClimGuidingReader.opener(self.inputFile) as f:
            for nline, line in enumerate(f, start=1):
                line = line.strip()

                if RE_ROUTE_ID.match(line):
                    route_id = RE_ROUTE_ID.search(line).group(1)

                if RE_TRACK_ID.match(line):
                    track_id = RE_TRACK_ID.search(line).group(1)

                elif RE_TIMEZONE.match(line):
                    tzinfo = ZoneInfo(RE_TIMEZONE.search(line).group(1))

                elif RE_COMMENT.match(line) or RE_CANCELING.match(line) or (0 == len(line)):
                    # There is nothing to do
                    pass

                elif RE_PREPARING.match(line):
                    warning_msg = None
                    wp1, wp2 = RE_PREPARING.search(line).groups()
                    wp1, wp2 = int(wp1), int(wp2) 
                    assert wp2 == 1 + wp1

                elif RE_STARTING.match(line):
                    dts = RE_TIMESTAMP.findall(line)
                    dts = [self._timestamp2datetime(dt, tzinfo) for dt in dts]
                    # dts = [dt.strftime("%X") for dt in dts]
                    df[wp1] = {"timestamps": dts}

                elif RE_WARNING.match(line):
                    warning_msg = RE_WARNING.search(line).group(1).strip()
                    df[wp1]["warning"] = warning_msg

                else:
                    raise Exception(f"Syntax error line {nline}\n\t{line}")

        rows = []
        for wp1 in sorted(df.keys()):
            _timestamps = df[wp1]["timestamps"]
            _warning = df[wp1]["warning"] if ("warning" in df[wp1]) else None
            rows.append({"route_id": route_id, "track_id": track_id, "wp1": wp1,
                         "wp2": wp1 + 1, "timestamps": _timestamps,
                         "warning": _warning})
        return DataFrame(rows)

    def __readV4(self):
        RE_PROJECT_ID = re.compile(r"^#\s*PROJECT\s+(.*)$", flags=re.IGNORECASE)
        RE_TRACK_ID = re.compile(r"^#\s*TRACK\s+(.*)$", flags=re.IGNORECASE)
        RE_TIMEZONE = re.compile(r"^#\s*TIMEZONE\s+(.*)$", flags=re.IGNORECASE)
        RE_COMMENT = re.compile(r"^#")
        RE_CANCELING = re.compile(r"^.*CANCELING", flags=re.IGNORECASE)
        RE_PREPARING = re.compile(r"^MOVING\s+FROM\s+WP_(\d+)\s+TO\s+WP_(\d+)$", flags=re.IGNORECASE)
        RE_STARTING = re.compile(r"^STARTING AT\s+\d{13}\s+(PAUSING\s+AT\s+\d{13}\s+RESUMING\s+AT\s+\d{13}\s+)*ARRIVING\s+AT\s+\d{13}$", flags=re.IGNORECASE)
        RE_WARNING = re.compile(r"^WARNING\s*:(.*)$", flags=re.IGNORECASE)
        RE_TIMESTAMP = re.compile(r"\d{13}")

        tzinfo = None
        df = {}
        with UClimGuidingReader.opener(self.inputFile) as f:
            for nline, line in enumerate(f, start=1):
                line = line.strip()

                if RE_PROJECT_ID.match(line):
                    project_id = RE_PROJECT_ID.search(line).group(1)

                if RE_TRACK_ID.match(line):
                    track_id = RE_TRACK_ID.search(line).group(1)

                elif RE_TIMEZONE.match(line):
                    tzinfo = ZoneInfo(RE_TIMEZONE.search(line).group(1))

                elif RE_COMMENT.match(line) or RE_CANCELING.match(line) or (0 == len(line)):
                    # There is nothing to do
                    pass

                elif RE_PREPARING.match(line):
                    warning_msg = None
                    wp1, wp2 = RE_PREPARING.search(line).groups()
                    wp1, wp2 = int(wp1), int(wp2) 
                    assert wp2 == 1 + wp1

                elif RE_STARTING.match(line):
                    dts = RE_TIMESTAMP.findall(line)
                    dts = [self._timestamp2datetime(dt, tzinfo) for dt in dts]
                    # dts = [dt.strftime("%X") for dt in dts]
                    df[wp1] = {"timestamps": dts}

                elif RE_WARNING.match(line):
                    warning_msg = RE_WARNING.search(line).group(1).strip()
                    df[wp1]["warning"] = warning_msg

                else:
                    raise Exception(f"Syntax error line {nline}\n\t{line}")

        rows = []
        for wp1 in sorted(df.keys()):
            _timestamps = df[wp1]["timestamps"]
            _warning = df[wp1]["warning"] if ("warning" in df[wp1]) else None
            rows.append({"project_id": project_id, "track_id": track_id, "wp1": wp1,
                         "wp2": wp1 + 1, "timestamps": _timestamps,
                         "warning": _warning})
        return DataFrame(rows)

    def getDfUclim(self):
        if self.dfUclim is None:
            version = self.__getVersion()
            if (1 == version):
                self.dfUclim = self.__readV1()
            elif (2 == version):
                self.dfUclim = self.__readV2()
            elif (3 == version):
                self.dfUclim = self.__readV3()
            elif (4 == version):
                self.dfUclim = self.__readV4()
            else:
                raise Exception("Unreachable instruction!")
        return self.dfUclim

    def getPerformance(self):
        df = self.getDfUclim()
        dt0 = df.loc[0, "timestamps"][0]
        dt1 = df.loc[len(df) - 1, "timestamps"][-1]
        deltaTotal = (dt1 - dt0).seconds
        deltaActual = df.actual_elapsed_time.sum()
        return dt0, dt1, deltaTotal, deltaActual, 100 * deltaActual / deltaTotal

    @staticmethod
    def timedeltaBetweenTwoWaypoints(dts):
        assert (0 == len(dts) % 2), "List of an odd number of dates"
        delta = timedelta(0)
        for i in range(0, len(dts), 2):
            delta += dts[i + 1] - dts[i]
        return delta

    def audit(self):
        dt0, dt1, deltaTotal, deltaActual, perf = self.getPerformance()

        identifier = ""
        if not isinstance(self.inputFile, StringIO):
            identifier = f"\n**** {basename(self.inputFile) }"

        warnings.warn("\n" + "*"*70 + f"""{identifier}
****\tFROM: {dt0}
****\tTO: {dt1}
****\tTOTAL PERIOD: {deltaTotal//60} min. {deltaTotal%60} sec.
****\tACTUAL PERIOD: {deltaActual//60} min. {deltaActual%60} sec.
****\tMEASUREMENT PERFORMANCE: {perf:.1f} %
****\tNB WAYPOINTS: {len(self.getDfUclim())}
""" + "*"*70)

    def run(self):
        self.dfUclim = self.getDfUclim()
        self.dfUclim["actual_elapsed_time"] = self.dfUclim.timestamps.apply(
            lambda dts: self.timedeltaBetweenTwoWaypoints(dts).total_seconds())
        self.__check()
        self.audit()
        return self.dfUclim

"""
ifile = "/home/tleduc/prj/uclim/flask/static/uploads/1686227346623113409/uclimLOC_nantes_commerce_feydeau_20230607T1228.txt"
df = UClimGuidingReader(ifile).run()
"""
