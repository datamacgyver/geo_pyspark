from typing import Optional

import attr

from geo_pyspark.core.SpatialRDD.spatial_rdd import SpatialRDD
from geo_pyspark.core.SpatialRDD.spatial_rdd_factory import SpatialRDDFactory


@attr.s
class PointRDD(SpatialRDD):
    Offset = attr.ib(default=None, type=Optional[int])

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    def srdd_from_attributes(self):
        Spatial = SpatialRDDFactory(self.sparkContext).create_point_rdd()

        if self.InputLocation is not None:
            point_rdd = Spatial(
                self._jsc,
                self.InputLocation,
                self.Offset,
                self.splitter,
                self.carryInputData
            )
        else:
            point_rdd = Spatial()

        return point_rdd