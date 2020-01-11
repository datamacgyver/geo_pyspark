import pytest
import os

from pyspark import StorageLevel

from geo_pyspark.core.SpatialRDD import RectangleRDD
from geo_pyspark.core.SpatialRDD.spatial_rdd import SpatialRDD
from geo_pyspark.core.enums import FileDataSplitter, GridType
from geo_pyspark.core.geom_types import Envelope
from geo_pyspark.core.spatialOperator import JoinQuery
from tests.test_base import TestBase
from tests.utils import tests_path


inputLocation = os.path.join(tests_path, "resources/zcta510-small.csv")
queryWindowSet = os.path.join(tests_path, "resources/zcta510-small.csv")
offset = 0
splitter = FileDataSplitter.CSV
gridType = "rtree"
indexType = "rtree"
numPartitions = 11
distance = 0.001
queryPolygonSet = os.path.join(tests_path, "resources/primaryroads-polygon.csv")
inputCount = 3000
inputBoundary = Envelope(-171.090042, 145.830505, -14.373765, 49.00127)
matchCount = 17599
matchWithOriginalDuplicatesCount = 17738


class TestRectangleJoin(TestBase):

    def partition_rdds(self, query_rdd: SpatialRDD, spatial_rdd: SpatialRDD, index: GridType):
        spatial_rdd.spatialPartitioning(index)
        query_rdd.spatialPartitioning(spatial_rdd.getPartitioner)

    def create_rectangle_rdd(self):
        rdd = RectangleRDD(self.sc, inputLocation, splitter, True, numPartitions)
        rdd.analyze()
        return RectangleRDD(rdd.rawJvmSpatialRDD, StorageLevel.MEMORY_ONLY)

    def test_nested_loop(self):
        """TODO add sanity check"""
        query_rdd = self.create_rectangle_rdd()
        spatial_rdd = self.create_rectangle_rdd()

        for index in GridType:
            self.partition_rdds(query_rdd, spatial_rdd, index)

            result = JoinQuery.SpatialJoinQuery(
                spatial_rdd, query_rdd, False, True).collect()

            count = 0
            for el in result:
                count += el[1].__len__()
            assert matchCount == count

        # sanityCheckJoinResults(result);
        # assertEquals(expectedMatchCount, countJoinResults(result));
