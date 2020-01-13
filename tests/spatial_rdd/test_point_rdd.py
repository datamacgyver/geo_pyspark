import os

import pytest
from pyspark import StorageLevel

from geo_pyspark.core.SpatialRDD import PointRDD
from geo_pyspark.core.enums import IndexType, GridType, FileDataSplitter
from geo_pyspark.core.geom_types import Envelope
from tests.test_base import TestBase
from tests.tools import tests_path

inputLocation = os.path.join(tests_path, "resources/arealm-small.csv")
queryWindowSet = os.path.join("zcta510-small.csv")
offset = 1
splitter = FileDataSplitter.CSV
gridType = "rtree"
indexType = "rtree"
numPartitions = 11
distance = 0.01
queryPolygonSet = "primaryroads-polygon.csv"
inputCount = 3000
inputBoundary = Envelope(
    minx=-173.120769,
    maxx=-84.965961,
    miny=30.244859,
    maxy=71.355134
)
rectangleMatchCount = 103
rectangleMatchWithOriginalDuplicatesCount = 103
polygonMatchCount = 472
polygonMatchWithOriginalDuplicatesCount = 562


class TestPointRDD(TestBase):

    def test_constructor(self):
        spatial_rdd = PointRDD(
            self.sc,
            inputLocation,
            offset,
            splitter,
            True,
            numPartitions
        )

        spatial_rdd.analyze()
        assert inputCount == spatial_rdd.approximateTotalCount
        assert inputBoundary == spatial_rdd.boundaryEnvelope
        spatial_rdd.rawSpatialRDD.take(9)[0].getUserData()
        assert spatial_rdd.rawSpatialRDD.take(9)[0].getUserData() == "testattribute0\ttestattribute1\ttestattribute2"
        assert spatial_rdd.rawSpatialRDD.take(9)[2].getUserData() == "testattribute0\ttestattribute1\ttestattribute2"
        assert spatial_rdd.rawSpatialRDD.take(9)[4].getUserData() == "testattribute0\ttestattribute1\ttestattribute2"
        assert spatial_rdd.rawSpatialRDD.take(9)[8].getUserData() == "testattribute0\ttestattribute1\ttestattribute2"

    def test_empty_constructor(self):
        spatial_rdd = PointRDD(
            sparkContext=self.sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=numPartitions,
            newLevel=StorageLevel.MEMORY_ONLY
        )
        spatial_rdd.buildIndex(IndexType.RTREE, False)
        spatial_rdd_copy = PointRDD()
        spatial_rdd_copy.rawJvmSpatialRDD = spatial_rdd.rawJvmSpatialRDD
        spatial_rdd_copy.analyze()

    def test_equal_partitioning(self):
        spatial_rdd = PointRDD(
            sparkContext=self.sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=False,
            partitions=10,
            newLevel=StorageLevel.MEMORY_ONLY
        )
        spatial_rdd.analyze()
        spatial_rdd.spatialPartitioning(GridType.EQUALGRID)

        for envelope in spatial_rdd.grids:
            print("PointRDD spatial partitioning grids: " + str(envelope))
        assert spatial_rdd.countWithoutDuplicates() == spatial_rdd.countWithoutDuplicatesSPRDD()

    def test_hilbert_curve_spatial_partitioning(self):
        spatial_rdd = PointRDD(
            sparkContext=self.sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=False,
            partitions=10,
            newLevel=StorageLevel.MEMORY_ONLY
        )

        spatial_rdd.analyze()
        spatial_rdd.spatialPartitioning(GridType.HILBERT)

        for envelope in spatial_rdd.grids:
            print(envelope)
        assert spatial_rdd.countWithoutDuplicates() == spatial_rdd.countWithoutDuplicatesSPRDD()

    def test_r_tree_spatial_partitioning(self):
        spatial_rdd = PointRDD(
            sparkContext=self.sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=10,
            newLevel=StorageLevel.MEMORY_ONLY
        )
        spatial_rdd.analyze()
        spatial_rdd.spatialPartitioning(GridType.RTREE)

        for envelope in spatial_rdd.grids:
            print(envelope)

        assert spatial_rdd.countWithoutDuplicates() == spatial_rdd.countWithoutDuplicatesSPRDD()

    def test_voronoi_spatial_partitioning(self):
        spatial_rdd = PointRDD(
            sparkContext=self.sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=False,
            partitions=10,
            newLevel=StorageLevel.MEMORY_ONLY
        )

        spatial_rdd.analyze()
        spatial_rdd.spatialPartitioning(GridType.VORONOI)

        for envelope in spatial_rdd.grids:
            print(envelope)

        assert spatial_rdd.countWithoutDuplicates() == spatial_rdd.countWithoutDuplicatesSPRDD()

    def test_build_index_without_set_grid(self):
        spatial_rdd = PointRDD(
            sparkContext=self.sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=numPartitions,
            newLevel=StorageLevel.MEMORY_ONLY
        )
        spatial_rdd.buildIndex(IndexType.RTREE, False)

    def test_build_r_tree_index(self):
        pass
        # TODO Add indexedRDD

    def test_build_quadtree_index(self):
        pass
        # TODO Add indexedRDD
        # spatial_rdd = PointRDD(
        #     sparkContext=sc,
        #     InputLocation=inputLocation,
        #     Offset=offset,
        #     splitter=splitter,
        #     carryInputData=True,
        #     partitions=numPartitions,
        #     newLevel=StorageLevel.MEMORY_ONLY
        #
        # )
        #
        # spatial_rdd.spatialPartitioning(gridType)
        # spatial_rdd.buildIndex(IndexType.QUADTREE, True)
        #
        # spatial_rdd.indexedRDD()
