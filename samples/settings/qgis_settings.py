__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

from typing import Any

__all__ = ["add_settings"]


from qgis.core import QgsProject, QgsSettings, QgsVectorLayer


def global_settings(name: str) -> None:
    """

    :param name:
    :type name:
    """

    def store():
        """ """
        s = QgsSettings()
        s.setValue("myplugin/mytext", "hello world")
        s.setValue("myplugin/myint", 10)
        s.setValue("myplugin/myreal", 3.14)

    def read():
        """ """
        s = QgsSettings()
        mytext = s.value("myplugin/mytext", "default text")
        myint = s.value("myplugin/myint", 123)
        myreal = s.value("myplugin/myreal", 2.71)
        nonexistent = s.value("myplugin/nonexistent", None)
        print(mytext)
        print(myint)
        print(myreal)
        print(nonexistent)


def projects_settings(name: str) -> None:
    """

    :param name:
    :type name:
    """
    proj = QgsProject.instance()

    # store values
    proj.writeEntry("myplugin", "mytext", "hello world")
    proj.writeEntry("myplugin", "myint", 10)
    proj.writeEntryDouble("myplugin", "mydouble", 0.01)
    proj.writeEntryBool("myplugin", "mybool", True)

    # read values (returns a tuple with the value, and a status boolean
    # which communicates whether the value retrieved could be converted to
    # its type, in these cases a string, an integer, a double and a boolean
    # respectively)

    mytext, type_conversion_ok = proj.readEntry("myplugin", "mytext", "default text")
    myint, type_conversion_ok = proj.readNumEntry("myplugin", "myint", 123)
    mydouble, type_conversion_ok = proj.readDoubleEntry("myplugin", "mydouble", 123)
    mybool, type_conversion_ok = proj.readBoolEntry("myplugin", "mybool", 123)


def vector_layer_settings(name: str) -> None:
    """

    :param name:
    :type name:
    """
    vlayer = QgsVectorLayer()
    # save a value
    vlayer.setCustomProperty("mytext", "hello world")

    # read the value again (returning "default text" if not found)
    mytext = vlayer.customProperty("mytext", "default text")


def add_settings(settings, key: str, value: Any) -> None:
    """

    :param settings:
    :type settings:
    :param key:
    :type key:
    :param value:
    :type value:
    """
    if settings is None:
        settings = QgsSettings()
    settings.beginGroup("PostgreSQL/connections")
    # self.cmb_db_connections.addItem('------------')
    # self.cmb_db_connections.addItems(settings.childGroups())
    settings.endGroup()
