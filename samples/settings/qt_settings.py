__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

from typing import Any, Optional, Type

from PyQt5.QtCore import (
    QSettings,
)

__all__ = ["store_plugin_setting", "read_plugin_setting"]

from jord import PROJECT_NAME


def store_plugin_setting(key: str, value: Any) -> None:
    """ """
    QSettings().setValue(f"{PROJECT_NAME}/{key}", value)


def read_plugin_setting(
    key: str, type_hint: Optional[Type] = None, *, default_value: Any = None
) -> object:
    """ """
    if type_hint is None:
        if isinstance(default_value, str):
            return QSettings().value(f"{PROJECT_NAME}/{key}", default_value, type=str)
        return QSettings().value(f"{PROJECT_NAME}/{key}", type=type_hint)
    return QSettings().value(f"{PROJECT_NAME}/{key}", default_value)


def settings_block(key: str) -> None:
    """ """
    settings = QSettings()
    settings.beginGroup(f"/{PROJECT_NAME}/config")
    # return QSettings(f"{PROJECT_NAME}/{key}", QSettings.IniFormat)
    settings.endGroup()


if __name__ == "__main__":
    store_plugin_setting("mytext", "hello world")
    print(read_plugin_setting("mytext"))
