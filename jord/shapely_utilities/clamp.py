__author__ = "heider"
__doc__ = r"""

           Created on 1/23/23
           """

__all__ = [
    "split_line_string",
    "combine_line_string",
    "extend_segment",
    "fix_starting_point",
    "adjust_line_end",
    "ensure_list_of_geometries",
]

from collections import deque
from typing import List, Sequence, Union

import shapely.geometry
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.geometry.base import BaseMultipartGeometry


def split_line_string(line_string: LineString) -> Sequence[LineString]:
    """
    Break a LineString

    :param line_string:
    :return:
    """
    for start, end in zip(line_string.coords[:-1], line_string.coords[1:]):
        yield LineString((start, end))


def combine_line_string(segments: Sequence[LineString]) -> LineString:
    """

    :param segments:
    :return:
    :rtype: LineString
    """
    coords = [segments[0].coords[0]]

    for segment in segments:
        coords.extend(segment.coords[1:])

    return LineString(coords)


def extend_segment(line_string: LineString) -> LineString:
    """
    Move a line segment's start and end away from each other to ensure intersections

    :param line_string:
    :return:
    """
    p0 = line_string.coords[0]
    p1 = line_string.coords[1]

    difference = (p0[0] - p1[0], p0[1] - p1[1])
    length = (difference[0] ** 2 + difference[1] ** 2) ** 0.5
    direction = (difference[0] / length, difference[1] / length)
    offset = (direction[0] * 1e-12, direction[1] * 1e-12)

    new_p0 = (p0[0] + offset[0], p0[1] + offset[1])
    new_p1 = (p1[0] - offset[0], p1[1] - offset[1])

    return LineString((new_p0, new_p1))


def fix_starting_point(polygon_pieces: Sequence[Polygon]) -> Sequence[Polygon]:
    """
    Reconnect the starting point of a polygon's pieces.
    When splitting a polygon with two lines, we want to get two pieces.
    However, that's not quite how Shapely works.  The outline of the
    polygon is a LinearRing that starts and ends at the same place, but
    Shapely still knows where that starting point is and splits there
    too.
    We don't want that third piece, so we'll reconnect the segments that
    touch the starting point.


    :param polygon_pieces:
    :return:
    """

    if len(polygon_pieces) == 3:
        # Fortunately, Shapely keeps the starting point of the LinearRing
        # as the starting point of the first segment.  That means it's also
        # the ending point of the last segment.  Reconnecting is super simple:
        return [
            polygon_pieces[1],
            LineString(polygon_pieces[2].coords[:] + polygon_pieces[0].coords[1:]),
        ]
    else:
        return polygon_pieces  # We probably cut exactly at the starting point.


def adjust_line_end(
    line: LineString, end: shapely.geometry.base.BaseGeometry
) -> LineString:
    """
    Reverse line if necessary to ensure that it ends near end.

    :param line:
    :param end:
    :return:
    """

    line_start = Point(*line.coords[0])
    line_end = Point(*line.coords[-1])

    if line_end.distance(end) < line_start.distance(end):
        return line
    else:
        return LineString(line.coords[::-1])


def ensure_list_of_geometries(
    thing: Union[shapely.geometry.base.BaseGeometry, BaseMultipartGeometry],
) -> List[shapely.geometry.base.BaseGeometry]:
    """

    :param thing:
    :return:
    """
    if False:
        try:  # Not MultiGeometry base class for shapely
            return list(thing.geoms)
        except AttributeError:
            return [thing]
    if isinstance(thing, BaseMultipartGeometry):
        return list(thing.geoms)
    return [thing]


def clamp_linestring_to_polygon(
    line_string: LineString, polygon: Polygon
) -> LineString:
    """

    :param line_string:
    :param polygon:
    :return:
    """
    segments = deque(split_line_string(line_string))
    result = []
    exiting_segment = None
    was_inside = False

    # contains() checks can fail without this.
    buffered_polygon = polygon.buffer(1e-9)

    while segments:
        current_segment = segments.popleft()
        pieces = ensure_list_of_geometries(current_segment.difference(polygon.exterior))

        if pieces[0].coords[0] != current_segment.coords[0]:
            # The initial part of this line segment coincided with part of the
            # polygon border and was removed.

            if was_inside:
                # If we were already inside, we include this border segment.
                result.append(
                    LineString((current_segment.coords[0], pieces[0].coords[0]))
                )

            # Push the rest back on to be processed later.
            # Note that extendleft() reverses its arguments, so we have to compensate.
            segments.extendleft(reversed(pieces))

        elif len(pieces) > 1 and pieces[0].coords[-1] != pieces[1].coords[0]:
            # There's an initial segment, then a portion that coincided with
            # part of the polygon border.  Break this segment apart and re-process.

            segments.appendleft(
                LineString((pieces[0].coords[1], current_segment.coords[-1]))
            )
            segments.appendleft(pieces[0])

        elif len(pieces) == 1:
            # This segment is either all inside or all outside the polygon.

            is_inside = buffered_polygon.contains(current_segment)
            if is_inside and not was_inside:
                # We've crossed from outside to inside exactly at the starting
                # point of this line segment.

                if exiting_segment:
                    # Earlier we crossed out from the inside, now we're
                    # crossing back in.  Find the shortest path along
                    # the border that gets from the exit point to the
                    # entry point and add it to the result.

                    entering_segment = extend_segment(current_segment)

                    difference = polygon.boundary.difference(
                        MultiLineString((exiting_segment, entering_segment))
                    )

                    polygon_pieces = ensure_list_of_geometries(difference)
                    polygon_pieces = fix_starting_point(polygon_pieces)

                    if len(polygon_pieces) == 1:
                        # We re-entered exactly where we left, so we
                        # don't include any of the border.
                        pass
                    else:
                        shorter = min(polygon_pieces, key=lambda piece: piece.length)

                        # We don't know which direction the polygon border
                        # piece should be.  adjust_line_end() will figure
                        # that out.
                        result.append(
                            adjust_line_end(shorter, Point(*current_segment.coords[0]))
                        )

                    exiting_segment = None

                result.append(current_segment)
            elif was_inside and not is_inside:
                # Like the previous case, but we've crossed to outside.  Store
                # an extended version of this segment as the exit point.
                exiting_segment = extend_segment(current_segment)
            elif is_inside:
                result.append(current_segment)

            was_inside = is_inside

        elif len(pieces) > 1:
            # This segment crosses the border, or touches the border at a single point,
            # or maybe crosses multiple times, etc.  Split the first portion off and
            # push it and the rest to be reprocessed in the following iterations.

            segments.appendleft(
                LineString((pieces[0].coords[1], current_segment.coords[-1]))
            )
            segments.appendleft(pieces[0])

    return combine_line_string(result)


if __name__ == "__main__":

    def _main():
        from draugr.numpy_utilities import HilbertCurve
        from geopandas import GeoSeries
        from matplotlib import pyplot

        hilbert_curve = HilbertCurve(5, 2)
        hc = LineString(hilbert_curve.points_from_distances(range(1023)))
        circle = Point(15, 15).buffer(15)
        clamped = clamp_linestring_to_polygon(hc, circle)

        gs = GeoSeries([clamped])
        gs.plot()
        pyplot.show()

    _main()
