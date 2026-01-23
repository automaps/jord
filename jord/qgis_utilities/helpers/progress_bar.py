__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

# noinspection PyUnresolvedReferences
from qgis.PyQt import QtWidgets
from typing import Any, Optional, Tuple
from warg import AlsoDecorator, passes_kws_to

from jord.qt_utilities import WindowModalityEnum

__all__ = [
    "make_dialog_progress_bar",
    "DialogProgressBar",
    "make_progress_bar",
    "InjectedProgressBar",
]


def make_progress_bar(
    *,
    progress: int = 0,
    min_value: int = 0,
    max_value: int = 100,
    parent: Optional[Any] = None
) -> QtWidgets.QProgressBar:
    bar = QtWidgets.QProgressBar(parent)
    bar.setTextVisible(True)
    bar.setValue(min_value)
    bar.setValue(progress)
    bar.setMaximum(max_value)
    return bar


def make_dialog_progress_bar(
    *,
    progress: int = 0,
    minimum_width: int = 300,
    min_value: int = 0,
    max_value: int = 100,
    title: str = "Progress",
    label: str = "",
    parent: Optional[Any] = None
) -> Tuple[QtWidgets.QDialog, QtWidgets.QProgressBar]:
    """
    Create a progress bar dialog.

    :param parent:
    :param title:
    :param label:
    :param min_value:
    :param max_value:
    :param progress: The progress to display.
    :type progress: int
    :param minimum_width: The minimum width of the dialog.
    :type minimum_width: int
    :return: The dialog.
    :rtype: Tuple[QtWidgets.QDialog, QtWidgets.QProgressBar]
    """
    dialog = QtWidgets.QProgressDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)

    bar = make_progress_bar(
        parent=dialog, progress=progress, min_value=min_value, max_value=max_value
    )

    dialog.setBar(bar)
    dialog.setMinimumWidth(minimum_width)
    dialog.setWindowModality(WindowModalityEnum.window.value)

    return dialog, bar


class DialogProgressBar(AlsoDecorator):  # TODO This freezes!

    # TODO Make it formatable with a unit or a title
    # self.progressBar.setFormat(f"{hms} - %p%")
    @passes_kws_to(make_dialog_progress_bar)
    def __init__(self, **kwargs):
        (self._progress_dialog, self._progress_bar) = make_dialog_progress_bar(**kwargs)

    def __enter__(self):
        if self._progress_dialog:
            # self._progress_dialog.forceShow()?
            self._progress_dialog.show()
            # time.sleep(0.2)  # WAIT FOR IT TO BE RENDERED?
            # self._progress_dialog.exec_() # RUN IT?
        return self._progress_bar

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._progress_dialog:
            self._progress_dialog.close()


class InjectedProgressBar(AlsoDecorator):

    @passes_kws_to(make_progress_bar)
    def __init__(self, **kwargs):
        self._parent = kwargs.pop("parent", None)
        self._progress_bar = make_progress_bar(**kwargs)

    def __enter__(self):
        if self._parent:
            self._parent.addWidget(self._progress_bar)
        return self._progress_bar

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._parent:
            self._parent.removeWidget(self._progress_bar)


if __name__ == "__main__":

    def calc(x, y):
        from time import sleep

        dialog, bar = make_dialog_progress_bar(0)
        bar.setValue(0)
        bar.setMaximum(100)
        sum_ = 0
        for i in range(x):
            for j in range(y):
                k = i + j
                sum_ += k
            i += 1
            bar.setValue((float(i) / float(x)) * 100)
            sleep(0.1)
        print(sum_)

    # calc(10000, 2000)
