import os

import pytest
from pyspark.sql import SparkSession

from geo_pyspark.core.formatMapper.geo_json_reader import GeoJsonReader
from geo_pyspark.register import GeoSparkRegistrator, upload_jars
from tests.utils import tests_path

upload_jars()


spark = SparkSession.\
    builder.\
    master("local").\
    getOrCreate()

GeoSparkRegistrator.\
    registerAll(spark)

sc = spark.sparkContext

geo_json_contains_id = os.path.join(tests_path, "resources/testContainsId.json")
geo_json_geom_with_feature_property = os.path.join(tests_path, "resources/testPolygon.json")
geo_json_geom_without_feature_property = os.path.join(tests_path, "resources/testpolygon-no-property.json")
geo_json_with_invalid_geometries = os.path.join(tests_path, "resources/testInvalidPolygon.json")
geo_json_with_invalid_geom_with_feature_property = os.path.join(tests_path, "resources/invalidSyntaxGeometriesJson.json")


class TestGeoJsonReader:

    def test_read_to_geometry_rdd(self):
        geo_json_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_geom_with_feature_property
        )

        assert geo_json_rdd.rawSpatialRDD.count() == 1001

        geo_json_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_geom_without_feature_property
        )

        assert geo_json_rdd.rawSpatialRDD.count() == 10

    def test_read_to_valid_geometry_rdd(self):
        geo_json_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_geom_with_feature_property,
            allowInvalidGeometries=True,
            skipSyntaticallyInvalidGeometries=False
        )

        assert geo_json_rdd.rawSpatialRDD.count() == 1001

        geo_json_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_geom_without_feature_property,
            allowInvalidGeometries=True,
            skipSyntaticallyInvalidGeometries=False
        )

        assert geo_json_rdd.rawSpatialRDD.count() == 10

        geo_json_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_with_invalid_geometries,
            allowInvalidGeometries=False,
            skipSyntaticallyInvalidGeometries=False
        )

        assert geo_json_rdd.rawSpatialRDD.count() == 2

        geo_json_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_with_invalid_geometries
        )
        assert geo_json_rdd.rawSpatialRDD.count() == 3

    def test_read_to_include_id_rdd(self):
        geo_json_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_contains_id,
            allowInvalidGeometries=True,
            skipSyntaticallyInvalidGeometries=False
        )

        assert geo_json_rdd.rawSpatialRDD.count() == 1
        assert geo_json_rdd.fieldNames.__len__() == 3

    def test_read_to_geometry_rdd_invalid_syntax(self):
        geojson_rdd = GeoJsonReader.readToGeometryRDD(
            sparkContext=sc,
            inputPath=geo_json_with_invalid_geom_with_feature_property,
            allowInvalidGeometries=False,
            skipSyntaticallyInvalidGeometries=True
        )
        assert geojson_rdd.rawSpatialRDD.count() == 1
