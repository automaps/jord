import logging

# noinspection PyUnresolvedReferences
import qgis._3d as q3d

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtCore import QSizeF

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtGui import QColor

# noinspection PyUnresolvedReferences
from qgis._3d import Qgs3DTypes

# noinspection PyUnresolvedReferences
from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsLineSymbol,
    QgsPalLayerSettings,
    QgsProject,
    QgsRendererCategory,
    QgsSymbol,
    QgsTextBackgroundSettings,
    QgsTextFormat,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
    QgsWkbTypes,
)

# noinspection PyUnresolvedReferences
from qgis.utils import iface
from typing import Any, Iterable, Mapping, Optional
from warg import Number, TripleNumber

from jord.qgis_utilities.enums import (
    Qgis3dAltitudeBinding,
    Qgis3dAltitudeClamping,
    Qgis3dFacade,
)

__all__ = [
    "style_layer_from_mapping",
    "set_3d_view_settings",
    "set_label_styling",
    "set_layer_rendering_scale",
]

_logger = logging.getLogger(__name__)


def style_layer_from_mapping(
    layer: QgsVectorLayer,
    style_mapping_field_dict: Mapping,
    field_name: str = "layer",
    default_color: TripleNumber = (0, 0, 0),
    default_opacity: float = 1.0,
    default_width: float = 0.1,
    *,
    repaint: bool = True,
) -> None:
    if layer is None:
        return

    style_mapping = style_mapping_field_dict[field_name]

    render_categories = []
    for cat in layer.uniqueValues(layer.fields().indexFromName(field_name)):
        cat_color = default_color
        cat_opacity = default_opacity
        cat_width = default_width
        label = str(cat)

        if cat in style_mapping.keys():
            style = style_mapping[label]
            if "color" in style:
                cat_color = (
                    int(n) for n in style["color"]
                )  # TODO: also support with AlphaChannel | Qt.GlobalColor | QGradient
            if "opacity" in style:
                cat_opacity = max(0.0, min(float(style["opacity"]), 1.0))
            if "width" in style:
                cat_width = max(0.0, float(style["width"]))

        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        symbol.setColor(QColor(*cat_color, 255))
        symbol.setOpacity(cat_opacity)

        if isinstance(symbol, QgsLineSymbol):
            symbol.setWidth(cat_width)
        else:
            logging(f"width ignored, symbol is of type: {type(symbol)}")

        render_categories.append(
            QgsRendererCategory(cat, symbol=symbol, label=label, render=True)
        )

    layer.setRenderer(QgsCategorizedSymbolRenderer(field_name, render_categories))
    if repaint:
        layer.triggerRepaint()


def set_layer_rendering_scale(
    layers: QgsVectorLayer,
    *,
    max_ratio: float = 1.0,
    min_ratio: float = 1 / 9999,
):
    """

    :param layers:
    :param max_ratio:
    :param min_ratio:
    :return:
    """

    # logger.warning(f"Setting layer rendering scale {max_ratio=} {min_ratio=}")

    if layers is None:
        return

    if not isinstance(
        layers, Iterable
    ):  # Handle both single layer and iterable of layers
        layers = [layers]

    assert max_ratio <= 1
    assert min_ratio <= max_ratio

    for layer in layers:
        if not layer:
            continue

        layer.setScaleBasedVisibility(True)
        layer.setMinimumScale(1.0 / min_ratio)
        layer.setMaximumScale(max_ratio)

        # Calling setMinimumScale() places a restriction on the acceptable maximum scale for the widget, and will alter any previously set maximum scale to pass this constraint. Always call setMinimumScale() before setMaximumScale() when restoring a scale range in the widget, or use the convenience method setScaleRange() instead.


def set_label_styling(
    layers: QgsVectorLayer,
    *,
    field_name: str = "name",
    max_ratio: float = 1.0,
    min_ratio: float = 1 / 999,
    font_size: int = 10,
    background: bool = False,
    background_color: tuple = (255, 255, 255, 200),
    background_svg: str = None,
    html_format: Optional[str] = None,
):
    # logger.warning(f"Setting layer label rendering scale {max_ratio=} {min_ratio=}")

    if layers is None:
        return

    assert max_ratio <= 1
    assert min_ratio <= max_ratio

    # Handle both single layer and iterable of layers
    if not isinstance(layers, Iterable):
        layers = [layers]

    for layer in layers:
        if not layer:
            continue

        # Create label settings
        label_settings = QgsPalLayerSettings()

        # Set field name with optional HTML formatting
        if html_format:  # ACTUALLY USE HTML
            # label_settings.isExpression = True
            label_settings.allowHtml = True
            label_settings.fieldName = (
                f"'<div style=\"text-align: center;\">' || {field_name} || '</div>'"
            )
        else:
            label_settings.fieldName = field_name

        # Set font settings
        format = QgsTextFormat()
        format.setSize(font_size)
        format.setNamedStyle("Regular")
        format.setColor(QColor(0, 0, 0))

        # Set background if enabled
        if background:
            bg_buffer = QgsTextBackgroundSettings()
            bg_buffer.setEnabled(True)
            bg_buffer.setFillColor(QColor(*background_color))
            bg_buffer.setSize(QSizeF(1, 0.5))
            bg_buffer.setType(QgsTextBackgroundSettings.ShapeRectangle)

            if background_svg:
                bg_buffer.setSvgFile(background_svg)
                bg_buffer.setType(QgsTextBackgroundSettings.ShapeSVG)

            format.setBackground(bg_buffer)

        label_settings.setFormat(format)

        label_settings.scaleVisibility = True
        label_settings.minimumScale = 1.0 / min_ratio  # Furthest zoom level
        label_settings.maximumScale = max_ratio  # Closest zoom level

        label_settings.placement = QgsPalLayerSettings.AroundPoint
        label_settings.priority = 5
        label_settings.obstacleScale = 1.0
        label_settings.enabled = True
        label_settings.isExpression = True

        layer_simple_label = QgsVectorLayerSimpleLabeling(label_settings)
        layer.setLabelsEnabled(True)
        layer.setLabeling(layer_simple_label)
        layer.triggerRepaint()

        # layer.resolveReferences(QgsProject.instance())
        # layer.reload()
        # layer.styleManager().
        # layer.styleChanged.emit()
        # layer.countSymbolFeatures()
        # layer.symbolFeatureCountMapChanged.emit()

        # iface.layerTreeView().refreshLayerSymbology(layer.id())
        # QgsProject.instance().reloadAllLayers()

        # node = QgsProject.instance().layerTreeRoot().findLayer(layer.id())
        # iface.layerTreeView().layerTreeModel().refreshLayerLegend(node)


def make_line_symbol(
    culling_mode, edge_color, edge_width, extrusion, facades, offset
) -> Any:
    # ->q3d.QgsPolygon3DSymbol:

    symbol = q3d.QgsLine3DSymbol()
    symbol.setWidth(edge_width)
    symbol.setOffset(offset)
    symbol.setExtrusionHeight(extrusion)
    symbol.setRenderAsSimpleLines(True)

    return symbol


def make_point_symbol(
    culling_mode: Qgs3DTypes.CullingMode,
    edge_color: TripleNumber,
    edge_width: Number,
    extrusion: Number,
    facades: Qgis3dFacade,
    offset: Number,
) -> Any:
    # ->q3d.QgsPolygon3DSymbol:

    symbol = q3d.QgsPoint3DSymbol()
    # symbol.setShape(q3d.QgsSymbol3DShape.Cylinder)
    # symbol.setHeight()
    # symbol.setRadius(extrusion)
    # symbol.setCullingMode(culling_mode.value)
    # symbol.setTransformation(0, 0, offset)
    return symbol


def set_3d_view_settings(
    layers: QgsVectorLayer,
    *,
    offset: float = 0,
    extrusion: float = 4,
    color: TripleNumber = (222, 222, 222),
    facades: Qgis3dFacade = Qgis3dFacade.walls,
    culling_mode: Qgs3DTypes.CullingMode = Qgs3DTypes.CullingMode.Front,
    repaint: bool = True,
    edge_width: float = 1.0,
    edge_color: TripleNumber = (255, 255, 255),
) -> None:
    if layers is None:
        return

    polygon_renderer = make_renderer(
        color,
        make_polygon_symbol(
            culling_mode, edge_color, edge_width, extrusion, facades, offset
        ),
    )

    line_renderer = make_renderer(
        color,
        make_line_symbol(
            culling_mode, edge_color, edge_width, extrusion, facades, offset
        ),
    )

    point_renderer = make_renderer(
        color,
        make_point_symbol(
            culling_mode, edge_color, edge_width, extrusion, facades, offset
        ),
    )

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layer in layers_inner:
                    if layer:
                        set_renderer(
                            layer, line_renderer, point_renderer, polygon_renderer
                        )

                        if repaint:
                            layer.triggerRepaint()
            else:
                set_renderer(
                    layers_inner, line_renderer, point_renderer, polygon_renderer
                )
                if repaint:
                    layers_inner.triggerRepaint()


def set_renderer(layer, line_renderer, point_renderer, polygon_renderer):
    if layer.geometryType() == QgsWkbTypes.PointGeometry:  # QgsWkbTypes.Point:
        layer.setRenderer3D(point_renderer)
    elif layer.geometryType() == QgsWkbTypes.LineGeometry:  # QgsWkbTypes.Line:
        layer.setRenderer3D(line_renderer)
    elif layer.geometryType() == QgsWkbTypes.PolygonGeometry:  # QgsWkbTypes.Polygon:
        layer.setRenderer3D(polygon_renderer)
    else:
        _logger.error(f"geometry type not supported: {layer.geometryType()}, skipping")


def make_renderer(color: TripleNumber, symbol: QgsSymbol) -> Any:  #    QgsRenderer
    apply_common_symbol_settings(symbol)
    apply_material(color, symbol)
    renderer = q3d.QgsVectorLayer3DRenderer()
    renderer.setSymbol(symbol)

    return renderer


def make_polygon_symbol(
    culling_mode: Qgs3DTypes.CullingMode,
    edge_color: TripleNumber,
    edge_width: Number,
    extrusion: Number,
    facades: Qgis3dFacade,
    offset: Number,
) -> Any:
    # ->q3d.QgsPolygon3DSymbol:

    symbol = q3d.QgsPolygon3DSymbol()
    symbol.setCullingMode(culling_mode)
    symbol.setOffset(offset)
    symbol.setExtrusionHeight(extrusion)
    symbol.setRenderedFacade(facades.value)

    if edge_width > 0:
        symbol.setEdgesEnabled(True)
    else:
        symbol.setEdgesEnabled(False)

    symbol.setEdgeWidth(edge_width)
    symbol.setEdgeColor(QColor(*edge_color))
    symbol.setAddBackFaces(False)
    # symbol.setInvertNormals(False)

    return symbol


def apply_common_symbol_settings(symbol: Any) -> None:
    if symbol is None:
        _logger.error("symbol is None, skipping")
        return

    if hasattr(symbol, "setAltitudeBinding"):
        symbol.setAltitudeBinding(Qgis3dAltitudeBinding.centroid.value)
    if hasattr(symbol, "setAltitudeClamping"):
        symbol.setAltitudeClamping(Qgis3dAltitudeClamping.absolute.value)


def apply_material(color: TripleNumber, symbol: Any) -> None:

    material_settings = q3d.QgsPhongMaterialSettings()

    q_color = QColor(*color)
    material_settings.setAmbient(q_color)
    material_settings.setDiffuse(q_color)
    material_settings.setSpecular(q_color)
    symbol.setMaterialSettings(material_settings)
