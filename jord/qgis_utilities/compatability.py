from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLineEdit

__all__ = [
    "yes_button",
    "no_button",
    "help_button",
    "accept_role",
    "reject_role",
    "echo_mode",
    "horizontal_orientation",
    "window_stays_on_top_hint",
    "item_is_enabled",
    "item_is_selectable",
    "item_is_user_checkable",
    "checked_state",
    "unchecked_state",
    "partially_checked_state",
    "align_center",
    "align_left",
    "align_right",
    "vertical_orientation",
    "message_box_warning",
    "normal_font_weight",
    "normal_font_style",
    "cancel_button",
    "ok_button",
]

__doc__ = (
    """Provides compatibility between different PyQt versions (often PyQt5 vs PyQt6)"""
)

try:
    yes_button = QtWidgets.QMessageBox.Yes
    no_button = QtWidgets.QMessageBox.No
    help_button = QtWidgets.QMessageBox.Help
    cancel_button = QtWidgets.QMessageBox.Cancel
    ok_button = QtWidgets.QMessageBox.Ok


except AttributeError:
    yes_button = QtWidgets.QMessageBox.StandardButton.Yes
    no_button = QtWidgets.QMessageBox.StandardButton.No
    help_button = QtWidgets.QMessageBox.StandardButton.Help
    cancel_button = QtWidgets.QMessageBox.StandardButton.Cancel
    ok_button = QtWidgets.QMessageBox.StandardButton.Ok


try:
    message_box_warning = QtWidgets.QMessageBox.Warning
except AttributeError:
    message_box_warning = QtWidgets.QMessageBox.Icon.Warning


try:
    accept_role = QtWidgets.QMessageBox.ButtonRole.AcceptRole
    reject_role = QtWidgets.QMessageBox.ButtonRole.RejectRole
except AttributeError:
    accept_role = QtWidgets.QMessageBox.AcceptRole
    reject_role = QtWidgets.QMessageBox.RejectRole

try:
    echo_mode = QLineEdit.EchoMode.Password
except AttributeError:
    echo_mode = QLineEdit.Password

try:
    horizontal_orientation = Qt.Orientation.Horizontal
    vertical_orientation = Qt.Orientation.Vertical

except AttributeError:
    horizontal_orientation = Qt.Horizontal
    vertical_orientation = Qt.Vertical

try:
    window_stays_on_top_hint = Qt.WindowType.WindowStaysOnTopHint
except AttributeError:
    window_stays_on_top_hint = Qt.WindowStaysOnTopHint

try:
    checked_state = Qt.CheckState.Checked
    unchecked_state = Qt.CheckState.Unchecked
    partially_checked_state = Qt.CheckState.PartiallyChecked
except AttributeError:
    checked_state = Qt.Checked
    unchecked_state = Qt.Unchecked
    partially_checked_state = Qt.PartiallyChecked

try:
    item_is_enabled = Qt.ItemFlag.ItemIsEnabled
    item_is_selectable = Qt.ItemFlag.ItemIsSelectable
    item_is_user_checkable = Qt.ItemFlag.ItemIsUserCheckable
except AttributeError:
    item_is_enabled = Qt.ItemIsEnabled
    item_is_selectable = Qt.ItemIsSelectable
    item_is_user_checkable = Qt.ItemIsUserCheckable

try:
    align_center = Qt.AlignmentFlag.AlignCenter
    align_left = Qt.AlignmentFlag.AlignLeft
    align_right = Qt.AlignmentFlag.AlignRight
except AttributeError:
    align_center = Qt.AlignCenter
    align_left = Qt.AlignLeft
    align_right = Qt.AlignRight


try:
    normal_font_weight = QtGui.QFont.Normal
    normal_font_style = QtGui.QFont.StyleNormal
except AttributeError:
    normal_font_weight = QtGui.QFont.Weight.Normal
    normal_font_style = QtGui.QFont.Style.StyleNormal
