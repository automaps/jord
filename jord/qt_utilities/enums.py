from enum import Enum
from typing import Any

__all__ = [
    "DockWidgetAreaFlag",
    "KeyEnum",
    "INT_TO_CHECK_STATE",
    "CHECK_STATE_TO_INT",
    "check_state_to_bool",
    "str_to_check_state",
    "check_state_to_str",
    "CheckStateEnum",
    "EdgeFlag",
    "DropActionFlag",
    "FocusPolicyFlag",
    "FocusReasonEnum",
    "ColorEnum",
    "WindowModalityEnum",
    # "AlignmentFlag",
]

try:
    from PyQt6.QtCore import Qt

    class AlignmentFlag(Enum):
        """
        Alignment
        """

        left = Qt.AlignmentFlag.AlignLeft
        right = Qt.AlignmentFlag.AlignRight
        bottom = Qt.AlignmentFlag.AlignBottom
        top = Qt.AlignmentFlag.AlignTop
        center = Qt.AlignmentFlag.AlignCenter
        horizontal_center = Qt.AlignmentFlag.AlignHCenter
        vertical_center = Qt.AlignmentFlag.AlignVCenter

    class WindowModalityEnum(Enum):
        """

        PySide2.QtCore.Qt.WindowModality¶
        This enum specifies the behavior of a modal window. A modal window is one that blocks input to other
        windows. Note that windows that are children of a modal window are not blocked.

        The values are:

        Constant

        Description

        Qt.NonModal

        The window is not modal and does not block input to other windows.

        Qt.WindowModal

        The window is modal to a single window hierarchy and blocks input to its parent window, all grandparent
        windows, and all siblings of its parent and grandparent windows.

        Qt.ApplicationModal

        The window is modal to the application and blocks input to all windows."""

        non_modal = Qt.WindowModality.NonModal
        application = Qt.WindowModality.ApplicationModal
        window = Qt.WindowModality.WindowModal

    class DockWidgetAreaFlag(Enum):
        left = (
            Qt.DockWidgetArea.LeftDockWidgetArea
        )  # 0x1	The left dock area of a QMainWindow.
        right = (
            Qt.DockWidgetArea.RightDockWidgetArea
        )  # 0x2	The right dock area of a QMainWindow.
        top = (
            Qt.DockWidgetArea.TopDockWidgetArea
        )  # 0x4	The top dock area of a QMainWindow.
        bottom = (
            Qt.DockWidgetArea.BottomDockWidgetArea
        )  # 0x8	The bottom dock area of a QMainWindow.
        all = (
            Qt.DockWidgetArea.AllDockWidgetAreas
        )  # DockWidgetArea_Mask	All dock widget areas (default).
        none = Qt.DockWidgetArea.NoDockWidgetArea  # 0	No dock widget areas.

    class CheckStateEnum(Enum):
        unchecked = Qt.CheckState.Unchecked
        partial = Qt.CheckState.PartiallyChecked
        checked = Qt.CheckState.Checked

except:
    try:
        from PyQt5.QtCore import Qt
    except:

        from qgis.PyQt.QtCore import Qt

    class AlignmentFlag(Enum):
        """
        Alignment
        """

        left = Qt.AlignLeft
        right = Qt.AlignRight
        bottom = Qt.AlignBottom
        top = Qt.AlignTop
        center = Qt.AlignCenter
        horizontal_center = Qt.AlignHCenter
        vertical_center = Qt.AlignVCenter

    class WindowModalityEnum(Enum):
        """

        PySide2.QtCore.Qt.WindowModality¶
        This enum specifies the behavior of a modal window. A modal window is one that blocks input to other
        windows. Note that windows that are children of a modal window are not blocked.

        The values are:

        Constant

        Description

        Qt.NonModal

        The window is not modal and does not block input to other windows.

        Qt.WindowModal

        The window is modal to a single window hierarchy and blocks input to its parent window, all grandparent
        windows, and all siblings of its parent and grandparent windows.

        Qt.ApplicationModal

        The window is modal to the application and blocks input to all windows."""

        non_modal = Qt.NonModal
        application = Qt.ApplicationModal
        window = Qt.WindowModal

    class DockWidgetAreaFlag(Enum):
        left = Qt.LeftDockWidgetArea  # 0x1	The left dock area of a QMainWindow.
        right = Qt.RightDockWidgetArea  # 0x2	The right dock area of a QMainWindow.
        top = Qt.TopDockWidgetArea  # 0x4	The top dock area of a QMainWindow.
        bottom = Qt.BottomDockWidgetArea  # 0x8	The bottom dock area of a QMainWindow.
        all = (
            Qt.AllDockWidgetAreas
        )  # DockWidgetArea_Mask	All dock widget areas (default).
        none = Qt.NoDockWidgetArea  # 0	No dock widget areas.

    class CheckStateEnum(Enum):
        unchecked = Qt.Unchecked
        partial = Qt.PartiallyChecked
        checked = Qt.Checked


INT_TO_CHECK_STATE = {
    0: CheckStateEnum.unchecked,
    1: CheckStateEnum.partial,
    2: CheckStateEnum.checked,
}
CHECK_STATE_TO_INT = {v: k for k, v in INT_TO_CHECK_STATE.items()}


def str_to_check_state(str_: str) -> Any:
    """

    :param str_:
    :type str_:
    :return:
    :rtype:
    """
    return INT_TO_CHECK_STATE[int(str_)]


def check_state_to_str(check_state: CheckStateEnum) -> Any:
    """

    :param check_state:
    :type check_state:
    :return:
    :rtype:
    """
    return str(CHECK_STATE_TO_INT[check_state])


def check_state_to_bool(check_state: CheckStateEnum) -> bool:
    """

    :param check_state:
    :type check_state:
    :return:
    :rtype:
    """
    return CHECK_STATE_TO_INT[check_state] > 0


class DropActionFlag(Enum):
    """
      Qt::CopyAction	0x1	Copy the data to the target.
    Qt::MoveAction	0x2	Move the data from the source to the target.
    Qt::LinkAction	0x4	Create a link from the source to the target.
    Qt::ActionMask	0xff
    Qt::IgnoreAction	0x0	Ignore the action (do nothing with the data).
    Qt::TargetMoveAction	0x8002	On Windows, this value is used when the ownership of the D&D data should be
    taken over by the target application, i.e., the source application should not delete the data. On X11 this
    value is used to do a move. TargetMoveAction is not used on the Mac.

    """


class EdgeFlag(Enum):
    """
      Qt::TopEdge	0x00001	The top edge of the rectangle.
    Qt::LeftEdge	0x00002	The left edge of the rectangle.
    Qt::RightEdge	0x00004	The right edge of the rectangle.
    Qt::BottomEdge	0x00008	The bottom edge of the rectangle.

    """


class FocusPolicyFlag(Enum):
    """
      Qt::TabFocus	0x1	the widget accepts focus by tabbing.
    Qt::ClickFocus	0x2	the widget accepts focus by clicking.
    Qt::StrongFocus	TabFocus | ClickFocus | 0x8	the widget accepts focus by both tabbing and clicking. On macOS
    this will also be indicate that the widget accepts tab focus when in 'Text/List focus mode'.
    Qt::WheelFocus	StrongFocus | 0x4	like Qt::StrongFocus plus the widget accepts focus by using the mouse
    wheel.
    Qt::NoFocus	0	the widget does not accept focus.
    """


class FocusReasonEnum(Enum):
    """
      This enum specifies why the focus changed. It will be passed through QWidget::setFocus and can be
      retrieved in the QFocusEvent sent to the widget upon focus change.

    Constant	Value	Description
    Qt::MouseFocusReason	0	A mouse action occurred.
    Qt::TabFocusReason	1	The Tab key was pressed.
    Qt::BacktabFocusReason	2	A Backtab occurred. The input for this may include the Shift or Control keys;
    e.g. Shift+Tab.
    Qt::ActiveWindowFocusReason	3	The window system made this window either active or inactive.
    Qt::PopupFocusReason	4	The application opened/closed a pop-up that grabbed/released the keyboard focus.
    Qt::ShortcutFocusReason	5	The user typed a label's buddy shortcut
    Qt::MenuBarFocusReason	6	The menu bar took focus.
    Qt::OtherFocusReason	7	Another reason, usually application-specific.
    """


class ColorEnum(Enum):
    """
      Qt's predefined QColor objects:

    Constant	Value	Description
    Qt::white	3	White (#ffffff)
    Qt::black	2	Black (#000000)
    Qt::red	7	Red (#ff0000)
    Qt::darkRed	13	Dark red (#800000)
    Qt::green	8	Green (#00ff00)
    Qt::darkGreen	14	Dark green (#008000)
    Qt::blue	9	Blue (#0000ff)
    Qt::darkBlue	15	Dark blue (#000080)
    Qt::cyan	10	Cyan (#00ffff)
    Qt::darkCyan	16	Dark cyan (#008080)
    Qt::magenta	11	Magenta (#ff00ff)
    Qt::darkMagenta	17	Dark magenta (#800080)
    Qt::yellow	12	Yellow (#ffff00)
    Qt::darkYellow	18	Dark yellow (#808000)
    Qt::gray	5	Gray (#a0a0a4)
    Qt::darkGray	4	Dark gray (#808080)
    Qt::lightGray	6	Light gray (#c0c0c0)
    Qt::transparent	19	a transparent black value (i.e., QColor(0, 0, 0, 0))
    Qt::color0	0	0 pixel value (for bitmaps)
    Qt::color1	1	1 pixel value (for bitmaps)
    """


class KeyEnum(Enum):
    """
      The key names used by Qt.

    Constant	Value	Description
    Qt::Key_Escape	0x01000000
    Qt::Key_Tab	0x01000001
    Qt::Key_Backtab	0x01000002
    Qt::Key_Backspace	0x01000003
    Qt::Key_Return	0x01000004
    Qt::Key_Enter	0x01000005	Typically located on the keypad.
    Qt::Key_Insert	0x01000006
    Qt::Key_Delete	0x01000007
    Qt::Key_Pause	0x01000008	The Pause/Break key (Note: Not related to pausing media)
    Qt::Key_Print	0x01000009
    Qt::Key_SysReq	0x0100000a
    Qt::Key_Clear	0x0100000b	Corresponds to the Clear key on selected Apple keyboard models. On other systems
    it is commonly mapped to the numeric keypad key 5, when Num Lock is off.
    Qt::Key_Home	0x01000010
    Qt::Key_End	0x01000011
    Qt::Key_Left	0x01000012
    Qt::Key_Up	0x01000013
    Qt::Key_Right	0x01000014
    Qt::Key_Down	0x01000015
    Qt::Key_PageUp	0x01000016
    Qt::Key_PageDown	0x01000017
    Qt::Key_Shift	0x01000020
    Qt::Key_Control	0x01000021	On macOS, this corresponds to the Command keys.
    Qt::Key_Meta	0x01000022	On macOS, this corresponds to the Control keys. On Windows keyboards, this key is
    mapped to the Windows key.
    Qt::Key_Alt	0x01000023
    Qt::Key_AltGr	0x01001103	On Windows, when the KeyDown event for this key is sent, the Ctrl+Alt modifiers
    are also set.
    Qt::Key_CapsLock	0x01000024
    Qt::Key_NumLock	0x01000025
    Qt::Key_ScrollLock	0x01000026
    Qt::Key_F1	0x01000030
    Qt::Key_F2	0x01000031
    Qt::Key_F3	0x01000032
    Qt::Key_F4	0x01000033
    Qt::Key_F5	0x01000034
    Qt::Key_F6	0x01000035
    Qt::Key_F7	0x01000036
    Qt::Key_F8	0x01000037
    Qt::Key_F9	0x01000038
    Qt::Key_F10	0x01000039
    Qt::Key_F11	0x0100003a
    Qt::Key_F12	0x0100003b
    Qt::Key_F13	0x0100003c
    Qt::Key_F14	0x0100003d
    Qt::Key_F15	0x0100003e
    Qt::Key_F16	0x0100003f
    Qt::Key_F17	0x01000040
    Qt::Key_F18	0x01000041
    Qt::Key_F19	0x01000042
    Qt::Key_F20	0x01000043
    Qt::Key_F21	0x01000044
    Qt::Key_F22	0x01000045
    Qt::Key_F23	0x01000046
    Qt::Key_F24	0x01000047
    Qt::Key_F25	0x01000048
    Qt::Key_F26	0x01000049
    Qt::Key_F27	0x0100004a
    Qt::Key_F28	0x0100004b
    Qt::Key_F29	0x0100004c
    Qt::Key_F30	0x0100004d
    Qt::Key_F31	0x0100004e
    Qt::Key_F32	0x0100004f
    Qt::Key_F33	0x01000050
    Qt::Key_F34	0x01000051
    Qt::Key_F35	0x01000052
    Qt::Key_Super_L	0x01000053
    Qt::Key_Super_R	0x01000054
    Qt::Key_Menu	0x01000055
    Qt::Key_Hyper_L	0x01000056
    Qt::Key_Hyper_R	0x01000057
    Qt::Key_Help	0x01000058
    Qt::Key_Direction_L	0x01000059
    Qt::Key_Direction_R	0x01000060
    Qt::Key_Space	0x20
    Qt::Key_Any	Key_Space
    Qt::Key_Exclam	0x21
    Qt::Key_QuoteDbl	0x22
    Qt::Key_NumberSign	0x23
    Qt::Key_Dollar	0x24
    Qt::Key_Percent	0x25
    Qt::Key_Ampersand	0x26
    Qt::Key_Apostrophe	0x27
    Qt::Key_ParenLeft	0x28
    Qt::Key_ParenRight	0x29
    Qt::Key_Asterisk	0x2a
    Qt::Key_Plus	0x2b
    Qt::Key_Comma	0x2c
    Qt::Key_Minus	0x2d
    Qt::Key_Period	0x2e
    Qt::Key_Slash	0x2f
    Qt::Key_0	0x30
    Qt::Key_1	0x31
    Qt::Key_2	0x32
    Qt::Key_3	0x33
    Qt::Key_4	0x34
    Qt::Key_5	0x35
    Qt::Key_6	0x36
    Qt::Key_7	0x37
    Qt::Key_8	0x38
    Qt::Key_9	0x39
    Qt::Key_Colon	0x3a
    Qt::Key_Semicolon	0x3b
    Qt::Key_Less	0x3c
    Qt::Key_Equal	0x3d
    Qt::Key_Greater	0x3e
    Qt::Key_Question	0x3f
    Qt::Key_At	0x40
    Qt::Key_A	0x41
    Qt::Key_B	0x42
    Qt::Key_C	0x43
    Qt::Key_D	0x44
    Qt::Key_E	0x45
    Qt::Key_F	0x46
    Qt::Key_G	0x47
    Qt::Key_H	0x48
    Qt::Key_I	0x49
    Qt::Key_J	0x4a
    Qt::Key_K	0x4b
    Qt::Key_L	0x4c
    Qt::Key_M	0x4d
    Qt::Key_N	0x4e
    Qt::Key_O	0x4f
    Qt::Key_P	0x50
    Qt::Key_Q	0x51
    Qt::Key_R	0x52
    Qt::Key_S	0x53
    Qt::Key_T	0x54
    Qt::Key_U	0x55
    Qt::Key_V	0x56
    Qt::Key_W	0x57
    Qt::Key_X	0x58
    Qt::Key_Y	0x59
    Qt::Key_Z	0x5a
    Qt::Key_BracketLeft	0x5b
    Qt::Key_Backslash	0x5c
    Qt::Key_BracketRight	0x5d
    Qt::Key_AsciiCircum	0x5e
    Qt::Key_Underscore	0x5f
    Qt::Key_QuoteLeft	0x60
    Qt::Key_BraceLeft	0x7b
    Qt::Key_Bar	0x7c
    Qt::Key_BraceRight	0x7d
    Qt::Key_AsciiTilde	0x7e
    Qt::Key_nobreakspace	0x0a0
    Qt::Key_exclamdown	0x0a1
    Qt::Key_cent	0x0a2
    Qt::Key_sterling	0x0a3
    Qt::Key_currency	0x0a4
    Qt::Key_yen	0x0a5
    Qt::Key_brokenbar	0x0a6
    Qt::Key_section	0x0a7
    Qt::Key_diaeresis	0x0a8
    Qt::Key_copyright	0x0a9
    Qt::Key_ordfeminine	0x0aa
    Qt::Key_guillemotleft	0x0ab
    Qt::Key_notsign	0x0ac
    Qt::Key_hyphen	0x0ad
    Qt::Key_registered	0x0ae
    Qt::Key_macron	0x0af
    Qt::Key_degree	0x0b0
    Qt::Key_plusminus	0x0b1
    Qt::Key_twosuperior	0x0b2
    Qt::Key_threesuperior	0x0b3
    Qt::Key_acute	0x0b4
    Qt::Key_mu	0x0b5
    Qt::Key_paragraph	0x0b6
    Qt::Key_periodcentered	0x0b7
    Qt::Key_cedilla	0x0b8
    Qt::Key_onesuperior	0x0b9
    Qt::Key_masculine	0x0ba
    Qt::Key_guillemotright	0x0bb
    Qt::Key_onequarter	0x0bc
    Qt::Key_onehalf	0x0bd
    Qt::Key_threequarters	0x0be
    Qt::Key_questiondown	0x0bf
    Qt::Key_Agrave	0x0c0
    Qt::Key_Aacute	0x0c1
    Qt::Key_Acircumflex	0x0c2
    Qt::Key_Atilde	0x0c3
    Qt::Key_Adiaeresis	0x0c4
    Qt::Key_Aring	0x0c5
    Qt::Key_AE	0x0c6
    Qt::Key_Ccedilla	0x0c7
    Qt::Key_Egrave	0x0c8
    Qt::Key_Eacute	0x0c9
    Qt::Key_Ecircumflex	0x0ca
    Qt::Key_Ediaeresis	0x0cb
    Qt::Key_Igrave	0x0cc
    Qt::Key_Iacute	0x0cd
    Qt::Key_Icircumflex	0x0ce
    Qt::Key_Idiaeresis	0x0cf
    Qt::Key_ETH	0x0d0
    Qt::Key_Ntilde	0x0d1
    Qt::Key_Ograve	0x0d2
    Qt::Key_Oacute	0x0d3
    Qt::Key_Ocircumflex	0x0d4
    Qt::Key_Otilde	0x0d5
    Qt::Key_Odiaeresis	0x0d6
    Qt::Key_multiply	0x0d7
    Qt::Key_Ooblique	0x0d8
    Qt::Key_Ugrave	0x0d9
    Qt::Key_Uacute	0x0da
    Qt::Key_Ucircumflex	0x0db
    Qt::Key_Udiaeresis	0x0dc
    Qt::Key_Yacute	0x0dd
    Qt::Key_THORN	0x0de
    Qt::Key_ssharp	0x0df
    Qt::Key_division	0x0f7
    Qt::Key_ydiaeresis	0x0ff
    Qt::Key_Multi_key	0x01001120
    Qt::Key_Codeinput	0x01001137
    Qt::Key_SingleCandidate	0x0100113c
    Qt::Key_MultipleCandidate	0x0100113d
    Qt::Key_PreviousCandidate	0x0100113e
    Qt::Key_Mode_switch	0x0100117e
    Qt::Key_Kanji	0x01001121
    Qt::Key_Muhenkan	0x01001122
    Qt::Key_Henkan	0x01001123
    Qt::Key_Romaji	0x01001124
    Qt::Key_Hiragana	0x01001125
    Qt::Key_Katakana	0x01001126
    Qt::Key_Hiragana_Katakana	0x01001127
    Qt::Key_Zenkaku	0x01001128
    Qt::Key_Hankaku	0x01001129
    Qt::Key_Zenkaku_Hankaku	0x0100112a
    Qt::Key_Touroku	0x0100112b
    Qt::Key_Massyo	0x0100112c
    Qt::Key_Kana_Lock	0x0100112d
    Qt::Key_Kana_Shift	0x0100112e
    Qt::Key_Eisu_Shift	0x0100112f
    Qt::Key_Eisu_toggle	0x01001130
    Qt::Key_Hangul	0x01001131
    Qt::Key_Hangul_Start	0x01001132
    Qt::Key_Hangul_End	0x01001133
    Qt::Key_Hangul_Hanja	0x01001134
    Qt::Key_Hangul_Jamo	0x01001135
    Qt::Key_Hangul_Romaja	0x01001136
    Qt::Key_Hangul_Jeonja	0x01001138
    Qt::Key_Hangul_Banja	0x01001139
    Qt::Key_Hangul_PreHanja	0x0100113a
    Qt::Key_Hangul_PostHanja	0x0100113b
    Qt::Key_Hangul_Special	0x0100113f
    Qt::Key_Dead_Grave	0x01001250
    Qt::Key_Dead_Acute	0x01001251
    Qt::Key_Dead_Circumflex	0x01001252
    Qt::Key_Dead_Tilde	0x01001253
    Qt::Key_Dead_Macron	0x01001254
    Qt::Key_Dead_Breve	0x01001255
    Qt::Key_Dead_Abovedot	0x01001256
    Qt::Key_Dead_Diaeresis	0x01001257
    Qt::Key_Dead_Abovering	0x01001258
    Qt::Key_Dead_Doubleacute	0x01001259
    Qt::Key_Dead_Caron	0x0100125a
    Qt::Key_Dead_Cedilla	0x0100125b
    Qt::Key_Dead_Ogonek	0x0100125c
    Qt::Key_Dead_Iota	0x0100125d
    Qt::Key_Dead_Voiced_Sound	0x0100125e
    Qt::Key_Dead_Semivoiced_Sound	0x0100125f
    Qt::Key_Dead_Belowdot	0x01001260
    Qt::Key_Dead_Hook	0x01001261
    Qt::Key_Dead_Horn	0x01001262
    Qt::Key_Dead_Stroke	0x01001263
    Qt::Key_Dead_Abovecomma	0x01001264
    Qt::Key_Dead_Abovereversedcomma	0x01001265
    Qt::Key_Dead_Doublegrave	0x01001266
    Qt::Key_Dead_Belowring	0x01001267
    Qt::Key_Dead_Belowmacron	0x01001268
    Qt::Key_Dead_Belowcircumflex	0x01001269
    Qt::Key_Dead_Belowtilde	0x0100126a
    Qt::Key_Dead_Belowbreve	0x0100126b
    Qt::Key_Dead_Belowdiaeresis	0x0100126c
    Qt::Key_Dead_Invertedbreve	0x0100126d
    Qt::Key_Dead_Belowcomma	0x0100126e
    Qt::Key_Dead_Currency	0x0100126f
    Qt::Key_Dead_a	0x01001280
    Qt::Key_Dead_A	0x01001281
    Qt::Key_Dead_e	0x01001282
    Qt::Key_Dead_E	0x01001283
    Qt::Key_Dead_i	0x01001284
    Qt::Key_Dead_I	0x01001285
    Qt::Key_Dead_o	0x01001286
    Qt::Key_Dead_O	0x01001287
    Qt::Key_Dead_u	0x01001288
    Qt::Key_Dead_U	0x01001289
    Qt::Key_Dead_Small_Schwa	0x0100128a
    Qt::Key_Dead_Capital_Schwa	0x0100128b
    Qt::Key_Dead_Greek	0x0100128c
    Qt::Key_Dead_Lowline	0x01001290
    Qt::Key_Dead_Aboveverticalline	0x01001291
    Qt::Key_Dead_Belowverticalline	0x01001292
    Qt::Key_Dead_Longsolidusoverlay	0x01001293
    Qt::Key_Back	0x01000061
    Qt::Key_Forward	0x01000062
    Qt::Key_Stop	0x01000063
    Qt::Key_Refresh	0x01000064
    Qt::Key_VolumeDown	0x01000070
    Qt::Key_VolumeMute	0x01000071
    Qt::Key_VolumeUp	0x01000072
    Qt::Key_BassBoost	0x01000073
    Qt::Key_BassUp	0x01000074
    Qt::Key_BassDown	0x01000075
    Qt::Key_TrebleUp	0x01000076
    Qt::Key_TrebleDown	0x01000077
    Qt::Key_MediaPlay	0x01000080	A key setting the state of the media player to play
    Qt::Key_MediaStop	0x01000081	A key setting the state of the media player to stop
    Qt::Key_MediaPrevious	0x01000082
    Qt::Key_MediaNext	0x01000083
    Qt::Key_MediaRecord	0x01000084
    Qt::Key_MediaPause	0x01000085	A key setting the state of the media player to pause (Note: not the
    pause/break key)
    Qt::Key_MediaTogglePlayPause	0x01000086	A key to toggle the play/pause state in the media player (rather
    than setting an absolute state)
    Qt::Key_HomePage	0x01000090
    Qt::Key_Favorites	0x01000091
    Qt::Key_Search	0x01000092
    Qt::Key_Standby	0x01000093
    Qt::Key_OpenUrl	0x01000094
    Qt::Key_LaunchMail	0x010000a0
    Qt::Key_LaunchMedia	0x010000a1
    Qt::Key_Launch0	0x010000a2
    Qt::Key_Launch1	0x010000a3
    Qt::Key_Launch2	0x010000a4
    Qt::Key_Launch3	0x010000a5
    Qt::Key_Launch4	0x010000a6
    Qt::Key_Launch5	0x010000a7
    Qt::Key_Launch6	0x010000a8
    Qt::Key_Launch7	0x010000a9
    Qt::Key_Launch8	0x010000aa
    Qt::Key_Launch9	0x010000ab
    Qt::Key_LaunchA	0x010000ac
    Qt::Key_LaunchB	0x010000ad
    Qt::Key_LaunchC	0x010000ae
    Qt::Key_LaunchD	0x010000af
    Qt::Key_LaunchE	0x010000b0
    Qt::Key_LaunchF	0x010000b1
    Qt::Key_LaunchG	0x0100010e
    Qt::Key_LaunchH	0x0100010f
    Qt::Key_MonBrightnessUp	0x010000b2
    Qt::Key_MonBrightnessDown	0x010000b3
    Qt::Key_KeyboardLightOnOff	0x010000b4
    Qt::Key_KeyboardBrightnessUp	0x010000b5
    Qt::Key_KeyboardBrightnessDown	0x010000b6
    Qt::Key_PowerOff	0x010000b7
    Qt::Key_WakeUp	0x010000b8
    Qt::Key_Eject	0x010000b9
    Qt::Key_ScreenSaver	0x010000ba
    Qt::Key_WWW	0x010000bb
    Qt::Key_Memo	0x010000bc
    Qt::Key_LightBulb	0x010000bd
    Qt::Key_Shop	0x010000be
    Qt::Key_History	0x010000bf
    Qt::Key_AddFavorite	0x010000c0
    Qt::Key_HotLinks	0x010000c1
    Qt::Key_BrightnessAdjust	0x010000c2
    Qt::Key_Finance	0x010000c3
    Qt::Key_Community	0x010000c4
    Qt::Key_AudioRewind	0x010000c5
    Qt::Key_BackForward	0x010000c6
    Qt::Key_ApplicationLeft	0x010000c7
    Qt::Key_ApplicationRight	0x010000c8
    Qt::Key_Book	0x010000c9
    Qt::Key_CD	0x010000ca
    Qt::Key_Calculator	0x010000cb
    Qt::Key_ToDoList	0x010000cc
    Qt::Key_ClearGrab	0x010000cd
    Qt::Key_Close	0x010000ce
    Qt::Key_Copy	0x010000cf
    Qt::Key_Cut	0x010000d0
    Qt::Key_Display	0x010000d1
    Qt::Key_DOS	0x010000d2
    Qt::Key_Documents	0x010000d3
    Qt::Key_Excel	0x010000d4
    Qt::Key_Explorer	0x010000d5
    Qt::Key_Game	0x010000d6
    Qt::Key_Go	0x010000d7
    Qt::Key_iTouch	0x010000d8
    Qt::Key_LogOff	0x010000d9
    Qt::Key_Market	0x010000da
    Qt::Key_Meeting	0x010000db
    Qt::Key_MenuKB	0x010000dc
    Qt::Key_MenuPB	0x010000dd
    Qt::Key_MySites	0x010000de
    Qt::Key_News	0x010000df
    Qt::Key_OfficeHome	0x010000e0
    Qt::Key_Option	0x010000e1
    Qt::Key_Paste	0x010000e2
    Qt::Key_Phone	0x010000e3
    Qt::Key_Calendar	0x010000e4
    Qt::Key_Reply	0x010000e5
    Qt::Key_Reload	0x010000e6
    Qt::Key_RotateWindows	0x010000e7
    Qt::Key_RotationPB	0x010000e8
    Qt::Key_RotationKB	0x010000e9
    Qt::Key_Save	0x010000ea
    Qt::Key_Send	0x010000eb
    Qt::Key_Spell	0x010000ec
    Qt::Key_SplitScreen	0x010000ed
    Qt::Key_Support	0x010000ee
    Qt::Key_TaskPane	0x010000ef
    Qt::Key_Terminal	0x010000f0
    Qt::Key_Tools	0x010000f1
    Qt::Key_Travel	0x010000f2
    Qt::Key_Video	0x010000f3
    Qt::Key_Word	0x010000f4
    Qt::Key_Xfer	0x010000f5
    Qt::Key_ZoomIn	0x010000f6
    Qt::Key_ZoomOut	0x010000f7
    Qt::Key_Away	0x010000f8
    Qt::Key_Messenger	0x010000f9
    Qt::Key_WebCam	0x010000fa
    Qt::Key_MailForward	0x010000fb
    Qt::Key_Pictures	0x010000fc
    Qt::Key_Music	0x010000fd
    Qt::Key_Battery	0x010000fe
    Qt::Key_Bluetooth	0x010000ff
    Qt::Key_WLAN	0x01000100
    Qt::Key_UWB	0x01000101
    Qt::Key_AudioForward	0x01000102
    Qt::Key_AudioRepeat	0x01000103
    Qt::Key_AudioRandomPlay	0x01000104
    Qt::Key_Subtitle	0x01000105
    Qt::Key_AudioCycleTrack	0x01000106
    Qt::Key_Time	0x01000107
    Qt::Key_Hibernate	0x01000108
    Qt::Key_View	0x01000109
    Qt::Key_TopMenu	0x0100010a
    Qt::Key_PowerDown	0x0100010b
    Qt::Key_Suspend	0x0100010c
    Qt::Key_ContrastAdjust	0x0100010d
    Qt::Key_TouchpadToggle	0x01000110
    Qt::Key_TouchpadOn	0x01000111
    Qt::Key_TouchpadOff	0x01000112
    Qt::Key_MicMute	0x01000113
    Qt::Key_Red	0x01000114
    Qt::Key_Green	0x01000115
    Qt::Key_Yellow	0x01000116
    Qt::Key_Blue	0x01000117
    Qt::Key_ChannelUp	0x01000118
    Qt::Key_ChannelDown	0x01000119
    Qt::Key_Guide	0x0100011a
    Qt::Key_Info	0x0100011b
    Qt::Key_Settings	0x0100011c
    Qt::Key_MicVolumeUp	0x0100011d
    Qt::Key_MicVolumeDown	0x0100011e
    Qt::Key_New	0x01000120
    Qt::Key_Open	0x01000121
    Qt::Key_Find	0x01000122
    Qt::Key_Undo	0x01000123
    Qt::Key_Redo	0x01000124
    Qt::Key_MediaLast	0x0100ffff
    Qt::Key_unknown	0x01ffffff
    Qt::Key_Call	0x01100004	A key to answer or initiate a call (see Qt::Key_ToggleCallHangup for a key to
    toggle current call state)
    Qt::Key_Camera	0x01100020	A key to activate the camera shutter. On Windows Runtime, the environment
    variable QT_QPA_ENABLE_CAMERA_KEYS must be set to receive the event.
    Qt::Key_CameraFocus	0x01100021	A key to focus the camera. On Windows Runtime, the environment variable
    QT_QPA_ENABLE_CAMERA_KEYS must be set to receive the event.
    Qt::Key_Context1	0x01100000
    Qt::Key_Context2	0x01100001
    Qt::Key_Context3	0x01100002
    Qt::Key_Context4	0x01100003
    Qt::Key_Flip	0x01100006
    Qt::Key_Hangup	0x01100005	A key to end an ongoing call (see Qt::Key_ToggleCallHangup for a key to toggle
    current call state)
    Qt::Key_No	0x01010002
    Qt::Key_Select	0x01010000
    Qt::Key_Yes	0x01010001
    Qt::Key_ToggleCallHangup	0x01100007	A key to toggle the current call state (ie. either answer, or hangup)
    depending on current call state
    Qt::Key_VoiceDial	0x01100008
    Qt::Key_LastNumberRedial	0x01100009
    Qt::Key_Execute	0x01020003
    Qt::Key_Printer	0x01020002
    Qt::Key_Play	0x01020005
    Qt::Key_Sleep	0x01020004
    Qt::Key_Zoom	0x01020006
    Qt::Key_Exit	0x0102000a
    Qt::Key_Cancel	0x01020001
    """
