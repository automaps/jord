__author__ = "heider"
__doc__ = r"""

           Created on 1/23/23
           """

__all__ = [
    "to_lines",
    "to_single_line",
    "explode_line",
    "explode_lines",
    "strip_multiline_dangles",
    "strip_line_dangles",
    "azimuth",
    "linestring_azimuth",
    "linemerge",
    "join_endings",
    "find_isolated_endpoints",
    "snappy_endings",
    "segments",
    "extend_line",
    "extend_lines",
    "add_coordinate",
    "perpendicular_line",
    "cap_lines",
    "ExtensionDirectionEnum",
    "intersecting_lines_idx",
    "intersecting_lines",
    "one_linestring_per_intersection",
    "are_incident",
    "prune_short_lines",
    "bend_towards",
    "remove_redundant_nodes",
    "split_line",
    "internal_points",
    "snap_endings_to_points",
]

import collections
import logging
import numpy
import shapely
import shapely.geometry
from enum import Enum
from shapely.geometry import (
    LineString,
    LinearRing,
    MultiLineString,
    MultiPoint,
    Point,
    box,
)
from typing import Iterable, List, Sequence, Tuple, Union

# from sorcery import assigned_names
from warg import Number, pairs

from .points import (
    azimuth,
    nearest_neighbor_within,
    shift_point,
    unique_line_points,
)
from .projection import nearest_geometry

EPSILON = 1e-6


def to_single_line(
    s: Union[LineString, MultiLineString, Iterable[LineString]],
) -> LineString:
    """
    assume that lines are ordered, NOTE closes of gaps!

    :param s:
    :type s: Union[LineString, MultiLineString]
    :return:
    :rtype: LineString
    """
    if isinstance(s, MultiLineString):
        out_coords = [
            list(i.coords) for i in s.geoms
        ]  # Put the subline coordinates into a list of sublists

        return LineString(
            [i for sublist in out_coords for i in sublist]
        )  # Flatten the list of sublists and use it to make a new line

    elif isinstance(s, LineString):
        return s
    elif isinstance(s, Iterable):
        return to_single_line(MultiLineString(s))
    else:
        raise NotImplementedError


def to_lines(
    geoms: Union[
        Sequence[shapely.geometry.base.BaseGeometry], LineString, MultiLineString
    ],
) -> List[LineString]:
    """
    Converts Shapely geoms in to Shapely LineString

    :param geoms:
    :type geoms: Sequence[shapely.geometry.base.BaseGeometry]
    :return:
    :rtype: List[LineString]
    """

    lines = []
    if isinstance(geoms, shapely.GeometryCollection):
        geoms = geoms.geoms

    if isinstance(geoms, Iterable):
        for g in geoms:
            if isinstance(g, LineString):
                lines.append(g)
            elif isinstance(g, MultiLineString):
                lines.extend(g.geoms)
            elif isinstance(g, shapely.geometry.base.BaseGeometry):
                boundary = g.boundary
                if boundary:
                    if isinstance(boundary, MultiLineString):
                        lines.extend(to_lines(boundary.geoms))
                    elif isinstance(boundary, MultiPoint):
                        lines.append(LineString(coordinates=boundary.geoms))
                    else:
                        lines.append(boundary)
                elif g.is_empty:
                    ...
                elif isinstance(g, Point):
                    ...
                else:
                    raise NotImplementedError(f"{g, type(g)}")
            else:
                raise NotImplementedError(f"{g, type(g)}")
    elif isinstance(geoms, MultiLineString):
        lines = geoms.geoms
    elif isinstance(geoms, LineString):
        lines = [geoms]
    elif isinstance(geoms, shapely.geometry.base.BaseGeometry):
        boundary = geoms.boundary
        if boundary:
            if isinstance(boundary, MultiLineString):
                lines.extend(to_lines(boundary.geoms))
            elif isinstance(boundary, MultiPoint):
                lines.append(LineString(coordinates=boundary.geoms))
            else:
                lines.append(boundary)
        elif geoms.is_empty:
            ...
        elif isinstance(geoms, Point):
            ...
        else:
            raise NotImplementedError(f"{geoms, type(geoms)}")
    else:
        raise NotImplementedError(f"{geoms, type(geoms)}")

    if not isinstance(lines, List):
        lines = list(lines)

    return lines


def strip_line_dangles(
    line: LineString, dangle_length_threshold: float = 0.1, iterations: int = 3
) -> LineString:
    """

    :param line:
    :type line: LineString
    :param dangle_length_threshold:
    :type dangle_length_threshold: float
    :param iterations:
    :type iterations: int
    :return: The LineString without dangles shorter than the dangle_length_threshold
    :rtype: LineString
    """

    working_line = line
    for ith_ in range(iterations):
        working_segments = []

        segments = explode_line(working_line)

        if len(segments) > 2:
            start, *rest, end = segments

            if start.length > dangle_length_threshold:
                working_segments.append(start)

            working_segments.extend(rest)

            if end.length > dangle_length_threshold:
                working_segments.append(end)

        elif len(segments) < 2:
            segment = segments[0]

            if segment.length > dangle_length_threshold:
                working_segments.append(segment)

        else:
            s1, s2 = segments

            if s1.length > dangle_length_threshold:
                working_segments.append(s1)

            if s2.length > dangle_length_threshold:
                working_segments.append(s2)

        working_line = LineString(working_segments)

    return working_line


def line_endpoints(lines: Union[List[LineString], MultiLineString]) -> MultiPoint:
    """

    :param lines:
    :type: Union[List[LineString], MultiLineString]
    :return: Returns a MultiPoint of terminal points from list of LineStrings.
    :rtype: MultiPoint
    """

    all_points = []
    if isinstance(lines, MultiLineString):
        lines = lines.geoms

    for line in lines:
        for i in [0, -1]:  # start and end point
            all_points.append(line.coords[i])

    endpoints = {
        item for item, count in collections.Counter(all_points).items() if count < 2
    }  # Remove duplicates

    return shapely.MultiPoint([Point(p) for p in endpoints])


def internal_points(
    lines: Union[List[LineString], MultiLineString],
) -> shapely.MultiPoint:
    """

    :param lines:
    :type: Union[List[LineString], MultiLineString]
    :return: Returns a MultiPoint of terminal points from list of LineStrings.
    :rtype: MultiPoint
    """

    all_points = []
    if isinstance(lines, MultiLineString):
        lines = lines.geoms

    for line in lines:
        for i in [0, -1]:  # start and end point
            all_points.append(line.coords[i])

    internal_points = {
        item for item, count in collections.Counter(all_points).items() if count >= 2
    }  # Remove duplicates

    return shapely.MultiPoint([Point(p) for p in internal_points])


def strip_multiline_dangles(
    multilinestring: MultiLineString,
    dangle_length_threshold: float = 0.1,
    iterations: int = 3,
) -> MultiLineString:
    """

    :param multilinestring:
    :type multilinestring: MultiLineString
    :param dangle_length_threshold:
    :type dangle_length_threshold: float
    :param iterations:
    :type iterations: int
    :return:
    :rtype: MultiLineString
    """
    working_multi = multilinestring
    for ith_ in range(iterations):
        endpoints = line_endpoints(working_multi)
        working_segments = []
        for linestring in working_multi.geoms:
            segments = explode_line(linestring)
            if len(segments) > 2:
                start, *rest, end = segments
                if start.intersects(endpoints):
                    if start.length > dangle_length_threshold:
                        working_segments.append(start)
                else:
                    working_segments.append(start)

                working_segments.extend(rest)

                if end.intersects(endpoints):
                    if end.length > dangle_length_threshold:
                        working_segments.append(end)
                else:
                    working_segments.append(end)
            elif len(segments) < 2:
                segment = segments[0]
                if segment.intersects(endpoints):
                    if segment.length > dangle_length_threshold:
                        working_segments.append(segment)
                else:
                    working_segments.append(segment)
            else:
                s1, s2 = segments
                if s1.intersects(endpoints):
                    if s1.length > dangle_length_threshold:
                        working_segments.append(s1)
                else:
                    working_segments.append(s1)

                if s2.intersects(endpoints):
                    if s2.length > dangle_length_threshold:
                        working_segments.append(s2)
                else:
                    working_segments.append(s2)

        working_multi = MultiLineString(working_segments)

    return working_multi


def explode_line(line: Union[LineString, MultiLineString]) -> List[LineString]:
    """

    :param line:
    :return:
    """

    if isinstance(line, MultiLineString):
        out = []
        for ls in line.geoms:
            out.extend(explode_line(ls))
        return out

    out = []
    for pt1, pt2 in zip(
        line.coords, line.coords[1:]
    ):  # iterate from first cord, iterate from second coords to get
        # endpoints of each segment
        out.append(LineString([pt1, pt2]))
    return out


def explode_lines(
    lines: Iterable[Union[LineString, MultiLineString]],
) -> list[LineString]:
    """
    :param lines: List of LineStrings or MultiLineStrings to be exploded
    :return: Exploded LineStrings
    """
    out = []
    for ls in lines:
        out.extend(explode_line(ls))
    return out


def find_isolated_endpoints(
    lines: Union[List[LineString], MultiLineString],
) -> List[Point]:
    """
    Find endpoints of lines that don't touch another line.

    :param lines: A list of LineStrings or a MultiLineString
    :return: A list of line end Points that don't touch any other line of lines
    """

    isolated_endpoints = []

    if not isinstance(lines, MultiLineString):
        lines = MultiLineString(to_lines(lines))

    for i, line in enumerate(lines.geoms):
        other_lines = lines.geoms[:i] | lines.geoms[i + 1 :]

        for q in [0, -1]:
            endpoint = Point(line.coords[q])

            if endpoint.touches(other_lines):
                continue
            else:
                isolated_endpoints.append(endpoint)

    return isolated_endpoints


def join_endings(
    lines: Union[
        LineString, Iterable[LineString], MultiLineString, Iterable[MultiLineString]
    ],
    only_inter_joins: bool = True,  # Only joining inter MultiLineString ending (NOT WITH ITSELF)!
    max_distance: float = 0,
) -> Sequence[Union[LineString, MultiLineString]]:
    """
    Snap endpoints of lines together if they are at most max_length apart.


    :param lines: A list of LineStrings or a MultiLineString
    :param max_distance: maximum distance two endpoints may be joined together
    :return:
    :rtype: Sequence[Union[LineString, MultiLineString]]
    """

    # lines_components = explode_lines(lines)
    # lines_components = to_lines(lines)
    lines_components = lines

    unique_endpoints = unique_line_points(lines_components)

    isolated_endpoints = find_isolated_endpoints(lines_components)

    it = isolated_endpoints

    for endpoint in it:
        if max_distance > 0:
            target = nearest_neighbor_within(unique_endpoints, endpoint, max_distance)
        else:
            target, *_ = nearest_geometry(unique_endpoints, endpoint)

        if not target:  # do nothing if no target point to join to was found
            continue

        lines_components.append(LineString([endpoint, target]))

    lines_components = [
        s for s in lines_components if s.length > 0
    ]  # post-processing: remove any resulting lines of length 0

    return lines_components


def snappy_endings(
    lines: Union[Iterable[LineString], MultiLineString], max_distance: float
) -> Sequence[Union[LineString, MultiLineString]]:
    """
    Snap endpoints of lines together if they are at most max_length apart.


    :param lines: A list of LineStrings or a MultiLineString
    :param max_distance: maximum distance two endpoints may be joined together
    :return:
    :rtype: Sequence[Union[LineString, MultiLineString]]
    """

    # initialize snapped lines with list of original lines
    # snapping points is a MultiPoint object of all vertices
    snapped_lines = to_lines(lines)

    snapping_points = unique_line_points(snapped_lines)

    # isolated endpoints are going to snap to the closest vertex
    isolated_endpoints = find_isolated_endpoints(snapped_lines)

    # only move isolated endpoints, one by one
    for endpoint in isolated_endpoints:
        # find all vertices within a radius of max_distance as possible
        target = nearest_neighbor_within(snapping_points, endpoint, max_distance)

        if not target:  # do nothing if no target point to snap to is found
            continue

        for i, snapped_line in enumerate(
            snapped_lines
        ):  # find the LineString to modify within snapped_lines and update it
            if endpoint.touches(snapped_line):
                snapped_lines[i] = bend_towards(snapped_line, where=endpoint, to=target)
                break

        for i, snapping_point in enumerate(snapping_points):
            # also update the corresponding snapping_points
            if endpoint.equals(snapping_point):
                snapping_points[i] = target
                break

    # post-processing: remove any resulting lines of length 0
    snapped_lines = [s for s in snapped_lines if s.length > 0]

    return snapped_lines


def snap_endings_to_points(
    lines: Union[Iterable[LineString], MultiLineString],
    snapping_points: Sequence[Point],
    max_distance: float,
) -> Sequence[Union[LineString, MultiLineString]]:
    """
    Snap endpoints of lines together if they are at most max_length apart.


    :param snapping_points:
    :param lines: A list of LineStrings or a MultiLineString
    :param max_distance: maximum distance two endpoints may be joined together
    :return:
    :rtype: Sequence[Union[LineString, MultiLineString]]
    """

    # initialize snapped lines with list of original lines
    # snapping points is a MultiPoint object of all vertices
    snapped_lines = to_lines(lines)

    if isinstance(snapping_points, MultiPoint):
        snapping_points = list(snapping_points.geoms)

    # isolated endpoints are going to snap to the closest vertex
    isolated_endpoints = find_isolated_endpoints(snapped_lines)

    # only move isolated endpoints, one by one
    for endpoint in isolated_endpoints:
        # find all vertices within a radius of max_distance as possible
        target = nearest_neighbor_within(snapping_points, endpoint, max_distance)

        if not target:  # do nothing if no target point to snap to is found
            continue

        for i, snapped_line in enumerate(
            snapped_lines
        ):  # find the LineString to modify within snapped_lines and update it
            if endpoint.touches(snapped_line):
                snapped_lines[i] = bend_towards(snapped_line, where=endpoint, to=target)
                break

        for i, snapping_point in enumerate(snapping_points):
            # also update the corresponding snapping_points
            if endpoint.equals(snapping_point):
                snapping_points[i] = target
                break

    # post-processing: remove any resulting lines of length 0
    snapped_lines = [s for s in snapped_lines if s.length > 0]

    return snapped_lines


def bend_towards(
    line: LineString, where: Point, to: Point, tolerance: float = 1e-6
) -> LineString:
    """
    Move the point where along a line to the point at location to.

    :param tolerance:
    :param line:
    :param where: a point ON the line (not necessarily a vertex)
    :param to: a point NOT on the line where the nearest vertex will be moved to
    :return: the modified (bent) line
    """

    if not line.contains(where) and not line.touches(where):
        raise ValueError("line does not contain the point where.")

    coords = line.coords[:]
    # easy case: where is (within numeric precision) a vertex of line
    for k, vertex in enumerate(coords):
        if where.equals_exact(Point(vertex), tolerance=tolerance):
            # move coordinates of the vertex to destination
            coords[k] = to.coords[0]
            return LineString(coords)

    # hard case: where lies between vertices of line, so
    # find the nearest vertex and move that one to point to
    _, min_k = min(
        (where.distance(Point(vertex)), k) for k, vertex in enumerate(coords)
    )
    coords[min_k] = to.coords[0]
    return LineString(coords)


def prune_short_lines(
    lines: Sequence[LineString], min_length: float
) -> List[LineString]:
    """
    Remove lines from a LineString shorter than min_length.

    Deletes all lines from a list of LineStrings or a MultiLineString
    that have a total length of less than min_length. Vertices of touching
    lines are contracted towards the centroid of the removed line.


    :param lines: List of LineStrings or a MultiLineString
    :param min_length: minimum length of a single LineString to be preserved
    :return:  the pruned pandas DataFrame
    """
    pruned_lines = [line for line in lines]  # converts MultiLineString to list
    to_prune = []

    for i, line in enumerate(pruned_lines):
        if line.length < min_length:
            to_prune.append(i)
            for n in intersecting_lines_idx(line, pruned_lines):
                contact_point = line.intersection(pruned_lines[n])
                pruned_lines[n] = bend_towards(
                    pruned_lines[n], where=contact_point, to=line.centroid
                )

    return [line for i, line in enumerate(pruned_lines) if i not in to_prune]


def linemerge(
    line_s: Union[
        LineString, MultiLineString, Iterable[LineString], Iterable[MultiLineString]
    ],
) -> Union[LineString, MultiLineString]:
    """
    Merge a list of LineStrings and/or MultiLineStrings.

    Given a list of LineStrings and possibly MultiLineStrings, merge all of
    them to a single MultiLineString.

    :type line_s: LineString|MultiLineString
    :rtype:LineString|MultiLineString
    """

    assert isinstance(line_s, (LineString, MultiLineString, Sequence))

    if isinstance(line_s, LineString):
        return line_s

    lines = []

    if isinstance(line_s, Iterable):
        for l in line_s:
            a = linemerge(l)
            if isinstance(a, LineString):
                lines.append(a)
            elif isinstance(a, MultiLineString):
                lines.extend(a.geoms)
            else:
                raise NotImplementedError(f"{type(a)} is not supported")

        lines = [l for l in lines if not l.is_empty]
        return shapely.ops.linemerge(lines)

    for line in line_s.geoms:
        if isinstance(line, MultiLineString):
            # line is a multilinestring, so append its components
            lines.extend(line.geoms)
        else:
            # line is a line, so simply append it
            lines.append(line)

    return shapely.ops.linemerge(lines)


def are_incident(v1, v2) -> bool:
    v1 /= numpy.linalg.norm(v1)
    v2 /= numpy.linalg.norm(v2)
    angle = numpy.dot(v1, v2)
    return angle < 1 - EPSILON


def one_linestring_per_intersection(
    lines: Sequence[LineString],
) -> Union[LineString, MultiLineString]:
    """
    Move line endpoints to intersections of line segments.

    Given a list of touching or possibly intersecting LineStrings, return a
     list of LineStrings that have their endpoints at all crossings and
    intersecting points and ONLY there.


    :param lines: A list of LineStrings or a MultiLineString
    :return: a list of LineStrings
    """
    lines_merged = linemerge(lines)

    # intersecting multiline with its bounding box somehow triggers a first
    bounding_box = box(*lines_merged.bounds)

    # perform linemerge (one linestring between each crossing only)
    # if this fails, write function to perform this on a bbox-grid and then
    # merge the result
    lines_merged = lines_merged.intersection(bounding_box)
    lines_merged = linemerge(lines_merged)
    return lines_merged


def intersecting_lines_idx(of: LineString, lines: Sequence[LineString]) -> List[int]:
    """Find the indices in a list of LineStrings that touch a given LineString.


    :param lines: List of LineStrings in which to search for neighbors
    :param of: the LineString, which must be touched
    :return: a list of indices, so that all lines[indices] touch the LineString of
    """
    return [k for k, line in enumerate(lines) if line.touches(of)]


def intersecting_lines(of: LineString, lines: Sequence[LineString]) -> List[LineString]:
    """
    Find the indices in a list of LineStrings that touch a given LineString.


    :param of: The LineString which must be touched
    :param lines: List of LineStrings in which to search for neighbors
    :return: list of indices, so that all lines[indices] touch the LineString of
    """
    return [line for line in lines if line.touches(of)]


def linestring_azimuth(linestring: LineString, verbose: bool = False) -> float:
    """
    # Calculates the angle of a LineString in degrees, meant for linestrings with only two vertices.

    :param verbose:
    :param linestring: Shapely linestring to get the angle of.
    :return: modulo_angle: The angle of the linestring, between 0 and 180 degrees
    """
    coords = linestring.coords
    num_coords = len(coords)

    assert num_coords > 1

    if verbose and num_coords > 2:
        logging.warning(
            f"Linestring has more than 2 vertices {num_coords}, calculating angle of first and last vertices"
        )

    return azimuth(Point(coords[0]), Point(coords[-1]))


class ExtensionDirectionEnum(Enum):
    """ """

    start, end, both = "start", "end", "both"  # assigned_names()


def extend_line(
    line: LineString,
    offset: float,
    side=ExtensionDirectionEnum.both,
    simplify: bool = True,
) -> LineString:
    """
    extend line in the same orientation

    :param line:
    :param offset:
    :param side:
    :param simplify:
    :return:
    """
    side = ExtensionDirectionEnum(side)

    if side == ExtensionDirectionEnum.both:
        sides = [ExtensionDirectionEnum.start, ExtensionDirectionEnum.end]
    else:
        sides = [side]

    for side in sides:
        coords = line.coords

        if side == ExtensionDirectionEnum.start:
            p_new = shift_point(coords[0], coords[1], -1.0 * offset)
            line = LineString([p_new] + coords[1:])

        elif side == ExtensionDirectionEnum.end:
            p_new = shift_point(coords[-1], coords[-2], -1.0 * offset)
            line = LineString(coords[:-1] + [p_new])

    if simplify:
        line = LineString(line.boundary.geoms)

    return line


def extend_lines(
    lines: Union[LineString, MultiLineString, Iterable[LineString]],
    distance: Number,
    simplify: bool = False,
) -> List[LineString]:
    """

    :param simplify:
    :param lines:
    :param distance:
    :return:
    """

    if isinstance(lines, LineString):
        lines = [lines]

    elif isinstance(lines, MultiLineString):
        lines = lines.geoms

    out_lines = []
    for l in lines:
        out_lines.append(extend_line(l, distance, simplify=simplify))

    return out_lines


def cap_lines(
    line: LineString, offset: float = 0.0, length: float = 1.0, eps=1e-11
) -> Tuple[LineString, LineString]:
    """
    Prepare two cap lines at the beginning and end of a LineString object


    :param line:
    :type line: LineString
    :param offset: determining an offset from the beginning/end point
    :param length: length of the cap lines (in same units as LineString coordinates)
    :return: a list with two LineString objects, containing the cap lines
    """
    coords = line.coords

    if offset != 0.0:
        # get start & end point line
        start, end = Point(coords[0]), Point(coords[-1])
    else:  # create short line around endpoints (necessary for perpendicular line function)
        offset = eps
        # get start & end point line
        start = shift_point(coords[0], coords[1], 2 * abs(offset))
        end = shift_point(coords[-1], coords[-2], 2 * abs(offset))

    # extend line at both sides
    start_extend = shift_point(coords[0], coords[1], -2 * abs(offset))
    end_extend = shift_point(coords[-1], coords[-2], -2 * abs(offset))

    # make new line segments
    start_line = LineString([start, start_extend])
    end_line = LineString([end, end_extend])

    # get perpendicular lines at half length of start &  end lines
    cap1 = perpendicular_line(start_line, length)
    cap2 = perpendicular_line(end_line, length)

    return cap1, cap2


def perpendicular_line(l1: LineString, length: float) -> LineString:
    """Create a new Line perpendicular to this linear entity which passes
    through the point `p`.


    """
    dx = l1.coords[1][0] - l1.coords[0][0]
    dy = l1.coords[1][1] - l1.coords[0][1]

    p = Point(l1.coords[0][0] + 0.5 * dx, l1.coords[0][1] + 0.5 * dy)
    x, y = p.coords[0][0], p.coords[0][1]

    if (dy == 0) or (dx == 0):
        a = length / l1.length
        l2 = LineString(
            [(x - 0.5 * a * dy, y - 0.5 * a * dx), (x + 0.5 * a * dy, y + 0.5 * a * dx)]
        )

    else:
        s = -dx / dy
        a = ((length * 0.5) ** 2 / (1 + s**2)) ** 0.5
        l2 = LineString([(x + a, y + s * a), (x - a, y - s * a)])

    return l2


def add_coordinate(line: LineString, distance: float) -> LineString:
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0 or distance >= line.length:
        return line

    coords = list(line.coords)

    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            break
        if pd > distance:
            cp = line.interpolate(distance)
            line = LineString(coords[:i] + [(cp.x, cp.y)] + coords[i:])
            break

    return line


def increase_points_line(line: LineString, spacing: float) -> LineString:
    line_length = line.length
    cp = Point(line.interpolate(line_length - spacing))
    line = LineString(line.coords[:-1] + [(cp.x, cp.y)] + [line.coords[-1]])
    for i, d in enumerate(numpy.arange(line_length, spacing, -spacing)):
        line = add_coordinate(line, d)
    return line


def segments(curve: Union[LinearRing, LineString]) -> List[LineString]:
    """

    :param curve:
    :return:
    """
    return list(map(LineString, zip(curve.coords[:-1], curve.coords[1:])))


def split_line(
    line: LineString, point: Point, tolerance: float = 0.0
) -> MultiLineString:
    """

    split line (Shapely LineString or MultiLineString) at  point (Shapely Point),
    return splitted line (Shapely MultiLineString)

    :param line:
    :param point:
    :param tolerance:
    :return:
    """
    if not isinstance(line, (LineString, MultiLineString)):
        raise TypeError("line should be shapely LineString or MultiLineString object")
    if not isinstance(point, Point):
        raise TypeError("point should be shapely Point object")

    # function works with MultiLineStrings to be able to use the function in a split loop
    if not isinstance(line, MultiLineString):
        line = MultiLineString([line])
    lines_out = []

    # for intersecting line, find intersecting segment and split line
    for l0 in line:
        # check if point on line, but not one of its endpoints
        if (not point.touches(l0.boundary)) and (point.distance(l0) <= tolerance):
            coords = list(l0.coords)
            segments = [LineString(s) for s in pairs(coords)]
            for i, segment in enumerate(segments):
                # find intersecting segment
                if segment.distance(point) <= tolerance:
                    if Point(coords[i]).touches(point):
                        # split line at vertex if within tolerance
                        la = LineString(coords[: i + 1])
                        lb = LineString(coords[i:])
                        if (la.length > tolerance) & (lb.length > tolerance):
                            lines_out.append(la)
                            lines_out.append(lb)
                        else:
                            lines_out.append(l0)
                        break
                    else:
                        # split line at point on segment
                        la = LineString(coords[: i + 1] + [(point.x, point.y)])
                        lb = LineString([(point.x, point.y)] + coords[i + 1 :])
                        if (la.length > tolerance) & (lb.length > tolerance):
                            lines_out.append(la)
                            lines_out.append(lb)
                        else:
                            lines_out.append(l0)
                        break
        else:
            lines_out.append(l0)

    return MultiLineString(lines_out)


def remove_redundant_nodes(
    lines: Sequence[LineString], tolerance: float = EPSILON
) -> List[LineString]:
    """
    remove vertices with length smaller than tolerance
    """
    lines_out = []
    for line in lines:
        coords = line.coords
        l_segments = numpy.array(
            [Point(s[0]).distance(Point(s[1])) for s in pairs(coords)]
        )
        idx = numpy.where(l_segments < tolerance)[0]
        lines_out.append(LineString([c for i, c in enumerate(coords) if i not in idx]))
    return lines_out


if __name__ == "__main__":

    def iashdh():
        print(
            to_single_line(MultiLineString([[[0, 0], [0, 1]], [[0, 2], [0, 3]]]))
        )  # LINESTRING (0 0, 0 1, 0 2, 0 3)

    def ausdh():
        from shapely.geometry import MultiPolygon, Point

        pol1 = MultiPolygon([Point(0, 0).buffer(2.0), Point(1, 1).buffer(2.0)])
        pol2 = Point(7, 8).buffer(1.0)
        pols = [pol1, pol2]

        print(to_lines(pols))

    def uahsduhjasd():
        print(extend_lines(MultiLineString([[[0, 0], [0, 1]], [[0, 2], [0, 3]]]), 1))

    def juashud():
        print(
            explode_lines(
                [
                    MultiLineString([[[0, 0], [0, 1]], [[0, 2], [0, 3]]]),
                    MultiLineString(
                        [
                            [[0, 0], [0, 1]],
                            [[0, 2], [0, 3]],
                            [[0, 1], [1, 2], [2, 3], [3, 4]],
                        ]
                    ),
                    MultiLineString([[[0, 0], [0, 1]], [[0, 2], [0, 3]]]),
                ]
            )
        )

    # juashud()
    # ausdh()
    iashdh()
    uahsduhjasd()

    def uhsaduh():
        v1 = (1, 1)
        v2 = (1, 1)
        v3 = (-1, 1)
        print(are_incident(v1, v1))
        print(are_incident(v1, v2))
        print(are_incident(v1, v3))
        print(are_incident(v2, v3))
        print(are_incident(v3, v3))

    # uhsaduh()
    uahsduhjasd()
