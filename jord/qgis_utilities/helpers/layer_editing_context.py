import contextlib
import logging
from typing import Any

_logger = logging.getLogger(__name__)

__all__ = ["LayerEditingContext"]

__doc__ = """
LayerEditingContext
=================

"""


class LayerEditingContext(contextlib.AbstractContextManager):
    """
    Context manager for safely editing a QGIS layer. It ensures that if an exception occurs during the editing process, all changes are rolled back to maintain data integrity. If no exceptions occur, changes are committed properly.
    """

    def __init__(self, context_message: str, layer: Any):
        self._context_message = context_message
        self._layer = layer
        self._was_editing = False

    def __enter__(self):
        _logger.info(
            f"Starting {self._context_message} context for layer {self._layer.name()}"
        )

        if self._layer.isEditable():
            self._layer.beginEditCommand(self._context_message)
            self._was_editing = True
        else:
            self._layer.startEditing()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # An exception was thrown, rollback changes
            self._layer.rollBack(stopEditing=True)
            _logger.warning(
                f"Exception occurred during {self._context_message}, rolling back changes",
                exc_info=(exc_type, exc_val, exc_tb),
            )
        elif self._was_editing:
            self._layer.endEditCommand()
        else:
            self._layer.commitChanges(stopEditing=True)

        _logger.info(f"Finished {self._context_message} context")
