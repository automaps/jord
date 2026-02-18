from qgis.core import QgsEditorWidgetSetup

HIDDEN_WIDGET = QgsEditorWidgetSetup("Hidden", {})

CHECKBOX_WIDGET = QgsEditorWidgetSetup(
    "CheckBox",
    {"CheckedState": "True", "UncheckedState": "False", "TextDisplayMethod": 0},
)

NULLABLE_CHECKBOX_WIDGET = QgsEditorWidgetSetup(
    "CheckBox",
    {
        "CheckedState": "True",
        "UncheckedState": "False",
        "AllowNullState": True,
        "TextDisplayMethod": 0,
    },
)

UNIQUE_VALUES_WIDGET = QgsEditorWidgetSetup(
    "UniqueValues",
    {"Editable": True},
)

COLOR_WIDGET = QgsEditorWidgetSetup(
    "Color",
    {},
)


def make_range_widget(
    min_value: float = 0.0, max_value: float = 360.0, step_size: float = 0.5
) -> QgsEditorWidgetSetup:
    """

    :param min_value:
    :param max_value:
    :param step_size:
    :return:
    """
    return QgsEditorWidgetSetup(
        "Range",
        {
            "Min": min_value,
            "Max": max_value,
            "Step": step_size,
            "UseCompleter": False,
            "NofColumns": 1,
            "CompleterMatchFlags": 2,
        },
    )
