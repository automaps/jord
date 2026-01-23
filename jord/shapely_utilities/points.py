import numpy
import shapely
import shapely.geometry
from shapely.geometry import LineString, MultiPoint, Point
from typing import Generator, Iterable, List, Optional, Sequence, Tuple, Union
from warg import Number

__all__ = [
    "unique_line_points",
    "nearest_neighbor_within",
    "azimuth",
    "shift_point",
    "closest_object",
    "off_center_point_inside_polygon",
]


def unique_line_points(lines: Sequence[LineString]) -> List[Point]:
    """


    :param lines:
    :return: Return list of unique vertices from list of LineStrings.
    :rtype: List[Point]
    """

    vertices = []

    for line in lines:
        vertices.extend(list(line.coords))

    return [Point(p) for p in set(vertices)]


def nearest_neighbor_within(
    others: Sequence, point: shapely.Point, max_distance: Number
) -> Optional[Point]:
    """Find the nearest point among others up to a maximum distance.


    :param others: a list of Points or a MultiPoint
    :param point: a Point
    :param max_distance: maximum distance to search for the nearest neighbor

    :return: A shapely Point if one is within max_distance, None otherwise
    :rtype: Optional[Point]
    """
    search_region = point.buffer(max_distance)
    interesting_points = search_region.intersection(MultiPoint(others))

    if not interesting_points:
        closest_point = None
    elif isinstance(interesting_points, Point):
        closest_point = interesting_points
    else:
        if isinstance(interesting_points, MultiPoint):
            interesting_points = list(interesting_points.geoms)

        distances = [
            point.distance(ip) for ip in interesting_points if point.distance(ip) > 0
        ]
        closest_point = interesting_points[distances.index(min(distances))]

    return closest_point


def closest_object(
    geometries: Iterable[shapely.geometry.base.BaseGeometry], point: Point
) -> Tuple[shapely.geometry.base.BaseGeometry, float, int]:
    """
    Find the nearest geometry among a list, measured from fixed point.

    :param geometries:  a iterable of shapely geometry objects
    :param point: a shapely Point
    :return: Tuple (geom, min_dist, min_index) of the geometry with minimum distance
        to point, its distance min_dist and the list index of geom, so that
        geom = geometries[min_index].
    """
    if isinstance(geometries, Generator):
        geometries = list(geometries)

    min_dist, min_index = min(
        (point.distance(geom), k) for (k, geom) in enumerate(geometries)
    )

    return geometries[min_index], min_dist, min_index


def shift_point(
    c1: Union[Point, Tuple[Number, Number]],
    c2: Union[Point, Tuple[Number, Number]],
    offset: float,
) -> Point:
    """

    shift points with offset in orientation of line c1->c2

    :param c1:
    :param c2:
    :param offset:
    :return:
    """

    if isinstance(c1, Point):
        x1, y1 = c1.coords[0]
    else:
        x1, y1 = c1

    if isinstance(c2, Point):
        x2, y2 = c2.coords[0]
    else:
        x2, y2 = c2

    if ((x1 - x2) == 0) and ((y1 - y2) == 0):  # zero length line
        x_new, y_new = x1, y1
    else:
        rel_length = numpy.minimum(
            offset / numpy.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2), 1
        )
        x_new = x1 + (x2 - x1) * rel_length
        y_new = y1 + (y2 - y1) * rel_length

    return Point(x_new, y_new)


def azimuth(point1: Point, point2: Point) -> float:
    """
    The clockwise angle from North to line of two points

    :param point1:
    :type point1: Point
    :param point2:
    :type point2: Point
    :return: angle
    :rtype: float
    """

    angle = numpy.arctan2(point2.x - point1.x, point2.y - point1.y)
    # Gets the angle between the first and last coordinate of a linestring

    return (
        numpy.degrees(angle) if angle >= 0 else numpy.degrees(angle) + 360
    ) % 180  # Modulo is used on the angle to produce a result between 0 and 180 degrees


def off_center_point_inside_polygon(polygon: shapely.Polygon) -> shapely.Point:

    rep_point = polygon.representative_point()
    for x, y in zip(*polygon.exterior.coords.xy):

        line = shapely.LineString([shapely.Point(x, y), rep_point])

        point = line.interpolate(0.5, normalized=True)
        if point.within(polygon):
            return point

    return rep_point


if __name__ == "__main__":
    print(azimuth(Point(0, 0), Point(1, 1)))
    print(azimuth(Point(1, 1), Point(0, 0)))

    print(shift_point(Point(1, 1), Point(0, 0), 1))
    print(shift_point(Point(1, 1), Point(0, 0), 2))
    print(shift_point(Point(1, 1), Point(0, 0), 3))

    print(shift_point(Point(0, 0), Point(1, 1), 1))
    print(shift_point(Point(0, 0), Point(1, 1), 0))
