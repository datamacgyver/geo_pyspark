from typing import Union

import attr
from shapely.geometry import Point, LinearRing
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import MultiPoint
from shapely.geometry.base import BaseGeometry

from geo_pyspark.sql.enums import ShapeEnum
from geo_pyspark.sql.exceptions import InvalidGeometryException
from geo_pyspark.sql.geometry import GeomEnum
from geo_pyspark.utils.abstract_parser import GeometryParser
from geo_pyspark.utils.binary_parser import BinaryParser, BinaryBuffer


def read_coordinates(parser: BinaryParser, read_scale: int):
    coordinates = []
    for i in range(read_scale):
        coordinates.append((parser.read_double(), parser.read_double()))
    return coordinates


@attr.s
class OffsetsReader:

    @staticmethod
    def read_offsets(parser, num_parts, max_offset):
        offsets = []
        for i in range(num_parts):
            offsets.append(parser.read_int())
        offsets.append(max_offset)
        return offsets


@attr.s
class PointParser(GeometryParser):
    name = "Point"

    @classmethod
    def serialize(cls, obj: Point, binary_buffer: BinaryBuffer):
        if isinstance(obj, Point):
            binary_buffer.put_byte(ShapeEnum.shape.value)
            binary_buffer.put_byte(GeomEnum.point.value)
            binary_buffer.put_double(obj.x)
            binary_buffer.put_double(obj.y)
            binary_buffer.put_byte(-127)
        else:
            raise TypeError(f"Need a {cls.name} instance")
        return binary_buffer.byte_array

    @classmethod
    def deserialize(cls, parser: BinaryParser) -> Point:
        x = parser.read_double()
        y = parser.read_double()
        return Point(x, y)


@attr.s
class UndefinedParser(GeometryParser):
    name = "Undefined"

    @classmethod
    def serialize(cls, obj: BaseGeometry, binary_buffer: BinaryBuffer):
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, parser: BinaryParser) -> BaseGeometry:
        raise NotImplementedError()


@attr.s
class LineStringParser:
    name = "LineString"

    @classmethod
    def serialize(cls, obj: LineString, binary_buffer: BinaryBuffer):
        if isinstance(obj, LineString):
            binary_buffer.put_byte(ShapeEnum.shape.value)
            binary_buffer.put_byte(GeomEnum.polyline.value)
            for _ in range(4):
                binary_buffer.put_double(0.0)
            num_points = obj.coords.__len__()
            binary_buffer.put_int(1)
            binary_buffer.put_int(num_points)
            binary_buffer.put_int(0)

            for coordinate in obj.coords:
                binary_buffer.put_double(Point(coordinate).x)
                binary_buffer.put_double(Point(coordinate).y)
            binary_buffer.put_byte(-127)
        else:
            raise TypeError(f"Need a {cls.name} instance")
        return binary_buffer.byte_array

    @classmethod
    def deserialize(cls, parser: BinaryParser) -> Union[LineString, MultiLineString]:
        raise NotImplemented()


@attr.s
class MultiLineStringParser:
    name = "MultiLineString"

    @classmethod
    def serialize(cls, obj: MultiLineString, binary_buffer: BinaryBuffer):
        if isinstance(obj, MultiLineString):
            binary_buffer.put_byte(ShapeEnum.shape.value)
            binary_buffer.put_byte(GeomEnum.polyline.value)
            for _ in range(4):
                binary_buffer.put_double(0.0)

            num_parts = len(obj.geoms)
            num_points = sum([len(el.coords) for el in obj.geoms])

            binary_buffer.put_int(num_parts)
            binary_buffer.put_int(num_points)

            offset = 0
            for _ in range(num_parts):
                binary_buffer.put_int(offset)
                offset = offset + obj.geoms[_].coords.__len__()

            for geom in obj.geoms:
                for coordinate in geom.coords:
                    binary_buffer.put_double(Point(coordinate).x)
                    binary_buffer.put_double(Point(coordinate).y)

            binary_buffer.put_byte(-127)
        else:
            raise TypeError(f"Need a {cls.name} instance")
        return binary_buffer.byte_array

    @classmethod
    def deserialize(cls, parser: BinaryParser) -> Union[LineString, MultiLineString]:
        raise NotImplemented()


@attr.s
class PolyLineParser(GeometryParser):
    name = "Polyline"

    @classmethod
    def serialize(cls, obj: Union[MultiLineString, LineString], binary_buffer: BinaryBuffer):
        if isinstance(obj, MultiLineString):
            MultiLineStringParser.serialize(obj, binary_buffer)
        elif isinstance(obj, LineString):
            LineStringParser.serialize(obj, binary_buffer)
        else:
            raise TypeError(f"Need a {MultiLineStringParser.name} instance or {LineStringParser.name}")
        return binary_buffer.byte_array

    @classmethod
    def deserialize(cls, parser: BinaryParser) -> Union[LineString, MultiLineString]:
        for _ in range(4):
            parser.read_double()

        num_parts = parser.read_int()
        num_points = parser.read_int()

        offsets = OffsetsReader.read_offsets(parser, num_parts, num_points)
        lines = []
        for i in range(num_parts):
            read_scale = offsets[i + 1] - offsets[i]
            coordinate_sequence = read_coordinates(parser, read_scale)
            lines.append(LineString(coordinate_sequence))

        if num_parts == 1:
            line = lines[0]
        elif num_parts > 1:
            line = MultiLineString(lines)
        else:
            raise InvalidGeometryException("Invalid geometry")

        return line


@attr.s
class PolygonParser(GeometryParser):
    name = "Polygon"

    @classmethod
    def serialize(cls):
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, parser: BinaryParser) -> Union[Polygon, MultiPolygon]:
        for _ in range(4):
            parser.read_double()
        num_rings = parser.read_int()
        num_points = parser.read_int()
        offsets = OffsetsReader.read_offsets(parser, num_parts=num_rings, max_offset=num_points)
        polygons = []
        holes = []
        shells_ccw = False
        shell = None
        for i in range(num_rings):
            read_scale = offsets[i + 1] - offsets[i]
            cs_ring = read_coordinates(parser, read_scale)
            if (len(cs_ring)) < 3:
                continue

            ring = LinearRing(cs_ring)

            if shell is None:
                shell = ring
                shells_ccw = LinearRing(cs_ring).is_ccw
            elif LinearRing(cs_ring).is_ccw != shells_ccw:
                holes.append(ring)
            else:
                if shell is not None:
                    polygon = Polygon(shell, holes)
                    polygons.append(polygon)
                shell = ring
                holes = []

        if shell is not None:
            geometry = Polygon(shell, holes)
            polygons.append(geometry)

        if polygons.__len__() == 1:
            return polygons[0]

        return MultiPolygon(polygons)


@attr.s
class MultiPointParser(GeometryParser):
    name = "MultiPoint"

    @classmethod
    def serialize(cls, obj: MultiPoint, binary_buffer: BinaryBuffer):
        if isinstance(obj, MultiPoint):
            binary_buffer.put_byte(ShapeEnum.shape.value)
            binary_buffer.put_byte(GeomEnum.multipoint.value)
            for _ in range(4):
                binary_buffer.put_double(0.0)
            binary_buffer.put_int(len(obj.geoms))
            for point in obj.geoms:
                binary_buffer.put_double(point.x)
                binary_buffer.put_double(point.y)
            binary_buffer.put_byte(-127)
        else:
            raise TypeError(f"Need a {cls.name} instance")
        return binary_buffer.byte_array

    @classmethod
    def deserialize(cls, parser: BinaryParser) -> MultiPoint:
        for _ in range(4):
            parser.read_double()
        number_of_points = parser.read_int()

        coordinates = read_coordinates(parser, number_of_points)

        return MultiPoint(coordinates)
