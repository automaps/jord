__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

from typing import Any

from jord import PROJECT_NAME

__all__ = ["store_plugin_setting", "read_plugin_setting", "delete_plugin_setting"]


def store_plugin_setting(
    key: str, value: Any, *, project_name: str = PROJECT_NAME
) -> None:
    """

    :param key:
    :param value:
    :param project_name:
    :return:
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsSettings

    QgsSettings().setValue(f"{project_name}/{key}", value)


def read_plugin_setting(
    key: str, *, default_value: Any = None, project_name: str = PROJECT_NAME
) -> Any:
    """

    :param key:
    :param default_value:
    :param project_name:
    :return:
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsSettings

    return QgsSettings().value(f"{project_name}/{key}", default_value)


def delete_plugin_setting(key: str, *, project_name: str = PROJECT_NAME) -> None:
    """

    :param key:
    :param project_name:
    :return:
    """
    # noinspection PyUnresolvedReferences
    from qgis.core import QgsSettings

    QgsSettings().remove(f"{project_name}/{key}")


if __name__ == "__main__":
    store_plugin_setting("mytext", "hello world")
    print(read_plugin_setting("mytext"))
