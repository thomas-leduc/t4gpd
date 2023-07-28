'''
Created on 6 mai 2023

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
import warnings

from numpy import isnan
from t4gpd.commons.GeoProcess import GeoProcess
from t4gpd.commons.WarnUtils import WarnUtils
from t4gpd.picoclim.InertialMeasureReader import InertialMeasureReader


class InertialMeasureReWriter(GeoProcess):
    '''
    classdocs
    '''
    OK = 0
    CANNOT_ADD_FIRST_TN = 1 
    CANNOT_ADD_LAST_TN = 2 
    
    def __init__(self, inputFile, outputFile, rewriteTagNames=True, addFirstTagName=True, addLastTagName=True):
        '''
        Constructor
        '''
        warnings.formatwarning = WarnUtils.format_Warning
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.rewriteTagNames = rewriteTagNames
        self.addFirstTagName = addFirstTagName
        self.addLastTagName = addLastTagName

    def __read_csv(self):
        version = InertialMeasureReader.getVersion(self.inputFile)
        # with open(self.inputFile, "r") as ifile:
        #     head = [next(ifile) for _ in (0, 1)]
        head = """     time_stamp step_count           X       Y       Z    Distance          degree          latitude       longitude        GpsAccuracy  indoor_outdoor_flag       TagName

"""
        df = InertialMeasureReader(self.inputFile).run()
        return version, head, df

    @staticmethod
    def tagNameDiagnosis(inputFile):
        df = InertialMeasureReader(inputFile).run()
        exit_status = InertialMeasureReWriter.OK
        tagNames = df[~df.TagName.isna()].TagName.to_dict()
        trackId = {(v // 10) if (v < 100) else (v // 100): None for v in tagNames.values()}
        if (1 != len(trackId)):
            raise Exception(f"The TagNames' fall under more than one track in {inputFile}!")
        trackId = int(list(trackId.keys())[0])
        if ((0 in tagNames) or (1 in tagNames)):
            # warnings.warn("I can't insert a starting TagName!")
            exit_status += InertialMeasureReWriter.CANNOT_ADD_FIRST_TN
        n = len(df) - 1
        if (((n - 1) in tagNames) or (n in tagNames)):
            # warnings.warn("I can't insert an end TagName!")
            exit_status += InertialMeasureReWriter.CANNOT_ADD_LAST_TN
        return trackId, exit_status
        
    @staticmethod
    def rectifyId(i):
        if (i < 100):
            tens, units = i // 10, i % 10
            return tens * 100 + units
        return i

    def __rewriteTagNames(self, df):
        exit_status = self.OK
        oldTagNames = df[~df.TagName.isna()].TagName.to_dict()
        newTagNames = {k: self.rectifyId(v) for k, v in oldTagNames.items()}

        trackId = {v // 100: None for v in newTagNames.values()}
        if (1 != len(trackId)):
            raise Exception(f"The TagNames' fall under more than one track in {self.inputFile}!")
        trackId = int(list(trackId.keys())[0])

        # HANDLE 31 TRACKS #4 IN 06-Carriere-misery-Nantes (id: 40 -> 42)
        if (0 == min(newTagNames.values()) % 100):
            newTagNames = {k: v+1 for k, v in newTagNames.items()}

        if self.addFirstTagName:
            if ((0 in newTagNames) or (1 in newTagNames)):
                # warnings.warn("I can't insert a starting TagName!")
                exit_status += self.CANNOT_ADD_FIRST_TN
            else:
                newTagNames[0] = trackId * 100
        if self.addLastTagName:
            n = len(df) - 1
            if (((n - 1) in newTagNames) or (n in newTagNames)):
                # warnings.warn("I can't insert an end TagName!")
                exit_status += self.CANNOT_ADD_LAST_TN
            else:
                newTagNames[n] = 1 + max(newTagNames.values())
        newTagNames = {k:v for k, v in sorted(newTagNames.items(), key=lambda kv: kv[0])}

        for k, v in newTagNames.items():
            df.at[k, "TagName"] = v

        # print(oldTagNames)
        # print(newTagNames)
        return exit_status, df

    def __to_csv(self, version, head, df):
        # df.to_csv(self.outputFile)
        # FMT = "{:>15s}{:>10d}{:>13.2f}{:>8.2f}{:>8.2f}{:>12.2f}{:>16.2f}{:>18.6f}{:>16.6f}{:>19.2f}{:>21s}{:>14.0f}\n"
        FMT = "{:>15s}{:>10d}{:>13s}{:>8s}{:>8s}{:>12s}{:>16s}{:>18s}{:>16s}{:>19s}{:>21s}{:>14s}\n"

        foo1 = lambda dt: dt[:-3]
        foo2 = lambda x: f"{x:.2f}".replace(".", ",")
        foo3 = foo2
        foo4 = lambda x: f"{x:.6f}".replace(".", ",")
        foo5 = lambda x: x.strip()
        foo6 = lambda x: "" if isnan(x) else f"{x:.0f}"

        if (2 == version):
            # FMT = "{:>11s}{:>14d}{:>13s}{:>8s}{:>8s}{:>12s}{:>16s}{:>16s}{:>16s}{:>21s}{:>21s}{:>12s}\n"
            foo1 = lambda dt: dt[:-7]
            foo4 = foo2
        elif (4 == version):
            # FMT = "{:<16s}{:>4d}{:>13s}{:>8s}{:>8s}{:>13s}{:>16s}{:>11s}{:>15s}{:>14s}{:>11s}{:>26s}\n"
            # FMT = "{:>11s}{:>14d}{:>13s}{:>8s}{:>8s}{:>12s}{:>16s}{:>16s}{:>16s}{:>21s}{:>21s}{:>12s}\n"
            foo3 = lambda x: x.replace(".", ",")

        with open(self.outputFile, "w") as ofile:
            ofile.writelines(head)

            for _, row in df.iterrows():
                line = FMT.format(
                    foo1(row.timestamp.strftime("%H:%M:%S.%f")),
                    row.step_count, foo2(row.X), foo2(row.Y), foo2(row.Z),
                    foo3(row.Distance), foo2(row.degree), foo4(row.latitude), foo4(row.longitude),
                    foo2(row.GpsAccuracy), foo5(row.indoor_outdoor_flag), foo6(row.TagName)
                )
                ofile.write(line)

    def run(self):
        exit_status = self.OK
        version, head, df = self.__read_csv()

        if (self.rewriteTagNames) or (self.addFirstTagName) or (self.addLastTagName):
            exit_status, df = self.__rewriteTagNames(df)

        self.__to_csv(version, head, df)
        print(f"{self.outputFile} has been written (v{version})!")
        return exit_status

"""
inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/05-Quai-de-plantes-Nantes/20200526/localisation/LOG_FILE_20200526_120307.txt"
InertialMeasureReWriter(inputFile, "/tmp/abc.csv").run()

inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/06-Carriere-misery-Nantes/20200722/localisation/LOG_FILE_20200722_141610.txt"
InertialMeasureReWriter(inputFile, "/tmp/abc.csv").run()

inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/08-La-defense-Paris/20210721/localisation/LOG_FILE_20210721_182401.txt"
InertialMeasureReWriter(inputFile, "/tmp/abc.csv").run()

inputFile = "/home/tleduc/prj/nm-ilots-frais/terrain/220711/LOG_FILE_20220711_172000.txt"
InertialMeasureReWriter(inputFile, "/tmp/abc.csv").run()

inputFile = "/home/tleduc/prj/coolscapes-tl/dev/data/06-Carriere-misery-Nantes/20200716/localisation/LOG_FILE_20200716_115024.txt"
InertialMeasureReWriter(inputFile, "/tmp/abc.csv", rewriteTagNames=True, addFirstTagName=False, addLastTagName=False).run()
"""
