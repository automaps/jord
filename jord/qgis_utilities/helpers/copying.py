# noinspection PyUnresolvedReferences
from qgis.core import QgsFeatureRequest, QgsField, QgsFieldConstraints, QgsVectorLayer
from typing import Any

__all__ = ["deepcopy_layer"]


def deepcopy_layer(source_layer: Any) -> Any:
    new_layer = source_layer.materialize(
        QgsFeatureRequest().setFilterFids(source_layer.allFeatureIds())
    )

    # get the name of the source layer's current style
    style_name = source_layer.styleManager().currentStyle()

    # get the style by the name
    style = source_layer.styleManager().style(style_name)

    # add the style to the target layer with a custom name (in this case: 'copied')
    new_layer.styleManager().addStyle("copied", style)

    # set the added style as the current style
    new_layer.styleManager().setCurrentStyle("copied")

    # propagate the changes to the QGIS GUI
    new_layer.triggerRepaint()
    new_layer.emitStyleChanged()

    return new_layer


def deepcopy_layer_old(layer: Any) -> Any:
    new_layer = layer.materialize(
        QgsFeatureRequest().setFilterFids(layer.allFeatureIds())
    )

    if isinstance(new_layer, QgsVectorLayer):
        # Copy field configurations
        fields = new_layer.fields()
        for field_idx in range(fields.count()):
            # Create new field with constraints
            old_field = layer.fields().at(field_idx)
            new_field = QgsField(old_field)

            constraints = QgsFieldConstraints()
            old_constraints = old_field.constraints()

            # Copy constraints
            for constraint_type in (
                QgsFieldConstraints.ConstraintNotNull,
                QgsFieldConstraints.ConstraintUnique,
                QgsFieldConstraints.ConstraintExpression,
            ):
                if old_constraints.constraints() & constraint_type:
                    strength = old_constraints.constraintStrength(constraint_type)
                    constraints.setConstraint(constraint_type)
                    constraints.setConstraintStrength(constraint_type, strength)

                    if constraint_type == QgsFieldConstraints.ConstraintExpression:
                        expr = old_constraints.constraintExpression()
                        desc = old_constraints.constraintDescription()
                        constraints.setConstraintExpression(expr, desc)

            new_field.setConstraints(constraints)
            new_layer.updateFields()

            # Copy editor widget setup
            editor_widget = layer.editorWidgetSetup(field_idx)
            new_layer.setEditorWidgetSetup(field_idx, editor_widget)

            # Copy default values
            default_value = layer.defaultValueDefinition(field_idx)
            new_layer.setDefaultValueDefinition(field_idx, default_value)

        new_layer.setEditFormConfig(layer.editFormConfig())
        new_layer.geometryOptions().setGeometryChecks(
            layer.geometryOptions().geometryChecks()
        )

        # Copy labeling
        if layer.labeling():
            new_layer.setLabeling(layer.labeling().clone())
            new_layer.setLabelsEnabled(layer.labelsEnabled())

        # Copy style and symbols
        new_layer.setRenderer(layer.renderer().clone())

        # Copy layer properties
        new_layer.setBlendMode(layer.blendMode())
        new_layer.setOpacity(layer.opacity())

        # Copy attribute table configuration
        new_layer.setAttributeTableConfig(layer.attributeTableConfig())

        # Copy actions
        for action in layer.actions().actions():
            new_layer.actions().addAction(action)

        # Copy auxiliary storage
        if layer.auxiliaryLayer():
            new_layer.setAuxiliaryLayer(layer.auxiliaryLayer())

        new_layer.setFeatureBlendMode(layer.featureBlendMode())

    if False:
        for r in layer.featureRendererGenerators():
            new_layer.addFeatureRendererGenerator(r)

    return new_layer
