'''
Created on 8 juin 2023

@author: tleduc

Copyright 2020-2022 Thomas Leduc

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
from io import StringIO
import unittest

from geopandas import GeoDataFrame

from t4gpd.picoclim.UClimTrackWaypointsReader import UClimTrackWaypointsReader


class UClimTrackWaypointsReaderTest(unittest.TestCase):

    def setUp(self):
        self.V1 = StringIO("""ptid;lat;long;waypoint;localmap_x;localmap_y;start_instruction;end_instruction
1;47.21177165;-1.557155871;1;1814.35;3124.45;Se placer au centre de l’allée entre les arbres juste à côté du poteau des panneaux de direction (Ouest-centre-ville, etc.) et avancer tout droit dans l'allée vers le Nord.;
2;47.21230629;-1.557631701;1;1808.27;2310.29;Continuer vers le centre des 4 arbres puis tourner à gauche sur le chemin.;Entre les deux arbres du bout de l’allée dans l’alignement avec le passage piéton à droite.
3;47.21233043;-1.557667723;0;1796.92;2266.91;;
4;47.21220043;-1.557996443;1;1459.72;2262.93;Continuer en restant sur le chemin à droite.;Au milieu de la grille d’entrée du parc à gauche.
5;47.21214217;-1.558106644;0;1336.88;2278.01;;
6;47.21209012;-1.558171063;0;1253.08;2306.95;;
7;47.21201984;-1.558228283;1;1162.61;2359.55;Continuer le chemin à droite.;A la bifurcation des chemins. 
8;47.21187003;-1.55845898;0;886.89;2422.26;;
9;47.2117751;-1.558691332;1;646.51;2422.85;Tourner à droite et continuer jusqu’au passage clouté.;Au milieu du trottoir qui longe la voie de circulation.
10;47.21182982;-1.558695001;0;680.22;2359.97;;
11;47.21188483;-1.558728779;0;691.16;2283.1;;
12;47.21191966;-1.558769053;1;683.69;2225.85;Traverser à gauche du passage clouté sur la route jusqu’à la voie de tramway.;Sur le bord gauche de la bande pour non-voyants avant le passage clouté.
13;47.21196384;-1.558933536;1;587.81;2101.7;Traverser la voie de tramway.;A gauche des poteaux avant la voie de tramway.
14;47.21200083;-1.559025878;1;542.11;2018.36;Traverser vers la place de la Bourse.;Au panneau indiquant les hôtels.
15;47.21216375;-1.559467621;1;314.12;1635.42;Tourner à droite et continuer vers la rue de la Fosse.;Avant l’angle entre la place de la Bourse et la rue Jean-Jacques Rousseau.
16;47.21248003;-1.559313605;0;642.42;1351.69;;
17;47.21268849;-1.559212817;1;858.26;1164.34;Continuer jusqu’au passage Pommeraye.;Au numéro 6 de la place de la Bourse, porte bleue avant le coiffeur.
18;47.21290194;-1.559118053;0;1072.82;968.69;;
19;47.21328946;-1.558999337;1;1421.73;589.24;Devant l'entrée du passage Pommeraye, tourner vers la rue François Salières.;Au centre devant l'entrée du passage Pommeraye.
20;47.21328762;-1.558920978;0;1480.21;626.91;;
21;47.21313391;-1.558520722;0;1682.72;980.7;;
22;47.21315675;-1.558421848;0;1773.3;1000.08;;
23;47.21307995;-1.558228254;1;1869.61;1173.95;Devant la FNAC, à environ 1m50 du bas des marches, axer le chariot sur la ligne entre les pavés.;Devant la FNAC, à environ 1m50 du bas des marches. Passer par les trappes au sol pour les points intermédiaires.
24;47.21342053;-1.55767534;1;2518.09;1044.3;Entre le café La Coquille et le café Le Nantais, tourner vers le tramway et suivre le caniveau.;Entre le café La Coquille et le café Le Nantais, juste avant la grille au sol.
25;47.2133058;-1.557503533;0;2572.5;1250.68;;
26;47.21321355;-1.557389319;1;2598.02;1405.75;Au milieu du parterre à gauche, tourner vers les fontaines.;Au niveau du milieu du parterre à gauche, au point de changement de pavage.
27;47.2131382;-1.557516295;0;2451.01;1432.32;;
28;47.21309667;-1.55765431;1;2318.14;1416.05;Au niveau du début de la fontaine de gauche, continuer entre les fontaines.;Entre les 2 fontaines, au niveau du début de la fontaine de gauche.
29;47.2130435;-1.557775725;0;2190.15;1420.35;;
30;47.21299272;-1.557936382;0;2033.86;1404.13;;
31;47.21292443;-1.558036549;1;1911.99;1434.99;Au niveau de la façade de la FNAC après la dernière fontaine, tourner vers le sud et monter 1 marche.;Au niveau de la façade de la FNAC après la dernière fontaine.
32;47.21289801;-1.557980546;1;1937.04;1489.99;Tourner à gauche pour continuer en cheminant entre les fontaines.;Entre les deux fontaines.
33;47.21295116;-1.557856345;0;2067.14;1486.98;;
34;47.21299278;-1.55777976;0;2153.25;1475.24;;
35;47.2130344;-1.557628921;1;2295.96;1497.23;Avant le dernier banc le long de la fontaine, continuer vers les arbres.;Juste avant le dernier banc le long de la fontaine à gauche.
36;47.21324843;-1.557276551;1;2707.22;1417.98;Au niveau du premier arbre, continuer tout droit.;Au niveau du premier arbre en restant à gauche de l’arbre.
37;47.21343352;-1.556850254;1;3155.51;1404.68;Au niveau du parterre végétal, tourner à gauche.;Juste avant le deuxième parterre végétal après avoir passé 2 arbres.
38;47.21349008;-1.556897594;1;3157.15;1319.92;Juste après le parterre végétal, tourner à droite et continuer en longeant les parterres à environ 2m50.;Juste après le parterre végétal à environ 2m50.
39;47.2137158;-1.556339703;0;3732.82;1320.97;;
40;47.21375365;-1.556209035;1;3857.64;1338.01;Au niveau du début du parterre végétal, continuer vers le tramway ligne 2 en longeant les parterres à environ 2m50.;Au niveau du début du 3ème parterre végétal à environ 2m50.
41;47.21396462;-1.55548175;1;4552.56;1432.52;Au niveau des voies de tramway ligne 2, tourner vers le Sud.;Au niveau du lampadaire près du tramway après avoir longé les parterres végétaux.
42;47.21370876;-1.555285211;1;4531.72;1807.98;Entre les deux parterres végétaux, tourner vers l'Ouest.;Entre les deux parterres végétaux le long des voies de tramway.
43;47.21350571;-1.555668397;1;4104.3;1860.97;Au niveau du début du parterre à gauche.;Au niveau du début du 2ème parterre à gauche.
44;47.21341949;-1.555847878;0;3910.03;1875.84;;
45;47.21325144;-1.556171267;0;3551.52;1916.85;;
46;47.21319433;-1.556318409;1;3401.3;1913.86;Juste après le 3ème parterre, tourner vers le Nord.;Juste après le 3ème parterre.
47;47.21327702;-1.556379341;1;3410.01;1793.7;Entre les 2 parterres végétaux, tourner vers l'Ouest.;Entre les 2 parterres végétaux.
48;47.21320367;-1.556563375;0;3220.85;1792.11;;
49;47.21298274;-1.557046711;1;2705.18;1819.57;Au niveau de la fin du dernier parterre à gauche.;Au niveau de la fin du dernier parterre à gauche après avoir traversé les parterres végétaux.
50;47.21285465;-1.557345181;0;2392.31;1827.2;;
51;47.21275105;-1.557633445;1;2103.55;1812.07;Au niveau de la fin de la dernière fontaine à gauche.;Au niveau de la fin de la dernière fontaine à gauche.
52;47.2126762;-1.557778182;1;1943.34;1830.01;Au milieu des deux derniers parterres végétaux, tourner vers le Sud.;Au milieu des deux derniers parterres végétaux.
53;47.21262442;-1.557673352;1;1988.69;1935.57;Le long du parterre végétal au niveau du banc, continuer en longeant le banc.;Le long du parterre végétal au niveau du banc.
54;47.21269242;-1.557515218;0;2154.54;1931.37;;
55;47.21274032;-1.557354144;1;2309.24;1950.99;Au niveau du milieu du banc à droite.;Au niveau du milieu du banc à droite.
56;47.21284125;-1.557148806;1;2533.03;1931.41;Au niveau de la dernière fontaine à gauche, tourner vers le Sud.;Au niveau de la dernière fontaine à gauche après avoir longé le banc.
57;47.21272925;-1.557046438;1;2536.35;2103.19;Sur le quai vers les marches au niveau de la ligne verte, tourner vers l'Est.;Sur le quai vers les marches au niveau du coiffeur du Commerce.
58;47.21305218;-1.556250834;1;3358;2103.55;Au niveau de la rue Du Guesclin, tourner vers l’île Feydeau.;Au niveau de la rue Du Guesclin.
59;47.21269099;-1.555941681;1;3352.73;2647.98;Au croisement de la rue Du Guesclin et de la rue Kervégan, tourner à droite.;Au croisement de la rue Du Guesclin et de la rue Kervégan après avoir suivi la ligne verte.
60;47.21254937;-1.556273561;1;3005.38;2655.57;;Terminus au niveau du numéro 17 rue Kervégan.
""")

    def tearDown(self):
        pass

    def testRun(self):
        tracks, waypoints = UClimTrackWaypointsReader(self.V1).run()

        self.assertIsInstance(tracks, GeoDataFrame, "Is a GeoDataFrame (1)")
        self.assertEqual(1, len(tracks), "Count rows (1)")
        self.assertEqual(2, len(tracks.columns), "Count columns (1)")

        self.assertIsInstance(waypoints, GeoDataFrame, "Is a GeoDataFrame (2)")
        self.assertEqual(37, len(waypoints), "Count rows (2)")
        self.assertEqual(4, len(waypoints.columns), "Count columns (2)")
        self.assertTrue(waypoints.id.is_monotonic_increasing, "id is monotonic increasing")
        for idx, row in waypoints.iterrows():
            if (idx + 1 < len(waypoints) - 1):
                self.assertAlmostEqual(
                    waypoints.loc[idx + 1, "curv_absc"],
                    waypoints.loc[idx, "curv_absc"] + waypoints.loc[idx, "sect_len"],
                    None,
                    "delta_acur is badly assessed",
                    1e-1)

        track = tracks.geometry.squeeze()
        for _, row in waypoints.iterrows():
            p0, p1 = row.geometry, track.interpolate(track.project(row.geometry))
            self.assertEqual(0.0, p0.distance(p1), "Distances from waypoints to track are equal to zero")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
