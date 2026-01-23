import logging
import shapely
import shapely.geometry
from shapely.validation import make_valid
from typing import Optional
from warg import passes_kws_to, first

from .uniformity import ensure_cw_poly

__all__ = [
    "closing",
    "opening",
    "erode",
    "erosion",
    "dilate",
    "dilation",
    "close",
    "clean_shape",
    "zero_buffer",
    "pro_opening",
    "pro_closing",
    "BecameEmptyException",
    "collapse_duplicate_vertices",
]


FALLBACK_LINESTRING_CAPSTYLE = shapely.BufferCapStyle.square  # CAN BE OVERRIDDEN
FALLBACK_POINT_CAPSTYLE = shapely.BufferCapStyle.round  # CAN BE OVERRIDDEN
FALLBACK_POINT_JOINSTYLE = shapely.BufferCapStyle.round  # CAN BE OVERRIDDEN
DEFAULT_DISTANCE = 1e-7

_logger = logging.getLogger(__name__)


@passes_kws_to(shapely.geometry.base.BaseGeometry.buffer)
def morphology_buffer(
    geom: shapely.geometry.base.BaseGeometry,
    distance: float = DEFAULT_DISTANCE,
    cap_style: shapely.BufferCapStyle = shapely.BufferCapStyle.flat,
    join_style: shapely.BufferJoinStyle = shapely.BufferJoinStyle.mitre,
    **kwargs,
):
    if geom.is_empty:
        return geom

    if distance == 0:
        if isinstance(geom, shapely.GeometryCollection):
            return shapely.GeometryCollection(
                [
                    morphology_buffer(
                        g,
                        distance=distance,
                        cap_style=cap_style,
                        join_style=join_style,
                        **kwargs,
                    )
                    for g in geom.geoms
                ]
            )

        if not isinstance(
            geom, (shapely.Polygon, shapely.MultiPolygon)
        ):  # So if line(s) or point(s)
            return geom

    if isinstance(
        geom, (shapely.Polygon, shapely.MultiPolygon, shapely.GeometryCollection)
    ):
        if geom.area == 0:
            geom_ = geom.boundary
            if geom_:
                geom = geom_

    if isinstance(geom, (shapely.LineString, shapely.MultiLineString)):
        if geom.length == 0:
            geom_ = geom.representative_point()
            if geom_:
                geom = geom_

    if (
        cap_style == shapely.BufferCapStyle.flat
    ):  # test for parameter NONSENSE, probably not what was intended
        if isinstance(geom, (shapely.Point, shapely.MultiPoint)):
            cap_style = FALLBACK_POINT_CAPSTYLE
            join_style = FALLBACK_POINT_JOINSTYLE
        elif isinstance(geom, (shapely.LineString, shapely.MultiLineString)):
            cap_style = FALLBACK_LINESTRING_CAPSTYLE

    res = geom.buffer(
        distance=distance, cap_style=cap_style, join_style=join_style, **kwargs
    )

    if res.is_empty:
        return geom

    return res


@passes_kws_to(morphology_buffer)
def erosion(
    geom: shapely.geometry.base.BaseGeometry,
    distance: float = DEFAULT_DISTANCE,
    **kwargs,
) -> shapely.geometry.base.BaseGeometry:
    """

    :param distance:
    :param cap_style:
    :param join_style:
    :param geom: The geometry to be eroded
    :return: The eroded geometry
    """
    return morphology_buffer(geom=geom, distance=-distance, **kwargs)


@passes_kws_to(morphology_buffer)
def dilation(
    geom: shapely.geometry.base.BaseGeometry,
    distance: float = DEFAULT_DISTANCE,
    **kwargs,
) -> shapely.geometry.base.BaseGeometry:
    """

    :param cap_style:
    :param join_style:
    :param geom: The geometry to be dilated
    :param distance: Dilation amount
    :return: The dilated geometry
    """

    return morphology_buffer(geom=geom, distance=distance, **kwargs)


@passes_kws_to(shapely.geometry.base.BaseGeometry.buffer)
def closing(
    geom: shapely.geometry.base.BaseGeometry, **kwargs
) -> shapely.geometry.base.BaseGeometry:
    """

    :param geom: The geometry to be closed
    :return: The closed geometry
    """
    return erode(dilate(geom, **kwargs), **kwargs)


@passes_kws_to(shapely.geometry.base.BaseGeometry.buffer)
def opening(
    geom: shapely.geometry.base.BaseGeometry, **kwargs
) -> shapely.geometry.base.BaseGeometry:
    """

    :param geom: The geometry to be opened
    :return: The opened geometry
    """
    return dilate(erode(geom, **kwargs), **kwargs)


@passes_kws_to(shapely.geometry.base.BaseGeometry.buffer)
def pro_closing(
    geom: shapely.geometry.base.BaseGeometry, **kwargs
) -> shapely.geometry.base.BaseGeometry:
    """
      Remove Salt and Pepper

      Common Variants
    Opening and closing are themselves often used in combination to achieve more subtle results. If we
    represent the closing of an image f by C(f), and its opening by O(f), then some common combinations include:

    Proper Opening
    Min(f, /em{C}(O(C(f))))

    Proper Closing
    Max(f, O(C(O(f))))

    Automedian Filter
    Max(O(C(O(f))), Min(f, C(O(C(f)))))

    These operators are commonly known as morphological filters.


    Closing
    Dilation means that the central pixel will be replaced by the brightest pixel in the vicinity (filter
    structural element).
    Perfect for removing pepper noise and ensuring that the key features are relatively sharp.

    Opening
    Erosion means is that if we have a structuring element that is a 3 X 3 matrix, the central pixel will be
    replaced by the darkest pixel in the 3 X 3 neighborhood.
    Opening is erosion followed by dilation which makes it perfect for removing salt noise (white dots) and
    ensuring that the key features are relatively sharp.

      :param geom:
      :param kwargs:
      :return:
    """

    return opening(closing(opening(geom, **kwargs), **kwargs), **kwargs)


@passes_kws_to(shapely.geometry.base.BaseGeometry.buffer)
def pro_opening(
    geom: shapely.geometry.base.BaseGeometry, **kwargs
) -> shapely.geometry.base.BaseGeometry:
    """
      Remove Salt and Pepper

      Common Variants
    Opening and closing are themselves often used in combination to achieve more subtle results. If we
    represent the closing of an image f by C(f), and its opening by O(f), then some common combinations include:

    Proper Opening
    Min(f, /em{C}(O(C(f))))

    Proper Closing
    Max(f, O(C(O(f))))

    Automedian Filter
    Max(O(C(O(f))), Min(f, C(O(C(f)))))

    These operators are commonly known as morphological filters.


    Closing
    Dilation means that the central pixel will be replaced by the brightest pixel in the vicinity (filter
    structural element).
    Perfect for removing pepper noise and ensuring that the key features are relatively sharp.

    Opening
    Erosion means is that if we have a structuring element that is a 3 X 3 matrix, the central pixel will be
    replaced by the darkest pixel in the 3 X 3 neighborhood.
    Opening is erosion followed by dilation which makes it perfect for removing salt noise (white dots) and
    ensuring that the key features are relatively sharp.

      :param geom:
      :param kwargs:
      :return:
    """

    return closing(opening(closing(geom, **kwargs), **kwargs), **kwargs)


# open = opening # keyword clash
erode = erosion
dilate = dilation
close = closing


def zero_buffer(
    geom: shapely.geometry.base.BaseGeometry,
) -> shapely.geometry.base.BaseGeometry:
    return dilate(geom, distance=0)


class BecameEmptyException(Exception): ...


def clean_shape(
    shape: shapely.geometry.base.BaseGeometry,
    grid_size: Optional[float] = None,
    raise_on_becoming_empty: bool = False,
) -> shapely.geometry.base.BaseGeometry:
    """
    removes self-intersections and duplicate points

    :param raise_on_becoming_empty:
    :param grid_size:
    :param shape: The shape to cleaned
    :return: the cleaned shape
    """

    original_shape = shape

    if isinstance(shape, shapely.Polygon):
        shape = ensure_cw_poly(shape)

    if grid_size is not None:
        if not shape.is_valid:
            try:
                shape = make_valid(shape)
            except shapely.errors.GEOSException as e:
                _logger.error(e)

        shape = shapely.set_precision(
            shape,
            grid_size,
            mode="keep_collapsed",
        )

    shape = collapse_duplicate_vertices(shape)

    if not shape.is_valid:
        try:
            shape = make_valid(shape)
        except shapely.errors.GEOSException as e:
            _logger.error(e)

    if not original_shape.is_empty:
        if shape.is_empty:
            if raise_on_becoming_empty:
                raise BecameEmptyException(
                    f"{original_shape=} was not empty, became {shape=}"
                )
            else:
                shape = original_shape.representative_point()

    if isinstance(shape, shapely.GeometryCollection):
        if len(shape.geoms) == 1:
            shape = first(shape.geoms)

    return shape


def collapse_duplicate_vertices(
    shape: shapely.geometry.base.BaseGeometry,
) -> shapely.geometry.base.BaseGeometry:
    return zero_buffer(shape).simplify(0)
