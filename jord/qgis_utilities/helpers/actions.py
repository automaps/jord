# noinspection PyUnresolvedReferences
from qgis.PyQt.QtGui import QIcon

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtWidgets import QAction, QWidget
from typing import Any, Callable

from jord.qgis_utilities.helpers.signals import reconnect_signal

__all__ = ["create_action"]


def create_action(
    icon_path: str,
    text: str,
    callback: Callable,
    enabled_flag: bool = True,
    toolbar: Any = None,
    iface: Any = None,
    menu: Any = None,
    status_tip: str = None,
    whats_this: str = None,
    parent: QWidget = None,
) -> QAction:
    """Action creation factory

    Add a toolbar icon to the toolbar.

      :param icon_path: Path to the icon for this action. Maybe a resource
          path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
      :type icon_path: Str

      :param text: Text that should be shown in menu items for this action.
      :type text: Str

      :param callback: Function to be called when the action is triggered.
      :type callback: Callable

      :param enabled_flag: A flag indicating if the action should be enabled
          by default. Defaults to True.
      :type enabled_flag: Bool

      :param toolbar: Flag indicating whether the action should also
          be added to the menu. Defaults to True.
      :type toolbar: Any

      :param iface: Flag indicating whether the action should also
          be added to the toolbar. Defaults to True.
      :type iface: Any

      :param menu: Flag indicating whether the action should also
          be added to the toolbar. Defaults to True.
      :type menu: Any

      :param status_tip: Optional text to show in a popup when the mouse pointer hovers over the action.
      :type status_tip: Str

      :param parent: Parent widget for the new action. Defaults None.
      :type parent: QWidget

      :param whats_this: Optional text to show in the status bar when the
          mouse pointer hovers over the action.

      :returns: The action that was created. Note that the action is also
          added to .actions list.
      :rtype: QAction
    """

    icon = QIcon(icon_path)
    action = QAction(icon, text, parent)
    reconnect_signal(action.triggered, callback)
    action.setEnabled(enabled_flag)

    if status_tip is not None:
        action.setStatusTip(status_tip)

    if whats_this is not None:
        action.setWhatsThis(whats_this)

    if toolbar:
        toolbar.addAction(action)

    if iface:
        assert menu
        iface.addPluginToMenu(menu, action)

    return action
