import os

import pytest
from pyspark.sql import SparkSession
from shapely.geometry import Point

from geo_pyspark.core.SpatialRDD import LineStringRDD
from geo_pyspark.core.enums import IndexType, FileDataSplitter
from geo_pyspark.core.spatialOperator import KNNQuery
from geo_pyspark.register import upload_jars, GeoSparkRegistrator
from tests.utils import tests_path

upload_jars()

spark = SparkSession.\
    builder.\
    master("local").\
    getOrCreate()

GeoSparkRegistrator.\
    registerAll(spark)

sc = spark.sparkContext

input_location = os.path.join(tests_path, "resources/primaryroads-linestring.csv")
offset = 0
splitter = FileDataSplitter.CSV
gridType = "rtree"
indexType = "rtree"


class TestLineStringKnn:

    loop_times = 5
    query_point = Point(-84.01, 34.01)

    def test_spatial_knn_query(self):
        line_string_rdd = LineStringRDD(sc, input_location, splitter, True)
        for i in range(self.loop_times):
            result = KNNQuery.SpatialKnnQuery(line_string_rdd, self.query_point, 5, False)
            assert result.__len__() > -1
            assert result[0].getUserData() is not None

    def test_spatial_knn_query_using_index(self):
        line_string_rdd = LineStringRDD(sc, input_location, splitter, True)
        line_string_rdd.buildIndex(IndexType.RTREE, False)
        for i in range(self.loop_times):
            result = KNNQuery.SpatialKnnQuery(line_string_rdd, self.query_point, 5, False)
            assert result.__len__() > -1
            assert result[0].getUserData() is not None
