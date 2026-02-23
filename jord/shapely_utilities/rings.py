import shapely

from shapely import LinearRing
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.ops import linemerge

__all__ = ["ensure_ccw_ring", "ensure_cw_ring", "split_ring"]

from typing import Union


def ensure_ccw_ring(ring: LinearRing) -> LinearRing:
    """

    :param ring:
    :type ring:
    :return:
    :rtype:
    """
    if not ring.is_ccw:
        return LinearRing(list(ring.coords)[::-1])
    return ring


def ensure_cw_ring(ring: LinearRing) -> LinearRing:
    """

    :param ring:
    :type ring:
    :return:
    :rtype:
    """
    if ring.is_ccw:
        return LinearRing(list(ring.coords)[::-1])
    return ring


def split_ring(
    ring: LinearRing,
    split: Union[LinearRing, LineString, MultiLineString, shapely.GeometryCollection],
):
    """Split a linear ring geometry, returns a [Multi]LineString

    See my PostGIS function on scigen named ST_SplitRing
    """
    valid_types = ("MultiLineString", "LineString", "GeometryCollection")
    if not hasattr(ring, "geom_type"):
        raise ValueError("expected ring as a geometry")
    elif not hasattr(split, "geom_type"):
        raise ValueError("expected split as a geometry")
    if ring.geom_type == "LinearRing":
        ring = LineString(ring)
    if ring.geom_type != "LineString":
        raise ValueError(
            "ring is not a LinearRing or LineString, found " + str(ring.geom_type)
        )
    elif not ring.is_closed:
        raise ValueError("ring is not closed")
    elif split.is_empty:
        return ring
    elif not split.intersects(ring):
        # split does not intersect ring
        return ring
    if split.geom_type == "LinearRing":
        split = LineString(split)
    if split.geom_type not in valid_types:
        raise ValueError(
            "split is not a LineString-like or GeometryCollection geometry, "
            "found " + str(split.geom_type)
        )

    intersections = ring.intersection(split)
    if intersections.is_empty:
        # no intersections, returning same ring
        return ring
    elif intersections.geom_type == "Point":
        # Simple case, where there is only one line intersecting the ring
        result = Polygon(ring).difference(split).exterior
        # If it is a coordinate of the ring, then the ring needs to be rotated
        coords = result.coords[:-1]
        found_i = 0
        for i, c in enumerate(coords):
            if Point(c).almost_equals(intersections):
                found_i = i
                break
        if found_i > 0:
            result = Polygon(coords[i:] + coords[:i]).exterior
        if result.interpolate(0).distance(intersections) > 0:
            raise Exception(
                "result start point %s to intersection %s is %s"
                % (result.interpolate(0), intersections, result.distance(intersections))
            )
        elif result.geom_type != "LinearRing":
            raise Exception("result is not a LinearRing, found " + result.geom_type)
        elif not result.is_closed:
            raise Exception("result is not closed")
        return LineString(result)

    difference = ring.difference(split)
    if difference.geom_type != "MultiLineString":
        raise ValueError(
            "expected MultiLineString difference, found " + difference.geom_type
        )

    start_point = ring.interpolate(0)
    if start_point.distance(intersections) == 0:
        # special case: start point is the same as an intersection
        return difference

    # Otherwise the line where the close meets needs to be fused
    fuse = []
    parts = list(difference.geoms)
    for ipart, part in enumerate(parts):
        if part.intersects(start_point):
            fuse.append(ipart)
    if len(fuse) != 2:
        raise ValueError("expected 2 geometries, found " + str(len(fuse)))
    # glue the last to the first
    popped_part = parts.pop(fuse[1])
    parts[fuse[0]] = linemerge([parts[fuse[0]], popped_part])
    return MultiLineString(parts)
