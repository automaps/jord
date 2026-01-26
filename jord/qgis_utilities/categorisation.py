import logging
import random
from itertools import cycle
from typing import Any, Callable, Generator, Iterable, Sized

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtCore import QVariant

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtGui import QColor

# noinspection PyUnresolvedReferences
from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsFeature,
    QgsFeatureRequest,
    QgsProject,
    QgsRendererCategory,
    QgsSimpleFillSymbolLayer,
    QgsSymbol,
    QgsVectorLayer,
    QgsVectorLayerUtils,
)

# noinspection PyUnresolvedReferences
from qgis.utils import iface
from warg import QuadNumber, TripleNumber, n_uint_mix_generator_builder

__all__ = [
    "categorise_layer",
    "random_color_alpha_generator",
    "random_color_generator",
    "random_rgba",
    "random_rgb",
    "styled_field_value_categorised",
]

_logger = logging.getLogger(__name__)


def random_rgb(mix: TripleNumber = (255, 255, 255)) -> TripleNumber:
    """

    :param mix: The upper limit of each element of the RGB Tuple
    :return: random RGB Tuple
    """
    red = random.randrange(0, mix[0])
    green = random.randrange(0, mix[1])
    blue = random.randrange(0, mix[2])
    return red, green, blue


def random_rgba(mix: QuadNumber = (1, 1, 1, 1)) -> QuadNumber:
    """

    :param mix: The upper limit of each element of the RGBA Tuple
    :return: random RGBA Tuple
    """
    red = random.randrange(0, mix[0])
    green = random.randrange(0, mix[1])
    blue = random.randrange(0, mix[2])
    alpha = random.randrange(0, mix[3])
    return red, green, blue, alpha


def random_color_generator(
    mix: TripleNumber = (1, 1, 1)
) -> Generator[TripleNumber, None, None]:
    """

    :param mix: The upper limit of each element of the RGBA Tuple
    :return: A generator of random RGB Tuples
    """
    while 1:
        yield random_rgb(mix=mix)


def random_color_alpha_generator(
    mix: QuadNumber = (1, 1, 1, 1)
) -> Generator[QuadNumber, None, None]:
    """

    :param mix: The upper limit of each element of the RGBA Tuple
    :return: A generator of random RGBA Tuples
    """
    while 1:
        yield random_rgba(mix=mix)


def categorise_layer(
    layer: QgsVectorLayer,
    field_name: str = "layer",
    *,
    color_iterable: Iterable = n_uint_mix_generator_builder(
        255, 255, 255, mix_min=(0, 0, 0)
    ),
    opacity: float = 1.0,
    outline_only: bool = False,
    outline_width=1.0,
) -> None:
    """

    https://qgis.org/pyqgis/3.0/core/Vector/QgsVectorLayer.html
    https://qgis.org/pyqgis/3.0/core/other/QgsFields.html

    :param outline_width:
    :param outline_only:
    :param opacity:
    :param layer:
    :param field_name:
    :param color_iterable:
    :return:
    """

    if isinstance(color_iterable, Sized):
        # noinspection PyTypeChecker
        color_iterable = cycle(color_iterable)

    if isinstance(color_iterable, Callable) and not isinstance(
        color_iterable, Generator
    ):
        # noinspection PyCallingNonCallable
        color_iterable = color_iterable()  # Compat

    color_iter = iter(color_iterable)

    available_field_names = layer.fields().names()

    assert (
        field_name in available_field_names
    ), f"Did not find {field_name=} in {available_field_names=}"

    render_categories = []
    for cat in layer.uniqueValues(layer.fields().indexFromName(field_name)):
        if cat is not None:
            sym = QgsSymbol.defaultSymbol(layer.geometryType())
            if sym is not None:
                set_symbol_styling(
                    color_iter, opacity, outline_only, outline_width, sym
                )

                render_categories.append(
                    QgsRendererCategory(cat, symbol=sym, label=str(cat), render=True)
                )

    if True:  # add default
        sym = QgsSymbol.defaultSymbol(layer.geometryType())
        # https://qgis.org/pyqgis/master/core/QgsSymbolLayer.html#qgis.core.QgsSymbolLayer.setFillColor
        # https://qgis.org/pyqgis/3.40/core/QgsSimpleLineSymbolLayer.html
        # QgsLinePatternFillSymbolLayer

        # sym.symbolLayer(0).setStrokeColor(QColor(*col))
        # StrokeWidth
        # StrokeStyle
        # FillColor
        # FillStyle

        if sym is not None:
            set_symbol_styling(color_iter, opacity, outline_only, outline_width, sym)

            render_categories.append(
                QgsRendererCategory(
                    QVariant(""), symbol=sym, label="default", render=True
                )
            )

        if False:
            # render_categories.append(QgsRendererCategory()) # crashes qgis
            render_categories.append(
                QgsRendererCategory([], symbol=sym, label="EmptyList", render=True)
            )
            render_categories.append(
                QgsRendererCategory("", symbol=sym, label="EmptyString", render=True)
            )
            render_categories.append(
                QgsRendererCategory("None", symbol=sym, label="None", render=True)
            )

    layer.setRenderer(QgsCategorizedSymbolRenderer(field_name, render_categories))
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())


def styled_field_value_categorised(
    layer: Any, style_attributes_layer, field_name="location_type"
) -> None:
    expression_str = f'represent_value("{field_name}")'
    # expression_str_unquoted = f'represent_value({field_name})'

    asd = QgsVectorLayerUtils.getValues(layer, expression_str, selectedOnly=False)
    cats = asd[0]

    if True:
        render_categories = []
        added_references = set()

        style_features = {
            f["admin_id"]: f for f in style_attributes_layer.getFeatures()
        }

        # refs = [r.lstrip('{').rstrip('}') for r in refs]
        refs = QgsVectorLayerUtils.getValues(layer, field_name, selectedOnly=False)[0]

        assert len(refs) == len(cats), f"{refs=}, {cats=}"

        for ref, cat in zip(refs, cats, strict=True):
            if False:
                _logger.error(cat)

            if cat is not None and ref not in added_references:
                sym = QgsSymbol.defaultSymbol(layer.geometryType())

                # Apply style from reference feature if available
                if ref in style_features:
                    style_feature = style_features[ref]
                    key = "display_rule.polygon.fillColor"
                    if key in style_feature.fields().names():
                        fill_color = str(style_feature[key])
                        if "#" in fill_color:
                            if False:
                                _logger.error(
                                    f"Set fill_color {fill_color} for {cat} in layer {layer.id()}"
                                )
                            sym.setColor(QColor(fill_color))
                        else:
                            if False:
                                _logger.error(
                                    f"Did not set fill_color for {cat} in layer {layer.id()}"
                                )

                render_categories.append(
                    QgsRendererCategory(
                        QVariant(ref), symbol=sym, label=str(cat), render=True, uuid=ref
                    )
                )
                added_references.add(ref)

        sym = QgsSymbol.defaultSymbol(layer.geometryType())
        render_categories.append(
            QgsRendererCategory(
                QVariant(None),
                symbol=sym,
                label="",
                render=True,
                # uuid=ref
            )
        )

        # renderer = QgsCategorizedSymbolRenderer(expression_str, render_categories) # DOES NOT WORK PROPER

        renderer = QgsCategorizedSymbolRenderer(field_name, render_categories)

    else:
        renderer = QgsCategorizedSymbolRenderer()
        renderer.setClassAttribute(expression_str)

        for c in renderer.createCategories(
            cats, QgsSymbol.defaultSymbol(layer.geometryType())
        ):
            renderer.addCategory(c)

    # renderer.filter()
    # renderer.setUsingSymbolLevels()

    # renderer.setOrderBy(QgsFeatureRequest.OrderBy([QgsFeatureRequest.OrderByClause(expression_str, False)]))
    # renderer.setOrderByEnabled(True)

    layer.setRenderer(renderer)
    layer.triggerRepaint()
    if False:
        iface.layerTreeView().refreshLayerSymbology(layer.id())
        iface.layerTreeView().layerTreeModel().refreshLayerLegend(
            QgsProject.instance().layerTreeRoot().findLayer(layer.id())
        )
        # iface.layerTreeView().layerTreeModel().recursivelyEmitDataChanged()


def set_symbol_styling(
    color_iter, opacity: float, outline_only: bool, outline_width: float, sym: Any
) -> None:
    col = next(color_iter)
    if len(col) == 3:
        col = (*col, 255)
    if outline_only:
        outline_symbol_layer = QgsSimpleFillSymbolLayer()
        outline_symbol_layer.setColor(QColor("transparent"))
        outline_symbol_layer.setStrokeWidth(outline_width)
        outline_symbol_layer.setStrokeColor(QColor(*col))
        sym.changeSymbolLayer(0, outline_symbol_layer)
    else:
        sym.setColor(QColor(*col))
    sym.setOpacity(opacity)
