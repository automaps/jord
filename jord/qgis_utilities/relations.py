from qgis.core import (
    QgsEditorWidgetSetup,
    QgsFeatureRequest,
    QgsProject,
    QgsVectorLayer,
)


from qgis.utils import iface

__all__ = ["add_value_relation_field"]


def add_value_relation_field(
    layer: QgsVectorLayer,
    field_name: str,
    referenced_layer: QgsVectorLayer,
    key_field: str,
    value_field: str,
    allow_null: bool = True,
    allow_multi: bool = False,
    filter_expression: str = "",
) -> None:
    """
    Adds a value relation widget to a field in the layer.

    Args:
        layer: The layer containing the field to set up
        field_name: Name of the field to set up
        referenced_layer: Layer containing the values to choose from
        key_field: Field in referenced layer to use as key
        value_field: Field in referenced layer to display to user
        allow_null: Allow NULL values
        allow_multi: Allow multiple value selection
        filter_expression: Optional filter expression for referenced layer
    """
    config = {
        "AllowMulti": allow_multi,
        "AllowNull": allow_null,
        "FilterExpression": filter_expression,
        "Key": key_field,
        "Layer": referenced_layer.id(),
        "NofColumns": 1,
        "OrderByValue": False,
        "UseCompleter": False,
        "Value": value_field,
    }

    setup = QgsEditorWidgetSetup("ValueRelation", config)
    layer.setEditorWidgetSetup(layer.fields().indexOf(field_name), setup)


def highlight_relationship() -> None:
    """ """
    parent = iface.activeLayer()  # Get parent layer from the ToC

    def selectChildren(fids, foo, bar):
        """

        :param fids:
        :type fids:
        :param foo:
        :type foo:
        :param bar:
        :type bar:
        """
        relations = QgsProject.instance().relationManager().relationsByName("my_rel")
        rel = relations[0]  # Assuming we only have 1 relation named 'my_rel'
        referencingLayer = rel.referencingLayer()
        referencedLayer = rel.referencedLayer()

        request = QgsFeatureRequest().setFilterFids(fids)
        fit = referencedLayer.getFeatures(request)
        childIds = []
        for f in fit:
            it = rel.getRelatedFeatures(f)
            childIds.extend([i.id() for i in it])

        iface.mapCanvas().flashFeatureIds(referencingLayer, childIds)

    parent.selectionChanged.connect(selectChildren)


if __name__ == "__main__":
    ...
    # add_value_relation_field(      layer=my_layer,      field_name='category',
    # referenced_layer=categories_layer,      key_field='id',      value_field='name'      )
