from enum import Enum

# noinspection PyUnresolvedReferences
from qgis._3d import Qgs3DTypes

# noinspection PyUnresolvedReferences
from qgis.core import (
    QgsMultiBandColorRenderer,
    QgsPalettedRasterRenderer,
    QgsSingleBandColorDataRenderer,
    QgsSingleBandGrayRenderer,
    QgsSingleBandPseudoColorRenderer,
)

from jord.geojson_utilities import GeoJsonGeometryTypesEnum

__all__ = [
    "QgisRendererEnum",
    "QgisLayerTypeEnum",
    "Qgis3dFacade",
    "Qgis3dAltitudeBinding",
    "Qgis3dAltitudeClamping",
]


class QgisRendererEnum(Enum):
    multi_band = QgsMultiBandColorRenderer
    paletted_raster = QgsPalettedRasterRenderer
    single_band_color = QgsSingleBandColorDataRenderer
    single_band_gray = QgsSingleBandGrayRenderer
    single_band_pseudo = QgsSingleBandPseudoColorRenderer


class QgisLayerTypeEnum(Enum):
    """
    This enum is useful for exhaustively iterating possible GeoJson types.

    NOTE: Z coordinate support is not included in this enum.
    """

    point = GeoJsonGeometryTypesEnum.point.value.__name__
    multi_point = GeoJsonGeometryTypesEnum.multi_point.value.__name__
    line_string = GeoJsonGeometryTypesEnum.line_string.value.__name__
    multi_line_string = GeoJsonGeometryTypesEnum.multi_line_string.value.__name__
    polygon = GeoJsonGeometryTypesEnum.polygon.value.__name__
    multi_polygon = GeoJsonGeometryTypesEnum.multi_polygon.value.__name__
    curve_polygon = "CurvePolygon"
    multi_surface = "MultiSurface"
    compound_curve = "CompoundCurve"
    multi_curve = "MultiCurve"
    no_geometry = "No Geometry"


class Qgis3dAltitudeBinding(Enum):
    vertex = (
        Qgs3DTypes.AltitudeBinding.Vertex
    )  # 0  # Vertex: Clamp every vertex of feature

    centroid = (
        Qgs3DTypes.AltitudeBinding.Centroid
    )  # Centroid: Clamp just centroid of feature


class Qgis3dAltitudeClamping(Enum):
    absolute = (
        Qgs3DTypes.AltitudeClamping.Absolute
    )  # 0  # Absolute: Elevation is taken directly from feature
    # and is independent of terrain height (
    # final elevation = feature elevation)

    relative = (
        Qgs3DTypes.AltitudeClamping.Relative
    )  # 1  # Relative: Elevation is relative to terrain height
    # (final elevation = terrain elevation +
    # feature elevation)

    terrain = (
        Qgs3DTypes.AltitudeClamping.Terrain
    )  # 2  # Terrain: Elevation is clamped to terrain (final
    # elevation = terrain elevation)


class Qgis3dFacade(Enum):
    no_facade = 0
    walls = 1
    roofs = 2
    walls_and_roofs = 3
