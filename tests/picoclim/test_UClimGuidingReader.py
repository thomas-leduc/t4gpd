'''
Created on 29 avr. 2023

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
import unittest
from io import StringIO
from t4gpd.picoclim.UClimGuidingReader import UClimGuidingReader
from pandas.core.frame import DataFrame


class UClimGuidingReaderTest(unittest.TestCase):

    def setUp(self):
        self.V1 = StringIO("""# CLIMATIC DATA ©CRENAU 2023
# ROUTE_ID NANTES_COMMERCE_2023_1
# 41 POINTS FROM PT_0 TO PT_40
# 21 WAYPOINTS FROM WP_0 TO WP_20
# BEGINING 2023-04-28 16:34
PREPARING MOVE FROM WP_0 TO WP_1
STARTING AT 1682692500645 ARRIVING AT 1682692503985
PREPARING MOVE FROM WP_1 TO WP_2
STARTING AT 1682692506240 STOPPING AT 1682692509233 RESUMING AT 1682692511512 ARRIVING AT 1682692513480
PREPARING MOVE FROM WP_2 TO WP_3
STARTING AT 1682692515792 ARRIVING AT 1682692518959
PREPARING MOVE FROM WP_3 TO WP_4
STARTING AT 1682692521584 CANCELING AND GOING BACK TO WP_3
PREPARING MOVE FROM WP_3 TO WP_4
STARTING AT 1682692526944 ARRIVING AT 1682692530401
PREPARING MOVE FROM WP_4 TO WP_5
STARTING AT 1682692533153 STOPPING AT 1682692535352 RESUMING AT 1682692537064 STOPPING AT 1682692539480 RESUMING AT 1682692541264 STOPPING AT 1682692543554 RESUMING AT 1682692545544 ARRIVING AT 1682692547810
PREPARING MOVE FROM WP_5 TO WP_6
STARTING AT 1682692549696 CANCELING AND GOING BACK TO WP_5
PREPARING MOVE FROM WP_5 TO WP_6
CANCELING AND GOING BACK TO PREVIOUS SECTION AT WP_4
PREPARING MOVE FROM WP_4 TO WP_5
STARTING AT 1682692557423 ARRIVING AT 1682692559896
PREPARING MOVE FROM WP_5 TO WP_6
STARTING AT 1682692561448 STOPPING AT 1682692566368 RESUMING AT 1682692568720 ARRIVING AT 1682692572623
PREPARING MOVE FROM WP_6 TO WP_7
STARTING AT 1682692574402 ARRIVING AT 1682692577785
PREPARING MOVE FROM WP_7 TO WP_8
STARTING AT 1682692579385 CANCELING AND GOING BACK TO WP_7
PREPARING MOVE FROM WP_7 TO WP_8
STARTING AT 1682692585759 ARRIVING AT 1682692588951
PREPARING MOVE FROM WP_8 TO WP_9
STARTING AT 1682692590495 STOPPING AT 1682692593055 RESUMING AT 1682692595103 STOPPING AT 1682692598170 RESUMING AT 1682692599623 ARRIVING AT 1682692601936
PREPARING MOVE FROM WP_9 TO WP_10
STARTING AT 1682692603761 ARRIVING AT 1682692607127
PREPARING MOVE FROM WP_10 TO WP_11
STARTING AT 1682692608631 CANCELING AND GOING BACK TO WP_10
PREPARING MOVE FROM WP_10 TO WP_11
STARTING AT 1682692613463 CANCELING AND GOING BACK TO WP_10
PREPARING MOVE FROM WP_10 TO WP_11
CANCELING AND GOING BACK TO PREVIOUS SECTION AT WP_9
PREPARING MOVE FROM WP_9 TO WP_10
STARTING AT 1682692621151 ARRIVING AT 1682692625839
PREPARING MOVE FROM WP_10 TO WP_11
STARTING AT 1682692627160 ARRIVING AT 1682692629224
PREPARING MOVE FROM WP_11 TO WP_12
STARTING AT 1682692630712 STOPPING AT 1682692632503 RESUMING AT 1682692633766 STOPPING AT 1682692636312 RESUMING AT 1682692637551 ARRIVING AT 1682692638896
PREPARING MOVE FROM WP_12 TO WP_13
STARTING AT 1682692640127 ARRIVING AT 1682692641441
PREPARING MOVE FROM WP_13 TO WP_14
STARTING AT 1682692642415 ARRIVING AT 1682692645328
PREPARING MOVE FROM WP_14 TO WP_15
STARTING AT 1682692646863 STOPPING AT 1682692648905 RESUMING AT 1682692650303 CANCELING AND GOING BACK TO WP_14
PREPARING MOVE FROM WP_14 TO WP_15
STARTING AT 1682692653799 ARRIVING AT 1682692658751
PREPARING MOVE FROM WP_15 TO WP_16
STARTING AT 1682692660255 ARRIVING AT 1682692662577
PREPARING MOVE FROM WP_16 TO WP_17
STARTING AT 1682692664623 ARRIVING AT 1682692666089
PREPARING MOVE FROM WP_17 TO WP_18
STARTING AT 1682692667406 STOPPING AT 1682692669584 RESUMING AT 1682692670559 STOPPING AT 1682692675487 RESUMING AT 1682692677672 STOPPING AT 1682692681825 RESUMING AT 1682692683206 STOPPING AT 1682692685824 RESUMING AT 1682692687190 ARRIVING AT 1682692689799
PREPARING MOVE FROM WP_18 TO WP_19
STARTING AT 1682692691984 ARRIVING AT 1682692695856
PREPARING MOVE FROM WP_19 TO WP_20
STARTING AT 1682692698063 CANCELING AND GOING BACK TO WP_19
PREPARING MOVE FROM WP_19 TO WP_20
STARTING AT 1682692703238 STOPPING AT 1682692706823 RESUMING AT 1682692708743 ARRIVING AT 1682692712584
WP_0 PT_0
WP_1 PT_2
WP_2 PT_5
WP_3 PT_6
WP_4 PT_7
WP_5 PT_8
WP_6 PT_12
WP_7 PT_14
WP_8 PT_16
WP_9 PT_18
WP_10 PT_21
WP_11 PT_22
WP_12 PT_26
WP_13 PT_27
WP_14 PT_29
WP_15 PT_31
WP_16 PT_32
WP_17 PT_33
WP_18 PT_36
WP_19 PT_38
WP_20 PT_40
PT_0 8 1770
PT_1 552 1306
PT_2 1070 752
PT_3 1300 1144
PT_4 1386 1158
PT_5 1463.383838383838 1319.444444444444
PT_6 2219.70802919708 1167.883211678832
PT_7 2295.620437956205 1530.656934306569
PT_8 2032.116788321168 1567.153284671533
PT_9 1900.757575757576 1548.232323232323
PT_10 1739.646464646465 1560.353535353535
PT_11 1631.565656565657 1548.737373737374
PT_12 1499.242424242424 1571.464646464647
PT_13 1517.929292929293 1617.424242424242
PT_14 1629.545454545455 1630.555555555556
PT_15 1740 1610.666666666667
PT_16 1879.545454545455 1627.525252525253
PT_17 2350.5 1559
PT_18 2706.313131313132 1531.565656565657
PT_19 2707.323232323232 1463.383838383838
PT_20 3349.747474747475 1479.545454545455
PT_21 4096.717171717172 1558.333333333333
PT_22 4096.5 1925.5
PT_23 3629.545454545455 1986.111111111111
PT_24 3444.191919191919 1995.707070707071
PT_25 3097.222222222223 2037.626262626263
PT_26 2957.323232323233 2023.484848484848
PT_27 2960.353535353536 1923.484848484849
PT_28 2782.070707070708 1901.767676767677
PT_29 2268.434343434344 1966.919191919192
PT_30 2076.010101010101 1965.909090909091
PT_31 1696.212121212121 1932.575757575758
PT_32 1529.545454545455 1959.343434343435
PT_33 1578.651685393258 2074.719101123596
PT_34 1757.828282828283 2055.808080808081
PT_35 1896.212121212121 2071.969696969697
PT_36 2107.323232323232 2050.757575757576
PT_37 2279.040404040404 2105.808080808081
PT_38 2280.555555555556 2215.909090909091
PT_39 2893.5 2216.5
PT_40 2895.505617977528 2548.876404494382

""")

        self.V2 = StringIO("""# CLIMATIC DATA ©CRENAU 2023
# CODING VERSION 2
# ROUTE_ID NANTES_COMMERCE_2023_1
# TIMEZONE Europe/Paris
# 40 POINTS FROM PT_0 TO PT_39
# 20 WAYPOINTS FROM WP_0 TO WP_19
MOVING FROM WP_0 TO WP_1
STARTING AT 1683202992761 ARRIVING AT 1683202995237
MOVING FROM WP_1 TO WP_2
STARTING AT 1683202997663 ARRIVING AT 1683202999375
MOVING FROM WP_2 TO WP_3
STARTING AT 1683203001815 ARRIVING AT 1683203003135
MOVING FROM WP_3 TO WP_4
STARTING AT 1683203005439 ARRIVING AT 1683203008871
MOVING FROM WP_4 TO WP_5
STARTING AT 1683203012615 ARRIVING AT 1683203015998
WARNING : Contournement d'un obstacle sur le trajet. Détour de 30m à droite.
MOVING FROM WP_5 TO WP_6
STARTING AT 1683203024383 PAUSING AT 1683203027151 RESUMING AT 1683203030423 PAUSING AT 1683203033575 RESUMING AT 1683203034967 PAUSING AT 1683203038535 RESUMING AT 1683203044862 ARRIVING AT 1683203047759
MOVING FROM WP_6 TO WP_7
STARTING AT 1683203050199 ARRIVING AT 1683203052863
MOVING FROM WP_7 TO WP_8
STARTING AT 1683203055183 ARRIVING AT 1683203058495
WARNING : Trop de gens dans l'espace, vitesse très lente.
MOVING FROM WP_8 TO WP_9
STARTING AT 1683203068767 ARRIVING AT 1683203072118
MOVING FROM WP_9 TO WP_10
STARTING AT 1683203074335 PAUSING AT 1683203077263 RESUMING AT 1683203079135 ARRIVING AT 1683203081694
MOVING FROM WP_10 TO WP_11
STARTING AT 1683203084086 ARRIVING AT 1683203087247
MOVING FROM WP_11 TO WP_12
STARTING AT 1683203090695 ARRIVING AT 1683203093543
MOVING FROM WP_12 TO WP_13
STARTING AT 1683203096487 ARRIVING AT 1683203098863
WARNING : nouvelle remarque...
MOVING FROM WP_13 TO WP_14
STARTING AT 1683203108583 ARRIVING AT 1683203110623
MOVING FROM WP_14 TO WP_15
STARTING AT 1683203112680 ARRIVING AT 1683203114583
MOVING FROM WP_15 TO WP_16
STARTING AT 1683203116926 ARRIVING AT 1683203118774
MOVING FROM WP_16 TO WP_17
STARTING AT 1683203121535 ARRIVING AT 1683203124198
MOVING FROM WP_17 TO WP_18
STARTING AT 1683203127918 PAUSING AT 1683203129375 RESUMING AT 1683203131191 PAUSING AT 1683203132278 RESUMING AT 1683203133520 CANCELING AND GOING BACK TO WP_17
MOVING FROM WP_17 TO WP_18
STARTING AT 1683203139502 ARRIVING AT 1683203142758
MOVING FROM WP_18 TO WP_19
STARTING AT 1683203145199 PAUSING AT 1683203149047 RESUMING AT 1683203150766 PAUSING AT 1683203152094 RESUMING AT 1683203153206 PAUSING AT 1683203155398 RESUMING AT 1683203156694 ARRIVING AT 1683203158390
WP_0 PT_0
WP_1 PT_2
WP_2 PT_5
WP_3 PT_6
WP_4 PT_7
WP_5 PT_12
WP_6 PT_13
WP_7 PT_16
WP_8 PT_18
WP_9 PT_21
WP_10 PT_22
WP_11 PT_26
WP_12 PT_27
WP_13 PT_29
WP_14 PT_31
WP_15 PT_32
WP_16 PT_33
WP_17 PT_36
WP_18 PT_37
WP_19 PT_39
PT_0 259.9935493549354 1550.620762076207
PT_1 551.0226522652266 1304.596159615962
PT_2 1070 752
PT_3 1300 1144
PT_4 1386 1158
PT_5 1463.383838383838 1319.444444444444
PT_6 2099.358974358974 1192.948717948718
PT_7 2182.692307692308 1541.666666666666
PT_8 2032.116788321168 1567.153284671533
PT_9 1900.757575757576 1548.232323232323
PT_10 1739.646464646465 1560.353535353535
PT_11 1631.565656565657 1548.737373737374
PT_12 1499.242424242424 1571.464646464647
PT_13 1513.291139240506 1606.962025316456
PT_14 1664.556962025316 1624.050632911392
PT_15 1740 1610.666666666667
PT_16 1879.545454545455 1627.525252525253
PT_17 2350.5 1559
PT_18 2706.313131313132 1531.565656565657
PT_19 2707.323232323232 1463.383838383838
PT_20 3349.747474747475 1479.545454545455
PT_21 4076.415094339622 1560.377358490566
PT_22 4072.641509433962 1927.358490566038
PT_23 3629.545454545455 1986.111111111111
PT_24 3444.191919191919 1995.707070707071
PT_25 3097.222222222223 2037.626262626263
PT_26 2957.323232323233 2023.484848484848
PT_27 2960.353535353536 1923.484848484849
PT_28 2782.070707070708 1901.767676767677
PT_29 2268.434343434344 1966.919191919192
PT_30 2076.010101010101 1965.909090909091
PT_31 1696.212121212121 1932.575757575758
PT_32 1536.708860759494 1957.911392405063
PT_33 1584.177215189874 2074.367088607595
PT_34 1757.828282828283 2055.808080808081
PT_35 1896.212121212121 2071.969696969697
PT_36 2107.323232323232 2050.757575757576
PT_37 2115.822784810127 2218.037974683544
PT_38 2893.5 2216.5
PT_39 2895.505617977528 2548.876404494382
""")

        self.V3 = StringIO("""# CLIMATIC DATA (C)CRENAU 2023
# CODING VERSION 3
# ROUTE_ID nantes-commerce-feydeau
# TRACK 1
# TIMEZONE Europe/Paris
# BEGINING 20230522T1749
# DRIVER tl
# 40 POINTS FROM PT_0 TO PT_39
# 20 WAYPOINTS FROM WP_0 TO WP_19
MOVING FROM WP_0 TO WP_1
STARTING AT 1684770600709 ARRIVING AT 1684770605598
MOVING FROM WP_1 TO WP_2
STARTING AT 1684770609182 ARRIVING AT 1684770613614
MOVING FROM WP_2 TO WP_3
STARTING AT 1684770618517 ARRIVING AT 1684770621422
MOVING FROM WP_3 TO WP_4
STARTING AT 1684770627365 ARRIVING AT 1684770631965
MOVING FROM WP_4 TO WP_5
STARTING AT 1684770635278 PAUSING AT 1684770640997 RESUMING AT 1684770643501 PAUSING AT 1684770647621 RESUMING AT 1684770650061 ARRIVING AT 1684770653701
MOVING FROM WP_5 TO WP_6
STARTING AT 1684770657877 ARRIVING AT 1684770663077
MOVING FROM WP_6 TO WP_7
STARTING AT 1684770666877 ARRIVING AT 1684770672269
MOVING FROM WP_7 TO WP_8
STARTING AT 1684770678766 ARRIVING AT 1684770681501
MOVING FROM WP_8 TO WP_9
STARTING AT 1684770687133 ARRIVING AT 1684770691021
MOVING FROM WP_9 TO WP_10
STARTING AT 1684770697165 ARRIVING AT 1684770702069
MOVING FROM WP_10 TO WP_11
STARTING AT 1684770707389 ARRIVING AT 1684770712045
MOVING FROM WP_11 TO WP_12
STARTING AT 1684770717789 ARRIVING AT 1684770724037
MOVING FROM WP_12 TO WP_13
STARTING AT 1684770733628 ARRIVING AT 1684770739509
MOVING FROM WP_13 TO WP_14
STARTING AT 1684770743092 CANCELING AND GOING BACK TO WP_13
MOVING FROM WP_13 TO WP_14
STARTING AT 1684770752380 ARRIVING AT 1684770756348
MOVING FROM WP_14 TO WP_15
STARTING AT 1684770759780 ARRIVING AT 1684770763108
MOVING FROM WP_15 TO WP_16
STARTING AT 1684770766284 ARRIVING AT 1684770770820
MOVING FROM WP_16 TO WP_17
STARTING AT 1684770773188 ARRIVING AT 1684770777396
MOVING FROM WP_17 TO WP_18
STARTING AT 1684770781612 PAUSING AT 1684770784452 RESUMING AT 1684770786436 CANCELING AND GOING BACK TO WP_17
MOVING FROM WP_17 TO WP_18
STARTING AT 1684770791956 ARRIVING AT 1684770797204
MOVING FROM WP_18 TO WP_19
CANCELING AND GOING BACK TO PREVIOUS SECTION AT WP_17
MOVING FROM WP_17 TO WP_18
STARTING AT 1684770805044 ARRIVING AT 1684770808492
MOVING FROM WP_18 TO WP_19
STARTING AT 1684770812004 ARRIVING AT 1684770816532
""")

        self.V4 = StringIO("""# CLIMATIC DATA (C)CRENAU 2023
# CODING VERSION 4
# PROJECT nantes_commerce_feydeau
# TRACK 1
# TIMEZONE Europe/Paris
# BEGINING 20230607T1530
# DRIVER Daniel
# 37 WAYPOINTS FROM WP_0 TO WP_36
MOVING FROM WP_0 TO WP_1
STARTING AT 1686144670158 ARRIVING AT 1686144762325
MOVING FROM WP_1 TO WP_2
STARTING AT 1686144810527 ARRIVING AT 1686144856306
MOVING FROM WP_2 TO WP_3
STARTING AT 1686144862366 ARRIVING AT 1686144899025
MOVING FROM WP_3 TO WP_4
STARTING AT 1686144903715 ARRIVING AT 1686144965881
MOVING FROM WP_4 TO WP_5
STARTING AT 1686144975186 ARRIVING AT 1686144998353
MOVING FROM WP_5 TO WP_6
STARTING AT 1686145023141 ARRIVING AT 1686145038751
MOVING FROM WP_6 TO WP_7
STARTING AT 1686145042721 ARRIVING AT 1686145054721
MOVING FROM WP_7 TO WP_8
STARTING AT 1686145057631 ARRIVING AT 1686145107762
MOVING FROM WP_8 TO WP_9
STARTING AT 1686145116931 ARRIVING AT 1686145209161
MOVING FROM WP_9 TO WP_10
STARTING AT 1686145213767 ARRIVING AT 1686145312006
WARNING : Pause de 4 secondes au niveau du magasin ramen à cause de 2 personnes non voyantes arrivant en face
MOVING FROM WP_10 TO WP_11
STARTING AT 1686145367238 ARRIVING AT 1686145453337
MOVING FROM WP_11 TO WP_12
STARTING AT 1686145460025 ARRIVING AT 1686145538209
MOVING FROM WP_12 TO WP_13
STARTING AT 1686145553666 ARRIVING AT 1686145595831
MOVING FROM WP_13 TO WP_14
STARTING AT 1686145612030 ARRIVING AT 1686145645827
MOVING FROM WP_14 TO WP_15
STARTING AT 1686145666549 ARRIVING AT 1686145721567
MOVING FROM WP_15 TO WP_16
STARTING AT 1686145736314 ARRIVING AT 1686145745772
MOVING FROM WP_16 TO WP_17
STARTING AT 1686145770598 ARRIVING AT 1686145815209
MOVING FROM WP_17 TO WP_18
STARTING AT 1686145865914 ARRIVING AT 1686145913970
MOVING FROM WP_18 TO WP_19
STARTING AT 1686145924440 ARRIVING AT 1686145976436
MOVING FROM WP_19 TO WP_20
STARTING AT 1686145984455 ARRIVING AT 1686145997444
MOVING FROM WP_20 TO WP_21
STARTING AT 1686146012795 ARRIVING AT 1686146101487
MOVING FROM WP_21 TO WP_22
STARTING AT 1686146111244 ARRIVING AT 1686146195816
MOVING FROM WP_22 TO WP_23
STARTING AT 1686146207083 ARRIVING AT 1686146252459
MOVING FROM WP_23 TO WP_24
STARTING AT 1686146309297 ARRIVING AT 1686146367194
MOVING FROM WP_24 TO WP_25
STARTING AT 1686146408210 ARRIVING AT 1686146495928
MOVING FROM WP_25 TO WP_26
STARTING AT 1686146502875 ARRIVING AT 1686146518281
MOVING FROM WP_26 TO WP_27
STARTING AT 1686146542383 ARRIVING AT 1686146637816
MOVING FROM WP_27 TO WP_28
STARTING AT 1686146656126 ARRIVING AT 1686146735540
MOVING FROM WP_28 TO WP_29
STARTING AT 1686146740864 ARRIVING AT 1686146765968
MOVING FROM WP_29 TO WP_30
STARTING AT 1686146776080 ARRIVING AT 1686146788897
MOVING FROM WP_30 TO WP_31
STARTING AT 1686146797299 ARRIVING AT 1686146843260
MOVING FROM WP_31 TO WP_32
STARTING AT 1686146858555 ARRIVING AT 1686146888622
MOVING FROM WP_32 TO WP_33
STARTING AT 1686146938781 ARRIVING AT 1686146960200
MOVING FROM WP_33 TO WP_34
STARTING AT 1686146967767 ARRIVING AT 1686147075495
MOVING FROM WP_34 TO WP_35
STARTING AT 1686147084269 ARRIVING AT 1686147157978
MOVING FROM WP_35 TO WP_36
STARTING AT 1686147165663 ARRIVING AT 1686147207057
""")

    def tearDown(self):
        pass

    def testRunV1(self):
        df = UClimGuidingReader(self.V1).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(5, len(df.columns), "Count columns")
        self.assertEqual(20, len(df), "Count rows")

        self.assertTrue(df.wp1.is_monotonic_increasing, "The wp1 column is increasing")
        self.assertTrue(df.wp1.is_unique, "The wp1 column is strictly increasing")

        self.assertTrue(df.wp2.is_monotonic_increasing, "The wp2 column is increasing")
        self.assertTrue(df.wp2.is_unique, "The wp2 column is strictly increasing")

        self.assertTrue(df.timestamps.explode().is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamps.explode().is_unique, "The timestamps are strictly increasing")

        for _, row in df.iterrows():
            self.assertEqual(1, row.wp2 - row.wp1, "The difference between 2 consecutive waypoints is equal to 1")
            delta = UClimGuidingReader.timedeltaBetweenTwoWaypoints(row.timestamps)
            self.assertLess(0, delta.seconds, "Timedelta between 2 consecutive waypoints")

    def testRunV2(self):
        df = UClimGuidingReader(self.V2).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(6, len(df.columns), "Count columns")
        self.assertEqual(19, len(df), "Count rows")

        self.assertTrue(df.wp1.is_monotonic_increasing, "The wp1 column is increasing")
        self.assertTrue(df.wp1.is_unique, "The wp1 column is strictly increasing")

        self.assertTrue(df.wp2.is_monotonic_increasing, "The wp2 column is increasing")
        self.assertTrue(df.wp2.is_unique, "The wp2 column is strictly increasing")

        self.assertTrue(df.timestamps.explode().is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamps.explode().is_unique, "The timestamps are strictly increasing")

        for _, row in df.iterrows():
            self.assertEqual(1, row.wp2 - row.wp1, "The difference between 2 consecutive waypoints is equal to 1")
            delta = UClimGuidingReader.timedeltaBetweenTwoWaypoints(row.timestamps)
            self.assertLess(0, delta.seconds, "Timedelta between 2 consecutive waypoints")

    def testRunV3(self):
        df = UClimGuidingReader(self.V3).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(7, len(df.columns), "Count columns")
        self.assertEqual(19, len(df), "Count rows")

        self.assertTrue(df.wp1.is_monotonic_increasing, "The wp1 column is increasing")
        self.assertTrue(df.wp1.is_unique, "The wp1 column is strictly increasing")

        self.assertTrue(df.wp2.is_monotonic_increasing, "The wp2 column is increasing")
        self.assertTrue(df.wp2.is_unique, "The wp2 column is strictly increasing")

        self.assertTrue(df.timestamps.explode().is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamps.explode().is_unique, "The timestamps are strictly increasing")

        for _, row in df.iterrows():
            self.assertEqual(1, row.wp2 - row.wp1, "The difference between 2 consecutive waypoints is equal to 1")
            delta = UClimGuidingReader.timedeltaBetweenTwoWaypoints(row.timestamps)
            self.assertLess(0, delta.seconds, "Timedelta between 2 consecutive waypoints")

    def testRunV4(self):
        df = UClimGuidingReader(self.V4).run()

        self.assertIsInstance(df, DataFrame, "Is a DataFrame")
        self.assertEqual(7, len(df.columns), "Count columns")
        self.assertEqual(36, len(df), "Count rows")

        self.assertTrue(df.wp1.is_monotonic_increasing, "The wp1 column is increasing")
        self.assertTrue(df.wp1.is_unique, "The wp1 column is strictly increasing")

        self.assertTrue(df.wp2.is_monotonic_increasing, "The wp2 column is increasing")
        self.assertTrue(df.wp2.is_unique, "The wp2 column is strictly increasing")

        self.assertTrue(df.timestamps.explode().is_monotonic_increasing, "The timestamps are increasing")
        self.assertTrue(df.timestamps.explode().is_unique, "The timestamps are strictly increasing")

        for _, row in df.iterrows():
            self.assertEqual(1, row.wp2 - row.wp1, "The difference between 2 consecutive waypoints is equal to 1")
            delta = UClimGuidingReader.timedeltaBetweenTwoWaypoints(row.timestamps)
            self.assertLess(0, delta.seconds, "Timedelta between 2 consecutive waypoints")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
