import attr

from geo_pyspark.core.enums import IndexType
from geo_pyspark.core.enums.join_build_side import JoinBuildSide
from geo_pyspark.core.jvm.abstract import JvmObject


@attr.s
class JoinParams(JvmObject):
    useIndex = attr.ib(type=bool, default=True)
    indexType = attr.ib(type=str, default=IndexType.RTREE)
    joinBuildSide = attr.ib(type=str, default=JoinBuildSide.LEFT)

    def create_jvm_instance(self):
        return self.jvm_reference(self.useIndex, self.indexType, self.joinBuildSide)

    @property
    def jvm_reference(self):
        return self.jvm.org.imbruced.geo_pyspark.JoinParams.createJoinParams