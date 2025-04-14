"""
Created on 13 Apr. 2025

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
from geopandas import GeoDataFrame
from io import StringIO
from pandas import read_csv
from t4gpd.wrf.MeteoFranceReader import MeteoFranceReader


class MeteoFranceReaderTest(unittest.TestCase):
    def setUp(self):
        self.sio = StringIO(
            """NUM_POSTE;NOM_USUEL;LAT;LON;ALTI;AAAAMMJJHH;RR1;QRR1;DRR1;QDRR1;FF;QFF;DD;QDD;FXY;QFXY;DXY;QDXY;HXY;QHXY;FXI;QFXI;DXI;QDXI;HXI;QHXI;FF2;QFF2;DD2;QDD2;FXI2;QFXI2;DXI2;QDXI2;HXI2;QHXI2;FXI3S;QFXI3S;DXI3S;QDXI3S;HFXI3S;QHFXI3S;T;QT;TD;QTD;TN;QTN;HTN;QHTN;TX;QTX;HTX;QHTX;DG;QDG;T10;QT10;T20;QT20;T50;QT50;T100;QT100;TNSOL;QTNSOL;TN50;QTN50;TCHAUSSEE;QTCHAUSSEE;DHUMEC;QDHUMEC;U;QU;UN;QUN;HUN;QHUN;UX;QUX;HUX;QHUX;DHUMI40;QDHUMI40;DHUMI80;QDHUMI80;TSV;QTSV;PMER;QPMER;PSTAT;QPSTAT;PMERMIN;QPMERMIN;GEOP;QGEOP;N;QN;NBAS;QNBAS;CL;QCL;CM;QCM;CH;QCH;N1;QN1;C1;QC1;B1;QB1;N2;QN2;C2;QC2;B2;QB2;N3;QN3;C3;QC3;B3;QB3;N4;QN4;C4;QC4;B4;QB4;VV;QVV;DVV200;QDVV200;WW;QWW;W1;QW1;W2;QW2;SOL;QSOL;SOLNG;QSOLNG;TMER;QTMER;VVMER;QVVMER;ETATMER;QETATMER;DIRHOULE;QDIRHOULE;HVAGUE;QHVAGUE;PVAGUE;QPVAGUE;HNEIGEF;QHNEIGEF;NEIGETOT;QNEIGETOT;TSNEIGE;QTSNEIGE;TUBENEIGE;QTUBENEIGE;HNEIGEFI3;QHNEIGEFI3;HNEIGEFI1;QHNEIGEFI1;ESNEIGE;QESNEIGE;CHARGENEIGE;QCHARGENEIGE;GLO;QGLO;GLO2;QGLO2;DIR;QDIR;DIR2;QDIR2;DIF;QDIF;DIF2;QDIF2;UV;QUV;UV2;QUV2;UV_INDICE;QUV_INDICE;INFRAR;QINFRAR;INFRAR2;QINFRAR2;INS;QINS;INS2;QINS2;TLAGON;QTLAGON;TVEGETAUX;QTVEGETAUX;ECOULEMENT;QECOULEMENT
44015001;BLAIN;47.472833;-1.771667;13;2024010100;0.0;1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;7.4;1;;;6.5;1;2310;9;7.5;1;2351;9;0;9;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
44015001;BLAIN;47.472833;-1.771667;13;2024010101;0.8;1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;6.8;1;;;6.8;1;59;9;7.4;1;1;9;0;9;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
44015001;BLAIN;47.472833;-1.771667;13;2024010102;0.2;1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;7.0;1;;;6.2;1;144;9;7.0;1;158;9;0;9;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
44015001;BLAIN;47.472833;-1.771667;13;2024010103;0.0;1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;6.5;1;;;6.5;1;258;9;7.3;1;208;9;0;9;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
"""
        )
        self.ncols = len(
            read_csv(StringIO(self.sio.getvalue()), sep=";", nrows=0).columns
        )

    def tearDown(self):
        pass

    def testRun1(self):
        actual = MeteoFranceReader([self.sio]).run()
        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(4, len(actual), "Count rows")
        self.assertEqual(self.ncols + 8 + 1 + 10, len(actual.columns), "Count columns")

    def testRun2(self):
        actual = MeteoFranceReader([self.sio], station="NANTES-BOUGUENAIS").run()
        self.assertIsInstance(actual, GeoDataFrame, "Is a GeoDataFrame")
        self.assertEqual(0, len(actual), "Count rows")
        self.assertEqual(self.ncols + 8, len(actual.columns), "Count columns")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
