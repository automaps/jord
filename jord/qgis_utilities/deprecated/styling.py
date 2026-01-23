import logging

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

_logger = logging.getLogger(__name__)


def styled_field_value_categorised2(
    layer, style_attributes_layer, field_name="location_type"
):
    expression_str = f'represent_value("{field_name}")'

    render_categories = []
    added_categories = set()

    style_features = {f["admin_id"]: f for f in style_attributes_layer.getFeatures()}

    for ref, cat in zip(
        QgsVectorLayerUtils.getValues(layer, field_name, selectedOnly=False)[0],
        QgsVectorLayerUtils.getValues(layer, expression_str, selectedOnly=False)[0],
        strict=True,
    ):
        _logger.error(cat)

        if cat is not None and cat not in added_categories:
            sym = QgsSymbol.defaultSymbol(layer.geometryType())

            # Apply style from reference feature if available
            if ref in style_features:
                style_feature = style_features[ref]
                key = "display_rule.polygon.fillColor"
                if key in style_feature.fields().names():
                    fill_color = str(style_feature[key])
                    if "#" in fill_color:
                        _logger.error(
                            f"Set fill_color {fill_color} for {cat} in layer {layer.id()}"
                        )
                        sym.setColor(QColor(fill_color))
                    else:
                        _logger.error(
                            f"Did not set fill_color for {cat} in layer {layer.id()}"
                        )

            render_categories.append(
                QgsRendererCategory(ref, symbol=sym, label=cat, render=True)
            )
            added_categories.add(cat)

    sym = QgsSymbol.defaultSymbol(layer.geometryType())
    render_categories.append(
        QgsRendererCategory("", symbol=sym, label="default", render=True)
    )

    rendered = QgsCategorizedSymbolRenderer(field_name, render_categories)

    # rendered.setClassAttribute(expression_str)
    # rendered.rebuildHash()

    # rendered.matchToSymbols()

    layer.setRenderer(rendered)
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

    if False:  # TODO: DOES NOT WORK
        # Add this to update category counts
        layer_tree_layer = (
            iface.layerTreeView().layerTreeModel().rootGroup().findLayer(layer)
        )
        if layer_tree_layer:
            layer_tree_layer.setCustomProperty("showFeatureCount", True)
            iface.layerTreeView().layerTreeModel().refreshLayerLegend(layer_tree_layer)


def expression_field_value_categorised_do_not_use(layer, field_name="location_type"):
    expression_str = f'represent_value("{field_name}")'

    # expression = QgsExpression(expression_str)
    # context = QgsExpressionContext()

    # context.appendScope(QgsExpressionContextUtils.globalScope())
    # context.appendScope(QgsExpressionContextUtils.projectScope(QgsProject.instance()))
    # context.appendScope(QgsExpressionContextUtils.atlasScope(None))

    # context.appendScope(QgsExpressionContextUtils.layerScope(layer))
    # context.appendScope(QgsExpressionContextUtils.layerScope(reference_layer))

    render_categories = []
    added_categories = set()

    # for feature in layer.getFeatures(QgsFeatureRequest(expression)):
    # feature_iterator = QgsVectorLayerUtils.getValuesIterator(layer, expression_str, selectedOnly=False)
    # while feature_iterator.isValid():
    # cat = QgsFeature()
    # feature_iterator.nextFeature(cat)

    for cat in QgsVectorLayerUtils.getValues(layer, expression_str, selectedOnly=False)[
        0
    ]:
        _logger.error(cat)

        if cat is not None and cat not in added_categories:
            sym = QgsSymbol.defaultSymbol(layer.geometryType())

            # context.setFeature(feature)

            # context.setFeature(QgsFeature())
            # context.lastScope().setVariable(field_name, cat)

            # label = expression.evaluate(context)

            # if expression.hasEvalError():
            #  logger.error(f"Expression evaluation error: {expression.evalErrorString()} {label}")

            render_categories.append(
                QgsRendererCategory(cat, symbol=sym, label=cat, render=True)
            )
            added_categories.add(cat)

    rendered = QgsCategorizedSymbolRenderer(expression_str, render_categories)
    layer.setRenderer(rendered)
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
