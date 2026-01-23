import logging

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtCore import pyqtSignal
from typing import Optional

__author__ = "Christian Heider Lindbjerg"
__doc__ = r"""

           Created on 02-12-2020
           """

__all__ = ["disconnect_signal", "connect_signal", "reconnect_signal"]

IS_DEBUGGING = False

_logger = logging.getLogger(__name__)


def connect_signal(signal: pyqtSignal, new_handler: Optional[callable] = None) -> None:
    """

    :param signal:
    :param new_handler:
    :return:
    """
    if new_handler is not None:  # if new_handler is not None, connect it
        signal.connect(new_handler)
    else:
        if IS_DEBUGGING:
            raise Exception("new_handler is None")
        _logger.warning("new_handler is None")


def disconnect_signal(
    signal: pyqtSignal, old_handler: Optional[callable] = None
) -> None:
    """

    :param signal:
    :param old_handler:
    :return:
    """
    if signal is not None:
        try:
            if old_handler is not None:  # disconnect old_handler(s)
                while True:
                    # the loop is needed for safely disconnecting a specific handler,
                    # because it may have been connected multple times,
                    # and disconnect(slot) only removes one connection at a time.
                    signal.disconnect(old_handler)
            else:  # disconnect all, only available when old_handler is None and we are debugging, as this is bad
                # practice
                if IS_DEBUGGING:
                    signal.disconnect()
        except TypeError:
            pass


def reconnect_signal(
    signal: pyqtSignal,
    new_handler: Optional[callable] = None,
    old_handler: Optional[callable] = None,
) -> None:
    """

    :param signal:
    :type signal: pyqtSignal
    :param new_handler:
    :type new_handler: Optional[callable]
    :param old_handler:
    :type old_handler: Optional[callable]
    :return:
    :rtype: None
    """
    disconnect_signal(signal, old_handler)
    connect_signal(signal, new_handler)
