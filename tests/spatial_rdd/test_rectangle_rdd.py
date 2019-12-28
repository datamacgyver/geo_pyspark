import pytest
from pyspark import StorageLevel
from pyspark.sql import SparkSession

from geo_pyspark.core.SpatialRDD import RectangleRDD
from geo_pyspark.core.enums import IndexType, GridType
from geo_pyspark.core.geom_types import Envelope
from geo_pyspark.register import upload_jars, GeoSparkRegistrator

upload_jars()

spark = SparkSession.\
    builder.\
    master("local").\
    getOrCreate()

GeoSparkRegistrator.\
    registerAll(spark)

sc = spark.sparkContext


inputLocation = "resources/zcta510-small.csv"
queryWindowSet = "resources/zcta510-small.csv"
offset = 0
splitter = "csv"
gridType = "rtree"
indexType = "rtree"
numPartitions = 11
distance = 0.001
queryPolygonSet = "resources/primaryroads-polygon.csv"
inputCount = 3000
inputBoundary = Envelope(minx=-171.090042, maxx=145.830505, miny=-14.373765, maxy=49.00127)
matchCount = 17599
matchWithOriginalDuplicatesCount = 17738


class TestRectangleRDD:

    def test_constructor(self):
        spatial_rdd = RectangleRDD(
            sparkContext=sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=numPartitions,
            newLevel=StorageLevel.MEMORY_ONLY
        )

        spatial_rdd.analyze()

        assert inputCount == spatial_rdd.approximateTotalCount
        assert inputBoundary == spatial_rdd.boundaryEnvelope

    def test_empty_constructor(self):
        spatial_rdd = RectangleRDD(
            sparkContext=sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=numPartitions,
            newLevel=StorageLevel.MEMORY_ONLY
        )

        spatial_rdd.analyze()
        spatial_rdd.buildIndex(IndexType.RTREE, False)

        spatial_rdd_copy = RectangleRDD()
        spatial_rdd_copy.rawSpatialRDD = spatial_rdd
        spatial_rdd_copy.analyze()

    def test_hilbert_curve_spatial_partitioning(self):
        spatial_rdd = RectangleRDD(
            sparkContext=sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=10,
            newLevel=StorageLevel.MEMORY_ONLY
        )
        spatial_rdd.analyze()

        spatial_rdd.spatialPartitioning(GridType.HILBERT)

        for envelope in spatial_rdd.grids:
            print(envelope)

        assert spatial_rdd.countWithoutDuplicates() == spatial_rdd.countWithoutDuplicatesSPRDD()

    def test_rtree_spatial_partitioning(self):
        spatial_rdd = RectangleRDD(
            sparkContext=sc,
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
            print(spatial_rdd)

        assert spatial_rdd.countWithoutDuplicates() == spatial_rdd.countWithoutDuplicatesSPRDD()

    def test_voronoi_spatial_partitioning(self):
        spatial_rdd = RectangleRDD(
            sparkContext=sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=10,
            newLevel=StorageLevel.MEMORY_ONLY
        )
        spatial_rdd.analyze()
        spatial_rdd.spatialPartitioning(GridType.VORONOI)
        for envelope in spatial_rdd.grids:
            print(envelope)

        assert spatial_rdd.countWithoutDuplicates() == spatial_rdd.countWithoutDuplicatesSPRDD()

    def test_build_index_without_set_grid(self):
        spatial_rdd = RectangleRDD(
            sparkContext=sc,
            InputLocation=inputLocation,
            Offset=offset,
            splitter=splitter,
            carryInputData=True,
            partitions=numPartitions
        )

        spatial_rdd.analyze()

        spatial_rdd.buildIndex(IndexType.RTREE, False)

    def test_build_rtree_index(self):
        pass
        # TODO write this test

    def test_build_quad_tree_index(self):
        pass
        # TODO write this test