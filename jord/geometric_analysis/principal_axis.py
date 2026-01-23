import logging
import shapely
from enum import Enum
from shapely import affinity
from typing import Collection, Tuple, Union

__all__ = [
    "compute_center_principal_axes",
    "buffer_principal_axis",
    "buffer_secondary_axis",
    "PrincipalityMeasure",
    "other_mass_projection_is_longer",
]

_logger = logging.getLogger(__name__)


class PrincipalityMeasure(Enum):
    double_doors = "double_doors"
    length = "length"
    density = "density"
    hybrid = "hybrid"


def other_mass_projection_is_longer(
    poly: shapely.geometry.base.BaseGeometry,
    first_axis: shapely.LineString,
    other_axis: shapely.LineString,
    hybrid_normalised_axes_projections: bool = False,
) -> bool:
    first_axis_projection_length = first_axis.project(
        poly.centroid, normalized=hybrid_normalised_axes_projections
    )
    other_axis_projection_length = other_axis.project(
        poly.centroid, normalized=hybrid_normalised_axes_projections
    )

    return other_axis_projection_length > first_axis_projection_length


def compute_center_principal_axes(
    poly: shapely.geometry.base.BaseGeometry,
    principality_measure: PrincipalityMeasure = PrincipalityMeasure.length,
    hybrid_ratio_threshold: float = 0.1,
    oppose_hybrid_ratio_cases: bool = True,  # TODO: WACKY
    normalised_projections: bool = False,
    translate_axes: bool = True,
) -> Tuple[shapely.LineString, shapely.LineString]:
    if not isinstance(poly, shapely.geometry.base.BaseGeometry):
        assert isinstance(
            poly, Collection
        ), f"{poly} was an collection of shapely objects"
        poly = shapely.unary_union(poly)

    minimum_rotated_rectangle: shapely.Polygon = poly.minimum_rotated_rectangle

    x, y = minimum_rotated_rectangle.exterior.coords.xy

    first_axis = shapely.LineString(
        [shapely.Point(x[0], y[0]), shapely.Point(x[1], y[1])]
    )
    other_axis = shapely.LineString(
        [shapely.Point(x[1], y[1]), shapely.Point(x[2], y[2])]
    )

    principal_axis = first_axis
    secondary_axis = other_axis

    if principality_measure == PrincipalityMeasure.length:
        if first_axis.length < other_axis.length:
            principal_axis, secondary_axis = secondary_axis, principal_axis

    elif principality_measure == PrincipalityMeasure.density:
        if other_mass_projection_is_longer(
            poly, first_axis, other_axis, normalised_projections
        ):
            principal_axis, secondary_axis = secondary_axis, principal_axis

    elif principality_measure == PrincipalityMeasure.hybrid:
        ratio = first_axis.length / other_axis.length
        if ratio < 1.0 - hybrid_ratio_threshold:
            if oppose_hybrid_ratio_cases:
                principal_axis, secondary_axis = secondary_axis, principal_axis
        elif ratio > 1.0 + hybrid_ratio_threshold:
            if not oppose_hybrid_ratio_cases:
                principal_axis, secondary_axis = secondary_axis, principal_axis
        elif other_mass_projection_is_longer(
            poly, first_axis, other_axis, normalised_projections
        ):
            principal_axis, secondary_axis = secondary_axis, principal_axis
        else:
            ...  # do not swap

    elif principality_measure == PrincipalityMeasure.double_doors:
        ...  # TODO: Grow centroid, test for intersection?

    else:
        raise NotImplementedError(f"{principality_measure=} is not supported")

    if translate_axes:
        return (
            affinity.translate(
                principal_axis,
                xoff=minimum_rotated_rectangle.centroid.x - principal_axis.centroid.x,
                yoff=minimum_rotated_rectangle.centroid.y - principal_axis.centroid.y,
            ),
            affinity.translate(
                secondary_axis,
                xoff=minimum_rotated_rectangle.centroid.x - secondary_axis.centroid.x,
                yoff=minimum_rotated_rectangle.centroid.y - secondary_axis.centroid.y,
            ),
        )

    return principal_axis, secondary_axis


def buffer_principal_axis(
    poly: shapely.geometry.base.BaseGeometry, distance: float = 1.4, **kwargs
) -> Union[shapely.Polygon, shapely.MultiPolygon]:
    pax, sax = compute_center_principal_axes(poly, **kwargs)
    return shapely.buffer(
        pax,
        sax.length / distance,
        # single_sided=True,
        cap_style=shapely.BufferCapStyle.flat,
    )


def buffer_secondary_axis(
    poly: shapely.geometry.base.BaseGeometry, distance: float = 1.4, **kwargs
) -> Union[shapely.Polygon, shapely.MultiPolygon]:
    pax, sax = compute_center_principal_axes(poly, **kwargs)
    return shapely.buffer(
        sax,
        pax.length / distance,
        # single_sided=True,
        cap_style=shapely.BufferCapStyle.flat,
    )


if __name__ == "__main__":

    def juashdu():
        door_wkt = """Polygon ((0.41771353596173888 0.45279106470461222, 0.42202990913524002
    0.44398345695594388, 0.42503883676252752 0.4322059060841496, 0.42406995639706679 0.43195837661635911,
    0.42108655796187611 0.44363600107054563, 0.41687005351423739 0.45223982556683989, 0.41178976975322512
    0.45824659085939767, 0.4062094412971064 0.46209824156605428, 0.40048080898385668 0.46422433579765993,
    0.39496063520860603 0.46503887492821949, 0.39001768047859658 0.46495146513763091, 0.38602765447831972
    0.46437481857520818, 0.38418851989281072 0.46392574885392379, 0.39047171136412068 0.42633994643201001,
    0.38948539794731218 0.42617506512978409, 0.38321620905574583 0.46367710467449691, 0.3824000529003504
    0.46341698788591579, 0.38209639266092799 0.46436976826931692, 0.38304962997471709 0.46467357413683308,
    0.38278232913254839 0.46627255718340038, 0.38376864254935689 0.46643743848562641, 0.38402318794159729
    0.46491475803511939, 0.38583709534983551 0.46535766792364591, 0.38993700301857598 0.46595019480524158,
    0.39502521705723481 0.4660401733196895, 0.40073048270725042 0.46519832262596478, 0.40667459603281331
    0.46299225591362603, 0.41246735498600151 0.4589939815663383, 0.41771353596173888 0.45279106470461222))"""

        buffer_secondary_axis(
            shapely.from_wkt(door_wkt), principality_measure=PrincipalityMeasure.hybrid
        )

    juashdu()
