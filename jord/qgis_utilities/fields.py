import logging
from enum import Enum, IntEnum

# noinspection PyUnresolvedReferences
from qgis.core import (
    QgsDefaultValue,
    QgsDefaultValue,
    QgsEditorWidgetSetup,
    QgsEditorWidgetSetup,
    QgsFieldConstraints,
    QgsFieldConstraints,
    QgsMapLayer,
)
from typing import Any, Iterable, Mapping, Sequence, Type

from jord.qgis_utilities.helpers.widgets import (
    CHECKBOX_WIDGET,
    NULLABLE_CHECKBOX_WIDGET,
    UNIQUE_VALUES_WIDGET,
)

__all__ = [
    "set_field_widget",
    "make_field_unique",
    "make_field_not_null",
    "make_field_default",
    "make_field_boolean",
    "make_field_reuse_last_entered_value",
    "make_value_relation_widget",
    "make_enum_dropdown_widget",
    "make_iterable_dropdown_widget",
    "make_sorted_mapping_dropdown_widget",
    "make_value_map_widget",
    "make_field_datetime",
    "make_field_readonly",
    "make_external_resource_widget",
]


class DocumentViewerEnum(IntEnum):
    no_content = 0
    image = 1
    audio = 2
    video = 3
    web_view = 4


AUTO_DIMENSION = 0

ABSOLUTE_PATH = 0
RELATIVE_PATH = 1

FILE_PATHS = 0
DIRECTORY_PATHS = 1

IGNORE_THIS_STRING = """

Line edit – a simple edit box
Classification – displays a combo box with the values used for “unique value” classification (symbology tab)
Range – allows numeric values within a given range, the widget can be either slider or spin box
Unique values
    editable – displays a line edit widget with auto-completion suggesting values already used in the
    attribute table
    not editable – displays a combo box with already used values
File name – adds a file chooser dialog
Value map – shows a combo box with predefined description/value items
Enumeration – a combo box with values that can be used within the columns type
Immutable – read-only
Hidden – makes the attribute invisible for the user
CheckBox – a checkbox with customizable representation for both checked and unchecked state
Text edit – an edit box that allow multiple input lines
Calendar – a calendar widget to input dates
"""

IGNORE_THIS_STRING2 = """
QGIS Widget Types
_________________

Binary

Checkbox

Classification

Color

DateTime

Enumeration

Attachment

Geometry

Hidden

JsonView

KeyValue

List

Range

RelationReference

TextEdit

UniqueValues

UuidGenerator

ValueMap

ValueRelation

"""

_logger = logging.getLogger(__name__)


def set_field_widget(layers: Any, field_name: str, form_widget: Any) -> None:
    """
    https://gis.stackexchange.com/questions/470963/setting-dropdown-on-feature-attribute-form-using-plugin


    :param layers:
    :param field_name:
    :param form_widget:
    :return:
    """

    if layers is None:
        return

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layer in layers_inner:
                    if layer:
                        idx = layer.fields().indexFromName(field_name)
                        if idx < 0:
                            continue
                        layer.setEditorWidgetSetup(
                            idx,
                            form_widget,
                        )
            else:
                idx = layers_inner.fields().indexFromName(field_name)
                if idx < 0:
                    continue
                layers_inner.setEditorWidgetSetup(
                    idx,
                    form_widget,
                )


def make_field_unique(
    layers: Sequence[Any], *, field_name: str = "id", auto_generate: bool = True
) -> None:
    """

    :param layers:
    :param field_name:
    :param auto_generate:
    :return:
    """
    if layers is None:
        return

    unique_widget = None
    default_value_generator = None

    if False:
        unique_widget = QgsEditorWidgetSetup(
            "UuidGenerator",
            {},
        )
        if False:
            _logger.error(unique_widget.config())
    elif auto_generate:
        default_value_generator = QgsDefaultValue()
        default_value_generator.setExpression("rtrim( ltrim( uuid(), '{'), '}')")
    else:
        unique_widget = UNIQUE_VALUES_WIDGET

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layer in layers_inner:
                    if layer:
                        idx = layer.fields().indexFromName(field_name)
                        if idx < 0:
                            continue

                        if unique_widget:
                            layer.setEditorWidgetSetup(
                                idx,
                                unique_widget,
                            )
                        elif default_value_generator:
                            layer.setDefaultValueDefinition(
                                idx, default_value_generator
                            )
                        else:
                            raise NotImplementedError

                        layer.setFieldConstraint(
                            idx, QgsFieldConstraints.ConstraintNotNull
                        )
                        layer.setFieldConstraint(
                            idx, QgsFieldConstraints.ConstraintUnique
                        )
            else:
                idx = layers_inner.fields().indexFromName(field_name)

                if idx < 0:
                    continue

                if unique_widget:
                    layers_inner.setEditorWidgetSetup(
                        idx,
                        unique_widget,
                    )
                elif default_value_generator:
                    layers_inner.setDefaultValueDefinition(idx, default_value_generator)
                else:
                    raise NotImplementedError

                layers_inner.setFieldConstraint(
                    idx, QgsFieldConstraints.ConstraintNotNull
                )
                layers_inner.setFieldConstraint(
                    idx, QgsFieldConstraints.ConstraintUnique
                )


def make_field_not_null(layers: Sequence[Any], field_name: str = "name") -> None:
    """

    :param layers:
    :param field_name:
    :return:
    """
    if layers is None:
        return

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layers in layers_inner:
                    if layers:
                        idx = layers.fields().indexFromName(field_name)
                        if idx < 0:
                            continue

                        layers.setFieldConstraint(
                            idx, QgsFieldConstraints.ConstraintNotNull
                        )
            else:
                idx = layers_inner.fields().indexFromName(field_name)
                if idx < 0:
                    continue
                layers_inner.setFieldConstraint(
                    idx, QgsFieldConstraints.ConstraintNotNull
                )


def make_field_default(
    layers: Sequence[Any], field_name: str, default_expression: str = "'None'"
) -> None:
    """

    :param layers:
    :param field_name:
    :param default_expression:
    :return:
    """
    if layers is None:
        return

    default_value = QgsDefaultValue()
    default_value.setExpression(default_expression)

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layers in layers_inner:
                    if layers:
                        layers.setDefaultValueDefinition(
                            layers.fields().indexFromName(field_name), default_value
                        )
            else:
                layers_inner.setDefaultValueDefinition(
                    layers_inner.fields().indexFromName(field_name), default_value
                )


def make_field_boolean(
    layers: Sequence[Any], field_name: str, nullable: bool = True
) -> None:
    """

    :param nullable:
    :param layers:
    :param field_name:
    :return:
    """
    if layers is None:
        return

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layer in layers_inner:
                    if layer:
                        idx = layer.fields().indexFromName(field_name)

                        if idx < 0:
                            continue

                        layer.setEditorWidgetSetup(
                            idx,
                            NULLABLE_CHECKBOX_WIDGET if nullable else CHECKBOX_WIDGET,
                        )
            else:
                idx = layers_inner.fields().indexFromName(field_name)

                if idx < 0:
                    continue

                layers_inner.setEditorWidgetSetup(
                    idx,
                    NULLABLE_CHECKBOX_WIDGET if nullable else CHECKBOX_WIDGET,
                )


def make_field_reuse_last_entered_value(layers: Sequence[Any], field_name: str) -> None:
    """

    :param layers:
    :param field_name:
    :return:
    """
    if layers is None:
        return

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layer in layers_inner:
                    if layer:
                        idx = layer.fields().indexFromName(field_name)

                        if idx < 0:
                            continue

                        layer_form_config = layer.editFormConfig()
                        layer_form_config.setReuseLastValue(idx, True)
                        layer.setEditFormConfig(layer_form_config)
            else:
                idx = layers_inner.fields().indexFromName(field_name)

                if idx < 0:
                    continue

                layer_form_config = layers_inner.editFormConfig()
                layer_form_config.setReuseLastValue(idx, True)
                layers_inner.setEditFormConfig(layer_form_config)


def fit_field_to_length(layers: Sequence[Any], field_name: str, length: int) -> None:
    """

    :param layers:
    :param field_name:
    :param length:
    :return:
    """
    if layers is None:
        return

    for layers_inner in layers:
        if layers_inner:
            if isinstance(layers_inner, Iterable):
                for layer in layers_inner:
                    if layer:
                        fields = layer.fields()

                        idx = fields.indexFromName(field_name)
                        if idx < 0:
                            continue

                        fields[idx].setLength(length)
            else:
                fields = layers_inner.fields()
                idx = fields.indexFromName(field_name)
                if idx < 0:
                    continue
                fields[idx].setLength(length)


def make_value_map_widget(mapp: Mapping[str, Any]) -> Any:
    """

    :param mapp:
    :return:
    """
    return QgsEditorWidgetSetup(
        "ValueMap",
        {"map": mapp},
    )


def make_enum_dropdown_widget(_enum: Type[Enum]) -> Any:
    """

    :param _enum:
    :return:
    """
    return make_value_map_widget(
        {
            name: _enum.__getitem__(name).value
            for name in sorted({l.name for l in _enum})
        }
    )


def make_sorted_mapping_dropdown_widget(m: Mapping[str, Any]) -> Any:
    """

    :param m:
    :return:
    """
    return make_value_map_widget({k: m[k] for k in sorted(m)})


def make_iterable_dropdown_widget(it: Iterable) -> Any:
    """

    :param it:
    :return:
    """
    return make_value_map_widget({name: name for name in sorted({l for l in it})})


def make_value_relation_widget(
    target_layer_id: str,
    *,
    target_key_field_name: str = "key",
    target_value_field_name: str = "name",
    use_completer: bool = False,
    order_by_value: bool = True,
    allow_null_values: bool = False,
    allow_multiple_values: bool = False
) -> Any:
    """
      <editWidget type="ValueRelation">
            <config>
              <Option type="Map">
                <Option value="false" type="bool" name="AllowMulti"/>
                <Option value="false" type="bool" name="AllowNull"/>
                <Option value="2" type="int" name="CompleterMatchFlags"/>
                <Option value="&quot;name&quot;" type="QString" name="Description"/>
                <Option value="true" type="bool" name="DisplayGroupName"/>
                <Option value="" type="QString" name="FilterExpression"/>
                <Option value="admin_id" type="QString" name="Group"/>
                <Option value="admin_id" type="QString" name="Key"/>
                <Option value="location_types_1743074272_2672093_6cf6edd7_a194_42b5_a1a9_8ccec987325c"
                type="QString" name="Layer"/>
                <Option value="location_types_1743074272.2672093" type="QString" name="LayerName"/>
                <Option value="memory" type="QString" name="LayerProviderName"/>
                <Option value="None?crs=EPSG:4326&amp;field=admin_id:text(255)&amp;field=name:text(
                255)&amp;index=no&amp;uid={57bd270e-08b6-4e66-8a4f-81f703d3a3a5}" type="QString"
                name="LayerSource"/>
                <Option value="1" type="int" name="NofColumns"/>
                <Option value="true" type="bool" name="OrderByValue"/>
                <Option value="true" type="bool" name="UseCompleter"/>
                <Option value="name" type="QString" name="Value"/>
              </Option>
            </config>
          </editWidget>


    :param target_layer_id:
    :param target_key_field_name:
    :param target_value_field_name:
    :param use_completer:
    :param order_by_value:
    :param allow_null_values:
    :param allow_multiple_values:
    :return:
    """

    return QgsEditorWidgetSetup(
        "ValueRelation",
        {
            "AllowMulti": allow_multiple_values,
            "AllowNull": allow_null_values,
            "FilterExpression": "",
            "Key": target_key_field_name,
            "Layer": target_layer_id,
            "NofColumns": 1,
            "OrderByValue": order_by_value,
            "UseCompleter": use_completer,
            "Value": target_value_field_name,
        },
    )


def make_field_datetime(layer: Any, field_name: str) -> None:
    """

    :param layer:
    :param field_name:
    :return:
    """
    config = {
        "allow_null": True,
        "calendar_popup": True,
        "display_format": "yyyy-MM-dd HH:mm:ss",
        "field_format": "yyyy-MM-dd HH:mm:ss",
        "field_iso_format": False,
    }
    type = "DateTime"
    fields = layer.fields()
    field_idx = fields.indexOf(field_name)

    widget_setup = QgsEditorWidgetSetup(type, config)
    layer.setEditorWidgetSetup(field_idx, widget_setup)
    layer.setDefaultValueDefinition(field_idx, QgsDefaultValue("now()"))


def make_field_readonly(layer: Any, field_name: str, option: bool = True) -> None:
    """

    :param layer:
    :param field_name:
    :param option:
    :return:
    """
    if layer.type() != QgsMapLayer.VectorLayer:
        return

    fields = layer.fields()
    field_idx = fields.indexOf(field_name)
    if field_idx >= 0:
        form_config = layer.editFormConfig()
        form_config.setReadOnly(field_idx, option)
        layer.setEditFormConfig(form_config)


def make_external_resource_widget(
    document_viewer: DocumentViewerEnum = DocumentViewerEnum.image,
    document_viewer_width: int = AUTO_DIMENSION,
    document_viewer_height: int = AUTO_DIMENSION,
) -> Any:
    """


    <editWidget type="ExternalResource">
          <config>
            <Option type="Map">
              <Option name="DocumentViewer" type="int" value="0"/>
              <Option name="DocumentViewerHeight" type="int" value="0"/>
              <Option name="DocumentViewerWidth" type="int" value="0"/>
              <Option name="FileWidget" type="bool" value="true"/>
              <Option name="FileWidgetButton" type="bool" value="true"/>
              <Option name="FileWidgetFilter" type="QString" value=""/>
              <Option name="PropertyCollection" type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
              <Option name="RelativeStorage" type="int" value="0"/>
              <Option name="StorageAuthConfigId" type="QString" value=""/>
              <Option name="StorageMode" type="int" value="0"/>
              <Option name="StorageType" type="QString" value=""/>
            </Option>
          </config>
        </editWidget>

    :param document_viewer:
    :param document_viewer_width:
    :param document_viewer_height:
    :return:
    """

    return QgsEditorWidgetSetup(
        "ExternalResource",
        {
            "FileWidget": True,
            "FileWidgetButton": True,
            "FileWidgetFilter": "",
            "DocumentViewer": document_viewer.value,
            "DocumentViewerHeight": document_viewer_height,
            "DocumentViewerWidth": document_viewer_width,
            "RelativeStorage": ABSOLUTE_PATH,
            "StorageMode": FILE_PATHS,
        },
    )


IGNORE_THIS_STRING3 = """

ews = layer.editorWidgetSetup(field_index)
print("Type:", ews.type())
print("Config:", ews.config())
"""
