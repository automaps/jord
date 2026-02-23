import pytest
import shapely

from jord.shapely_utilities.base import sanitise
from jord.shapely_utilities.morphology import clean_shape, dilate, zero_buffer


def test_point_clean_shape():
    p = shapely.Point((1, 1))
    assert clean_shape(p) == p


def test_linestring_clean_shape():
    p = shapely.LineString([(1, 1), (2, 2)])
    assert clean_shape(p) == p


def test_geometry_collection_clean_shape():
    p = shapely.GeometryCollection(
        [shapely.LineString([(1, 1), (2, 2)]), shapely.Point((1, 1))]
    )
    assert clean_shape(p) == p


def test_sanitise_kwargs():
    p = shapely.GeometryCollection(
        [shapely.LineString([(1, 1), (2, 2)]), shapely.Point((1, 1))]
    )

    def i(g, *, a=None):
        """

        :param g:
        :type g:
        :param a:
        :type a:
        :return:
        :rtype:
        """
        assert a == 1
        return g

    assert sanitise(p, i, kwargs={i: {"a": 1}}) == p


def test_sanitise_geom_zero():
    p = shapely.GeometryCollection(
        [shapely.LineString([(1, 1), (2, 2)]), shapely.Point((1, 1))]
    )

    assert sanitise(p, zero_buffer) == p


def test_sanitise_poly():
    p = shapely.Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1), (-1, 1)])

    assert sanitise(p).equals(p)


def test_clean_shape():
    p = shapely.Polygon([(-1, 1), (1, 1), (1, -1), (-1, -1), (-1, 1)])

    assert clean_shape(p).equals(p)


def test_clean_invalid_shape():
    p = shapely.Polygon(
        [
            (0, 0),
            (0, 3),
            (3, 3),
            (3, 0),
            (2, 0),
            (2, 2),
            (1, 2),
            (1, 1),
            (2, 1),
            (2, 0),
            (0, 0),
        ]
    )

    assert not p.is_valid
    assert clean_shape(p).is_valid


@pytest.mark.parametrize(
    "p",
    [
        shapely.Point(),
        shapely.LineString(),
        shapely.Polygon(),
        shapely.MultiPolygon(),
        shapely.MultiPoint(),
        shapely.MultiLineString(),
        shapely.GeometryCollection(),
    ],
)
def test_clean_empty_shape(p: shapely.geometry.base.BaseGeometry):
    assert p.is_empty
    assert clean_shape(p).is_empty


@pytest.mark.parametrize(
    "p,expected",
    [
        (shapely.MultiPoint([shapely.Point((-1, 1))]), shapely.Point((-1, 1))),
        (shapely.LineString(((1, 1), (1, 1))), shapely.Point((1, 1))),
        (shapely.Polygon(((1, 1), (1, 1), (1, 1), (1, 1))), shapely.Point((1, 1))),
        (
            shapely.MultiPolygon([shapely.Polygon(((1, 1), (1, 1), (1, 1), (1, 1)))]),
            shapely.Point((1, 1)),
        ),
        (
            shapely.MultiLineString([shapely.LineString(((1, 1), (1, 1)))]),
            shapely.Point((1, 1)),
        ),
        (
            shapely.GeometryCollection(
                [shapely.MultiLineString([shapely.LineString(((1, 1), (1, 1)))])]
            ),
            shapely.Point((1, 1)),
        ),
        (
            shapely.GeometryCollection(
                [
                    shapely.MultiPolygon(
                        [shapely.Polygon(((1, 1), (1, 1), (1, 1), (1, 1)))]
                    )
                ]
            ),
            shapely.Point((1, 1)),
        ),
        (
            shapely.GeometryCollection(
                [
                    shapely.MultiPolygon(
                        [shapely.Polygon(((1, 1), (1, 1), (1, 1), (1, 1)))]
                    ),
                    shapely.MultiLineString([shapely.LineString(((1, 1), (1, 1)))]),
                ]
            ),
            shapely.GeometryCollection(
                [shapely.Point((1, 1)), shapely.Point((1, 1))],
            ),
        ),
    ],
)
def test_clean_collapsing_cases(p: shapely.geometry.base.BaseGeometry, expected):
    assert clean_shape(p) == expected


def test_null_point_become_poly_after_dilation():
    NULL_POLYGON = dilate(shapely.Point([0, 0]), distance=1)

    assert isinstance(NULL_POLYGON, shapely.Polygon)
    assert NULL_POLYGON.area > 0
    assert not NULL_POLYGON.is_empty
    assert NULL_POLYGON.is_valid
