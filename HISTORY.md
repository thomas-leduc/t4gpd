# Package t4gpd history

## Version 0.6.0 - rev. 13549 - 23 Mar. 2023
* Add new Docker image (see https://github.com/thomas-leduc/t4gpd-docker)
* Add new tests.misc.OptimalNumberOfClustersTest class
* Add new misc.OptimalNumberOfClusters class
* Add new demos.GeoDataFrameDemos9 class
* Add new tests.morph.STBBoxTest class
* Add new morph.STBBox class
* Add new morph.STVariableWidthBuffer class
* Add new misc.RoseMappingTool class
* Add new tests.commons.random.RandomPointPickingTest class
* Add new commons.random.RandomPointPicking class
* Add new misc.TimelineTool class
* Add new commons.sun.DaylightLib class
* Add new picoclim.ExtraProcessing class

## Version 0.5.0 - rev. 12961 - 14 Nov. 2022
* Add new tests.io.{GpkgLoaderTest,GpkgWriterTest} classes
* Add new io.{GpkgLoader,GpkgWriter} classes
* Add new tests.morph.geoProcesses.RectifyByFWTTest class
* Add new tests.morph.geoProcesses.RectifyByFFTTest class
* Add new tests.morph.geoProcesses.CrossroadsStarDomainTest class
* Add new tests.morph.geoProcesses.CrossroadsAngularityTest class
* Add new morph.geoProcesses.RectifyByFWT class
* Add new morph.geoProcesses.RectifyByFFT class
* Add new morph.geoProcesses.CrossroadsStarDomain class
* Add new morph.geoProcesses.CrossroadsAngularity class
* Add new tests.commons.KernelLibTest class
* Add new commons.KernelLib class
* Add new tests.morph.geoProcesses.CrossroadRecognitionTest class
* Add new morph.geoProcesses.CrossroadRecognition class
* Add new commons.crossroads_identification.CrossroadRecognitionLib class
* Add new commons.crossroads_identification.FFTMethod class
* Add new commons.crossroads_identification.FWTMethod class
* Add new commons.crossroads_identification.MeanAngularityMethod class
* Add new commons.crossroads_identification.MeanVectorMethod class
* Add new commons.crossroads_identification.AbstractMethod
* Add new tests.morph.STCrossroadsGenerationTest class
* Add new morph.STCrossroadsGeneration class
* Add new tests.commons.crossroads_generation.SequenceRadiiTest class
* Add new tests.commons.crossroads_generation.SequencesGenerationTest class
* Add new tests.commons.crossroads_generation.SequenceTest class
* Add new commons.crossroads_generation.SequenceRadii class
* Add new commons.crossroads_generation.SequencesGeneration class
* Add new commons.crossroads_generation.Sequence class
* Add new demos.GeoDataFrameDemos{6,7,8} classes
* Add new tests.commons.DataFrameLibTest class
* Add new commons.DataFrameLib class
* Add new picoclim.MeteoFranceReader class
* Add new picoclim.MetrologicalCampaignPlottings class
* Add new morph.STSquaredBBox class
* Add new picoclim.SnapImuOnTrackUsingWaypoints class
* Add new picoclim.TracksWaypointsReader class
* Add new tests.commons.SphericalProjectionLibTest class
* Add new commons.SphericalProjectionLib class
* Add new tests.commons.PointsDensifierLib3DTest class
* Add new commons.PointsDensifierLib3D class
* Add new picoclim.MetrologicalCampaignReader class
* Add new picoclim.InertialMeasureReader class
* Add new picoclim.CampbellSciReader class
* Add new picoclim.KestrelReader class
* Add new picoclim.SensirionReader class

## Version 0.4.1 - rev. 12508 - 24 Aug. 2022
* Third release on PyPI
* Add new pyqgis.Emphasizer class
* Add new io.{CirValReader,ValReader} classes
* Add new io.SalomeWriter class
* Add new tests.pyvista.geoProcesses.{Oriented,Panoptic}RayCasting3DTest classes
* Add new pyvista.geoProcesses.{Oriented,PanopticRay}Casting3D classes
* Add new tests.pyvista.geoProcesses.AutomaticFaceOrientationTest class
* Add new pyvista.geoProcesses.AutomaticFaceOrientation class
* Add new tests.pyvista.geoProcesses.FromContourToNormalVectorTest class
* Add new pyvista.geoProcesses.FromContourToNormalVector class
* Add new pyqgis.MapPrinter class
* Add new morph.RepresentativePoint class
* Add new tests.pyvista.STRaysToViewFactorsTest class
* Add new tests.pyvista.{GeodeCiel,Icosahedron}Test classes
* Add new pyvista.{GeodeCiel,Icosahedron} classes
* Add new pyvista.commons.Triangle3D class
* Add new pyvista.geoProcesses.MoveSensorsAwayFromSurface class
* Add new pyvista.commons.RayCasting3DLib class
* Add new pyvista.STRaysToViewFactors class
* Add new io.AbstractReader class
* Add new tests.raster.STToRasterTest class
* Add new raster.STToRaster class
* Add new commons.RayCasting3Lib class
* Add new commons.RayCasting2Lib class
* Enhance commons.GeomLib with new meth. {getAnchoringBuildingId, isABorderPoint, isAnOutdoorPoint}(...) + refactor isAnIndoorPoint(...)
* Debug commons.SVFLib class
* Add new tests.pyvista.ToUnstructuredGridTest class
* Add new pyvista.ToUnstructuredGrid class
* Add new tests.morph.STPointsDensifier2Test class
* Add new morph.STPointsDensifier2 class
* Add new PointsDensifierLib.densifyByCurvilinearAbscissa(...) static method
* Add new GridFaceLib class
* Add new demos.GeoDataFrameDemos{2,3,4,5} classes
* Add new pyplot.MultipleMarkerStyles class
* Update demos.GeoDataFrameDemos class
* Update geoProcesses.StarShapedIndices class
* Rename class commons.ShannonEntropy to commons.Entropy
* Add new file CITATION.cff

## Version 0.3.0 - rev. 11625 - 9 Dec. 2021
* Second release on PyPI
* Add new tests.io.ZipLoaderTest class
* Add new io.ZipLoader class
* Add new misc.PopulationPyramid class
* Add new pyqgis/{AddMemoryLayer,SetSymbolLib,ShowFeatureCount,ZoomLib} classes
* Add new tests datasets: la_defense_{measurepts.csv, pathway.gpkg, waypoints.gpkg}
* Add new tests.io.ZipWriterTest class
* Add new io.ZipWriter class
* Add new io.Reloading class
* Add new tests.commons.CalendarLibTest class
* Add new commons.CalendarLib class
* Add new tests.morph.geoProcesses.{GetInteriorPointTest, IsAnIndoorPointTest} classes
* Add new morph.geoProcesses.{GetInteriorPoint, IsAnIndoorPoint} classes
* Add new comfort.{Empirical,Linear,Universal}ThermalIndices classes
* Add new comfort.indices.Tmrt{GlobeTemperature,Out,Radiometer} classes
* Add new comfort.indices.{ASV,DI,ETU,H,HI,NET,OUTSET,PE,PET,PMV,PT,SET,SETmist,THI,UTCI,WCT} classes
* Add new comfort.indices.AbstractThermalComfortIndice class
* Add new comfort.algo.Tmrt{GlobeTemperature,Out}Lib classes
* Add new comfort.algo.{ETU,PET,PMV,PT,SET,UTCI}Lib classes
* Add new comfort.algo.WindSpeedExtrapolationLib class
* Add new comfort.algo.{Constants,Commons}Lib classes

## Version 0.2.0 - rev. 11186 - 30 Apr. 2021
* First release on PyPI
* Add new tests.sun.STTreeHardShadow2Test class
* Add new tests.commons.sun.ShadowLibTest class
* Add new commons.sun.ShadowLib class
* Add new tests.commons.sun.AbstractSunLibTest class
* Add new tests.morph.STPointsDensifierTest class
* Add new morph.STPointsDensifier class
* Add new tests.commons.PointsDensifierLibTest class
* Add new commons.PointsDensifierLib class
* Add new tests.commons.LineStringCuttingLibTest class
* Add new commons.LineStringCuttingLib class
* Delete commons.GridLib class
* Add new tests.commons.grid.GridLibTest class
* Add new commons.grid.GridLib class
* Add new commons.grid.AbstractGridLib class
* Add new tests.morph.STFacadesAnalysisTest class
* Add new morph.STFacadesAnalysis class
* Add new tests.morph.geoProcesses.GridFaceTest class
* Add new morph.geoProcesses.GridFace class
* Add new tests.commons.GridLibTest class
* Add new commons.GridLib class
* Add new commons.Logos class
* Add new tests.future.commons.distance.BoxCountingDistanceTest class
* Add new future.commons.distance.BoxCountingDistance class
* Add new tests.io.{CirReaderTest,CirWriterTest} classes ( + new dataset: cube_unitaire.cir)
* Add new io.CirWriter class
* Add new commons.GeomLib3D class
* Add new tests.sun.geoProcesses.SunshineDurationOnTopOfRoofTest class
* Add new sun.geoProcesses.SunshineDurationOnTopOfRoof class
* Add new tests.sun.geoProcesses.SunshineDurationTest class
* Add new sun.geoProcesses.{AbstractSunshineDuration,SunshineDuration} classes
* Add new tests.morph.geoProcesses.SkyViewFactorOnTopOfRoofTest class
* Add new morph.geoProcesses.SkyViewFactorOnTopOfRoof class
* Add new misc.WindRose class
* Add new tests.morph.geoProcesses.FootprintExtruderTest class
* Add new morph.geoProcesses.FootprintExtruder class
* Remove sun.SunPosition2 class
* Add new tests.commons.DatetimeLibTest class
* Add new commons.DatetimeLib class
* Add new tests.commons.sun.{PySolarSunLibTest,SoleneSunLibTest,SunLibTest} classes
* Add new commons.sun.{AbstractSunLib,PySolarSunLib,SoleneSunLib,SunLib} classes
* Add new tests.commons.LatLonLibTest class
* Add new commons.LatLonLib class
* Add new tests.sun.STSunMap2DTest class
* Add new sun.STSunMap2D class
* Add new tests.morph.geoProcesses.StarShapedIndicesTest class
* Add new morph.geoProcesses.StarShapedIndices class
* Add new commons.ShannonEntropy class
* Add new tests.morph.geoProcesses.MABR2Test class
* Add new morph.geoProcesses.MABR2 class
* Add new tests.morph.geoProcesses.HeightOfRoughnessTest class
* Add new morph.geoProcesses.HeightOfRoughness class
* Add new tests.morph.geoProcesses.SurfaceFractionTest class
* Add new morph.geoProcesses.SurfaceFraction class
* Add new tests.misc.STDendrogramTest class
* Add new misc.STDendrogram class
* Add new tests.misc.STKMeansTest class
* Add new misc.STKMeans class
* Add new morph.STPolygonize class
* Add new graph.STBetweennessCentrality class
* Add new morph.geoProcesses.{Circularity,Convexity,Ellipticity,Rectangularity} classes
* Add new graph.STClosenessCentrality class
* Add new tests.commons.graph.MCALibTest class
* Add new commons.graph.MCALib class
* Add new tests.morph.geoProcesses.MPBRTest class
* Add new morph.geoProcesses.MPBR class
* Add new tests.commons.CaliperLibTest class
* Add new commons.CaliperLib class
* Add new tests.morph.geoProcesses.MBCTest class
* Add new morph.geoProcesses.MBC class
* Add new tests.commons.ChrystalAlgorithmTest class
* Add new commons.ChrystalAlgorithm class
* Add new tests.morph.STExtractOpenSpacesTest class
* Add new morph.STExtractOpenSpaces class
* Add new datasets jardin_extraordinaire_{path,points,waypoints}5.shp
* Add new tests.morph.geoProcesses.SkyMap2DTest class
* Add new morph.geoProcesses.SkyMap2D class
* Add new tests.graph.{STShortestPathTest, STRoadNeighborhoodTest} classes
* Add new graph.{STShortestPath, STRoadNeighborhood} classes
* Add new tests.commons.graph.{ShortestPathLibTest, NeighborhoodLibTest} classes
* Add new commons.graph.{AbstractUrbanGraphLib, ShortestPathLib, NeighborhoodLib, UrbanGraphLib} classes
* Add new misc.StreetOrientationHistogram class
* Add new sun.SunPosition2 class
* Add new commons.LandoltRingLib class
* Add new io.CityGMLReader class
* Add new io.CirReader class
* Add new io.ObjWriter class
* Add new tests.morph.geoProcesses.CanyonStreetOrientationTest class
* Add new morph.geoProcesses.CanyonStreetOrientation class
* Add new tests.morph.STGradientOfDistancesToBuildingsTest class
* Add new morph.STGradientOfDistancesToBuildings class
* Add new commons.Checksum class
* Add new tests.morph.STCoolscapesTessellationTest class
* Add new morph.STCoolscapesTessellation class
* Add new tests.io.CSVWKTWriterTest class
* Add new misc.FrequencyHistogram class
* Add new tests.morph.geoProcesses.AspectRatioTest class
* Add new morph.geoProcesses.AspectRatio class
* Add new tests.morph.geoProcesses.SkyViewFactorTest class
* Add new morph.geoProcesses.SkyViewFactor class
* Add new commons.SVFLib class
* Add new tests.morph.geoProcesses.HMeanTest class
* Add new morph.geoProcesses.HMean class
* Add new tests.morph.geoProcesses.WMeanTest class
* Add new morph.geoProcesses.WMean class
* Add new tests.morph.STSkeletonizeTest class
* Add new morph.STSkeletonize class
* Add new tests.morph.STSkeletonizeTheVoidTest class
* Add new morph.STSkeletonizeTheVoid class
* Add new tests.morph.STVoronoiPartitionTest class
* Add new morph.STVoronoiPartition class
* Add new tests.STSnappingPointsOnLines2Test class (+ new dataset: jardin_extraordinaire_waypoints.shp)
* Add new morph.STSnappingPointsOnLines2 class
* Add new tests.STSnappingPointsOnLinesTest class (+ new dataset: jardin_extraordinaire_path.{csv,shp})
* Add new morph.STSnappingPointsOnLines class
* Add new tests.STMultipleOverlaps2Test class
* Add new morph.STMultipleOverlaps2 class
* Add new tests.STIdentifyRowOfTreesTest class
* Add new morph.STIdentifyRowOfTrees class
* Add new tests.IdentifyTheClosestPolylineTest class
* Add new morph.geoProcesses.IdentifyTheClosestPolyline class
* Add new tests.TranslationTest class
* Add new morph.geoProcesses.Translation class
* Add new tests.STMultipleOverlapsTest class
* Add new morph.STMultipleOverlaps class
* Add new sun.AbstractHardShadow class
* Add new tests.Rotation2DTest class
* Add new morph.geoProcesses.Rotation2D class
* Add new tests.commons.RotationLibTest
* Add new sun.STTreeHardShadow2 class
* Add new io.VTUWriter class
* Add new io.CSVWKTWriter class
* Add new tests.io.CSVWKTReaderTest class (+ new dataset: ensa_nantes.wkt)
* Add new io.CSVWKTReader class
* Add new tests.sun.STTreeHardShadowTest
* Add new sun.STTreeHardShadow class
* Add new commons.RotationLib class
* Add new sun.STHardShadow class
* Add new tests.ObjReaderTest class (+ new dataset: surfaceWithHole.obj)
* Add new tests.STSunshineHoursTest class
* Add new sun.STSunshineHours class
* Add new energy.{Dogniaux,Perez,Perraudeau,PerrinDeBrichambaut,PlotDirectNormalIrradiance} classes
* Add new tests.DateTimeGeneratorTest class
* Add new sun.{SunPosition,DateTimeGenerator} classes
* Add new io.ObjReader class

## Version 0.1.0 - rev. 9698 - 18 Jul. 2020
* Add new tests.MABETest class
* Add new tests.STClipTest class
* Add new morph.STClip class
* Add new morph.geoProcesses.MABE class
* Add new commons.ellipse.{EllipseLib,EllipticHullLib} classes
* Add new commons.{Distances,ListUtilities,PolarCartesianCoordinates} classes
* Add new tests.STSpatialJoinTest class
* Add new morph.STSpatialJoin class
* Add new tests.DiameterTest class
* Add new morph.geoProcesses.Diameter class
* Add new commons.{AngleLib,DiameterLib} classes
* Add new commons.IllegalArgumentTypeException class
* Add new tests.STDilationErosionTest class
* Add new morph.STDilationErosion class
* Add new tests.STLoadAndClipTest class
* Add new io.STLoadAndClip class
* Add new tests.AngularAbscissaTest class
* Add new morph.geoProcesses.AngularAbscissa class
* Add new tests.GmshTriangulatorTest class
* Add new morph.GmshTriangulator class
* Add new io.{GeoWriter,MshReader,SVGWriter} classes
* Add new commons.{Epsilon,MyNode,MyEdge} classes
* Add new Version class
* Add new tests.STIsovistField2DTest class
* Add new isovist.STIsovistField2D class
* Add new commons.RayCastingLib
* Add new tests.{STToRoadsSectionsTest,STToRoadsSectionsNodesTest} classes
* Add new graph.{STToRoadsSections,STToRoadsSectionsNodes} classes
* Add new commons.UrbanGraphLib
* Add new tests.STDensifierTest class
* Add new tests/data/ensa_nantes_roads.shp dataset
* Add new morph.STDensifier class
* Add new commons.{ArrayCoding,DensifierLib,GeomLib} class
* Add new tests.MABRTest class
* Add new morph.geoProcesses.MABR class
* Add new tests.RemoveHolesTest class
* Add new morph.geoProcesses.RemoveHoles class
* Add new tests.ConvexHullTest class
* Add new morph.geoProcesses.ConvexHull class
* Add new tests.BBoxTest class
* Add new morph.geoProcesses.BBox class
* Add new tests.AreaConvexityDefectTest class
* Add new morph.geoProcesses.AreaConvexityDefect class
* Add new morph.geoProcesses.{AbstractGeoprocess,STGeoProcess} class
* Add new tests.STGridTest class
* Add new tests/data/ensa_nantes.shp dataset
* Add new morph.STGrid class
* Add new commons.BoundingBox class
* Add new commons.GeoProcess class
