__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

import numpy

# noinspection PyUnresolvedReferences
from qgis.PyQt import QtGui

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtCore import QEvent, Qt

# noinspection PyUnresolvedReferences
from qgis.gui import QgsPixmapLabel
from typing import Any

from .conversion import get_qimage_from_numpy

__all__ = ["NumpyImageWidget"]


class NumpyImageWidget(QgsPixmapLabel):
    """solely for the purpose of the maintaining the aspect ratio of the image"""

    def __init__(self, parent: Any = None):
        super().__init__(parent)
        # self.setScaledContents(True)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.setAlignment(Qt.AlignCenter)
        self.setText("Waiting for layer...")
        self.setToolTip("Waiting for layer...")
        # self.setCentralWidget(self.label)
        # self.label.adjustSize()
        # self.resize(self.pixmap.width(), self.pixmap.height())
        # self.installEventFilter(self)

    def recalculate_size(self) -> None:  # TODO: maybe reset to non scaled img
        """

        :return:
        """
        if False:
            self.pixmap = self.pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation
            )
        elif False:  #
            self.pixmap = self.pixmap.scaledToWidth(
                self.width(), mode=Qt.SmoothTransformation
            )
        elif False:  #
            self.pixmap = self.pixmap.scaledToHeight(
                self.height(), mode=Qt.SmoothTransformation
            )
        else:
            pass

        # self.setMinimumSize(img.shape[1], img.shape[0])
        # self.setMinimumSize(pixmap.width(), pixmap.height())
        # self.setMinimumSize(1,1)

        self.setPixmap(self.pixmap)

    def setImage(self, img: numpy.ndarray) -> None:
        """

        :param img:
        :return:
        """
        self.pixmap = QtGui.QPixmap.fromImage(get_qimage_from_numpy(img))
        self.recalculate_size()

    def eventFilter(self, source: Any, event: Any) -> Any:
        """

        :param source:
        :param event:
        :return:
        """
        if source is self and event.type() == QEvent.Resize:
            # print("resize")
            if False:
                if self.pixmap():
                    self.recalculate_size()
        return super().eventFilter(source, event)


if __name__ == "__main__":
    pass
