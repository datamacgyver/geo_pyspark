from pyspark import SparkContext

from geo_pyspark.core.SpatialRDD.spatial_rdd import SpatialRDD, JvmCircleRDD
from geo_pyspark.core.SpatialRDD.spatial_rdd_factory import SpatialRDDFactory
from geo_pyspark.utils.meta import MultipleMeta


class CircleRDD(SpatialRDD, metaclass=MultipleMeta):

    def __init__(self, spatialRDD: SpatialRDD, Radius: float):
        """

        :param spatialRDD:
        :param Radius:
        """
        super().__init__(spatialRDD._sc)
        circle_rdd = self._create_jvm_circle_rdd(self._sc)
        self._srdd = circle_rdd(
            spatialRDD._srdd,
            Radius
        )

    def getCenterPointAsSpatialRDD(self) -> 'PointRDD':
        from geo_pyspark.core.SpatialRDD import PointRDD
        srdd = self._srdd.getCenterPointAsSpatialRDD()
        point_rdd = PointRDD()
        point_rdd.set_srdd(srdd)
        return point_rdd

    def getCenterPolygonAsSpatialRDD(self) -> 'PolygonRDD':
        from geo_pyspark.core.SpatialRDD import PolygonRDD
        srdd = self._srdd.getCenterPolygonAsSpatialRDD()
        polygon_rdd = PolygonRDD()
        polygon_rdd.set_srdd(srdd)
        return polygon_rdd

    def getCenterLineStringRDDAsSpatialRDD(self) -> 'LineStringRDD':
        from geo_pyspark.core.SpatialRDD import LineStringRDD
        srdd = self._srdd.getCenterPolygonAsSpatialRDD()
        linestring_rdd = LineStringRDD()
        linestring_rdd.set_srdd(srdd)
        return linestring_rdd

    def getCenterRectangleRDDAsSpatialRDD(self) -> 'RectangleRDD':
        from geo_pyspark.core.SpatialRDD import RectangleRDD
        srdd = self._srdd.getCenterLineStringRDDAsSpatialRDD()
        rectangle_rdd = RectangleRDD()
        rectangle_rdd.set_srdd(srdd)
        return rectangle_rdd

    def _create_jvm_circle_rdd(self, sc: SparkContext):
        spatial_factory = SpatialRDDFactory(sc)
        return spatial_factory.create_circle_rdd()

    def MinimumBoundingRectangle(self):
        raise NotImplementedError("CircleRDD has not MinimumBoundingRectangle method.")
