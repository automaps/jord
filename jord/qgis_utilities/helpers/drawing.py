__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """


from qgis.PyQt import QtGui


from qgis.PyQt.QtCore import Qt


from qgis.core import QgsWkbTypes


from qgis.gui import QgsMapCanvas, QgsRubberBand

__all__ = ["make_rubber_band"]


def make_rubber_band(canvas: QgsMapCanvas) -> QgsRubberBand:
    """
    Create a rubber band on the canvas.

    :param canvas: The canvas to create the rubber band on.
    :return: The rubber band.
    """
    fill_color = QtGui.QColor("white")
    fill_color.setAlphaF(0.0)

    stroke_color = QtGui.QColor("red")
    stroke_color.setAlphaF(0.65)

    rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
    rubber_band.setWidth(2)
    rubber_band.setColor(fill_color)  # fill color
    rubber_band.setStrokeColor(stroke_color)  # stroke color
    rubber_band.setLineStyle(Qt.DotLine)

    return rubber_band
