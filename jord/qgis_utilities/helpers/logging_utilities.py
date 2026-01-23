from pathlib import Path

import logging
import os
import sys

# noinspection PyUnresolvedReferences
from qgis.core import Qgis, QgsMessageLog
from typing import Any, Optional

__all__ = ["setup_qgs_logger", "add_logging_handler_once", "QgsLogHandler", "level_map"]

level_map = {
    logging.NOTSET: Qgis.MessageLevel.NoLevel,  # Qgis.MessageLevel.NoLevel
    # 0 When set on a logger, indicates that ancestor loggers are to be consulted to determine the effective
    # level. If that still resolves to NOTSET, then all events are logged. When set on a handler, all events
    # are handled.
    logging.DEBUG: Qgis.MessageLevel.Info,  # Qgis.MessageLevel.Info
    # 10 Detailed information, typically only of interest to a developer trying to diagnose a problem.
    logging.INFO: Qgis.MessageLevel.Info,  # Qgis.MessageLevel.Info  #Qgis.MessageLevel.Success
    # 20 Confirmation that things are working as expected.
    logging.WARNING: Qgis.MessageLevel.Warning,  # Qgis.MessageLevel.Warning
    # 30 An indication that something unexpected happened, or that a problem might occur in the near future
    # (e.g. ‘disk space low’). The software is still working as expected.
    logging.ERROR: Qgis.MessageLevel.Critical,  # Qgis.MessageLevel.Critical
    # 40 Due to a more serious problem, the software has not been able to perform some function.
    logging.CRITICAL: Qgis.MessageLevel.Critical,  # Qgis.MessageLevel.Critical
    # 50 A serious error, indicating that the program itself may be unable to continue running.}
}


class QgsLogHandler(logging.Handler):
    """A logging handler that will log messages to the QGIS logging console."""

    def __init__(
        self, tag_name, iface: Optional[Any] = None, level: int = logging.NOTSET
    ):
        self.tag_name = tag_name
        self.iface = iface
        super().__init__(level=level)

    def emit(self, record: logging.LogRecord) -> None:
        """Try to log the message to QGIS if available, otherwise do nothing.

        :param record: logging message containing whatever info needs to be
                logged.
        :type record: str
        """

        push = False

        level = level_map[record.levelno]
        if self.iface:
            push = True

        message = f"{record.name}({record.lineno}): {record.getMessage()}"

        QgsMessageLog.logMessage(
            message=message, tag=self.tag_name, notifyUser=push, level=level
        )

        # optionally, display message on QGIS Message bar (above the map canvas)
        if push and level >= logging.WARNING:
            self.iface.messageBar().pushMessage(
                title=self.tag_name,
                text=message,
                level=level,
                duration=(level + 1) * 3,
            )


def add_logging_handler_once(logger: logging.Logger, handler: logging.Handler) -> bool:
    """A helper to add a handler to a logger, ensuring there are no duplicates.

    :param logger: Logger that should have a handler added.
    :type logger: logging.logger

    :param handler: Handler instance to be added. It will not be added if an
        instance of that Handler subclass already exists.
    :type handler: logging.Handler

    :returns: True if the logging handler was added, otherwise False.
    :rtype: bool
    """
    class_name = handler.__class__.__name__

    for handler_ in logger.handlers:
        if handler_.__class__.__name__ == class_name:
            return False

    logger.addHandler(handler)
    return True


def setup_qgs_logger(
    logger_name: str,
    *,
    iface: Optional[Any] = None,
    sentry_url: Optional[str] = None,
    log_file: Optional[Path] = None,
    logger_level: int = logging.INFO,
    default_handler_level=logging.DEBUG,
) -> logging.Logger:
    """Run once when the module is loaded and enable logging.

    :param default_handler_level:
    :param logger_level:
    :param iface:
    :param logger_name:
    :param sentry_url: Mandatory url to sentry api for remote logging.
        Consult your sentry instance for the client instance url.
    :type sentry_url: str

    :param log_file: Optional full path to a file to write logs to.
    :type log_file: str

    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html

    Use this to first initialise the logger in your __init__.py::

       import custom_logging
       custom_logging.setup_qgs_logger('http://path to sentry')

    You would typically only need to do the above once ever as the
    safe model is initialised early and will set up the logger
    globally so it is available to all packages / subpackages as
    shown below.

    In a module that wants to do logging then use this example as
    a guide to get the initialised logger instance::

       # The LOGGER is initialised in utilities.py by init
       import logging
       LOGGER = logging.getLogger('QGIS')

    Now to log a message do::

       LOGGER.debug('Some debug message')

    .. note:: The file logs are written to the user tmp dir e.g.:
       /tmp/23-08-2012/timlinux/logs/qgis.log

    """
    if True:  # remove all handlers associated with the root logger object, QGIS
        for h in logging.root.handlers:
            logging.root.removeHandler(h)

    logger = logging.getLogger(logger_name)

    # logger.handlers.clear()  # TODO: QGIS STDOUT logging seems to not work
    # logger.handlers = [     h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
    logger.setLevel(logger_level)

    # create formatter that will be added to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    qgis_handler = QgsLogHandler(logger_name, iface=iface, level=default_handler_level)
    # qgis_handler.setLevel(default_handler_level)
    qgis_handler.setFormatter(formatter)
    add_logging_handler_once(logger, qgis_handler)

    if False:
        # create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(default_handler_level)
        console_handler.setFormatter(formatter)
        add_logging_handler_once(logger, console_handler)

    if log_file:
        # create syslog handler which logs even debug messages
        if not isinstance(log_file, Path):
            log_file = Path(log_file)

        assert log_file.is_file()

        file_handler = logging.FileHandler(str(log_file))
        file_handler.setLevel(default_handler_level)
        file_handler.setFormatter(formatter)
        add_logging_handler_once(logger, file_handler)

    if False:
        # Sentry handler - this is optional hence the localised import
        # It will only log if pip install raven. If raven is available
        # logging messages will be sent to the sentry host.
        # We will only log exceptions.
        # Enable the 'plugins/use_sentry' QgsSettings option
        # before this will be enabled.
        # noinspection PyUnresolvedReferences
        from qgis.core import QgsSettings

        settings = QgsSettings()
        app = "some_app"
        flag = settings.value(
            key=f"{app}/sentry-logging", defaultValue=False, type=bool
        )

        if flag:
            third_party_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "third_party")
            )
            if third_party_path not in sys.path:
                sys.path.append(third_party_path)
            # noinspection PyUnresolvedReferences
            from raven.handlers.logging import (
                SentryHandler,
            )  # Deprecated for  https://github.com/getsentry/sentry-python

            # noinspection PyUnresolvedReferences
            from raven import Client

            client = Client(sentry_url)
            sentry_handler = SentryHandler(client)
            sentry_handler.setFormatter(formatter)
            sentry_handler.setLevel(default_handler_level)
            if add_logging_handler_once(logger, sentry_handler):
                logger.debug("Sentry logging enabled")
        else:
            logger.debug("Sentry logging disabled")

    return logger


IGNORE = """

from qgis.core import QgsNetworkAccessManager, QgsMessageLog, Qgis, QgsApplication
import os, logging

LOGDIR = os.path.dirname(os.path.realpath(__file__))
LOGFILE = os.path.join(LOGDIR, 'log.txt')

def setupLogger(logfile):
    logger = logging.getLogger('logger')
    if (logger.hasHandlers()):
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    logger.setLevel(logging.DEBUG)
    fileHandler = logging.FileHandler(logfile)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger

logger = setupLogger(LOGFILE)

# Map received messages to logger
def write_log_message(message, tag, level):
    if level == Qgis.Warning:
        logger.warning(message)
    elif level == Qgis.Critical:
        logger.error(message)
    else:
        logger.info(message)

# Connect the message received signal to the utility function
QgsApplication.messageLog().messageReceived.connect(write_log_message)

"""
