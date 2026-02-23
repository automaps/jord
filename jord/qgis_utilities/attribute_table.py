from typing import Any, Collection

__all__ = ["set_column_visibility", "set_visible_columns"]

from jord.qgis_utilities.configuration import read_plugin_setting, store_plugin_setting


def set_column_visibility(layers: Any, column_name: str, visible: bool = False) -> None:
    """

    :param layers:
    :type layers:
    :param column_name:
    :type column_name:
    :param visible:
    :type visible:
    """
    if not isinstance(layers, Collection):
        layers = [layers]

    for layer in layers:
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name == column_name:
                column.hidden = not visible
                break

        config.setColumns(columns)
        layer.setAttributeTableConfig(config)


def set_visible_columns(layers: Any, column_names: Collection[str]) -> None:
    """

    :param layers:
    :type layers:
    :param column_names:
    :type column_names:
    """
    if not isinstance(layers, Collection):
        layers = [layers]

    for layer in layers:
        config = layer.attributeTableConfig()
        columns = config.columns()
        for column in columns:
            if column.name in column_names:
                column.hidden = True
            else:
                column.hidden = False

        config.setColumns(columns)
        layer.setAttributeTableConfig(config)


def update_column_visibility_with_defaults(
    layers: Any,
    column_names: Collection[str],
    default_visible: bool = True,
    persist_settings: bool = True,
) -> None:
    """Update column visibility with defaults for new columns.

    Args:
        layers: Single layer or collection of layers
        column_names: Names of columns to manage visibility
        default_visible: Default visibility for new columns
        persist_settings: Whether to save settings
    """
    if not isinstance(layers, Collection):
        layers = [layers]

    for layer in layers:
        config = layer.attributeTableConfig()
        columns = config.columns()
        settings_key = f"attribute_table/{layer.id()}/column_visibility"

        # Load or initialize stored visibility settings
        stored_visibility = read_plugin_setting(settings_key, default_value={})

        for column in columns:
            column_name = column.name

            if column_name in stored_visibility:
                # Use stored setting
                column.hidden = not stored_visibility[column_name]
            else:
                # Apply default for new columns
                is_visible = (
                    column_name in column_names
                    if default_visible
                    else column_name not in column_names
                )
                column.hidden = not is_visible
                stored_visibility[column_name] = is_visible

        # Save updated settings
        if persist_settings:
            store_plugin_setting(settings_key, stored_visibility)

        config.setColumns(columns)
        layer.setAttributeTableConfig(config)
