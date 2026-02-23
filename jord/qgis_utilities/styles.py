from pathlib import Path

__all__ = ["add_xml_style"]

from typing import Any


def add_xml_style(iface: Any, path: Path = "styles/my_directional_lines.xml") -> None:
    """

    :param iface:
    :type iface:
    :param path:
    :type path:
    """
    from qgis.core import QgsStyle

    if not isinstance(path, Path):
        path = Path(path)

    qstyles = QgsStyle.defaultStyle()
    qstyles.importXml(str(path))
    # qstyles.addFavorite(QgsStyle.StyleEntity.SymbolEntity, 'Snake')

    before = qstyles.symbolNames()
    qstyles.importXml("mycompanystyles.xml")
    after = qstyles.symbolNames()
    mystyles = list(set(after) - set(before))
    for s in mystyles:
        qstyles.addFavorite(QgsStyle.StyleEntity.SymbolEntity, s)

    layer = iface.activeLayer()
    qstyles = QgsStyle.defaultStyle()
    style = qstyles.symbol("Snake")
    layer.renderer().setSymbol(style)
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
