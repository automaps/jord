import qgis


from qgis.core import QgsProject

__all__ = ["gc_layers"]


def gc_layers() -> None:
    """ """
    registry_layers = QgsProject.instance().mapLayers().keys()
    legend_layers = [
        layer.id() for layer in qgis.utils.iface.legendInterface().layers()
    ]
    layers_to_remove = set(registry_layers) - set(legend_layers)
    QgsProject.instance().removeMapLayers(list(layers_to_remove))
