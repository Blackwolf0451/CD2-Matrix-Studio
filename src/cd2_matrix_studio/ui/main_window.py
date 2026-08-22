from __future__ import annotations

import locale
from pathlib import Path

from PySide6.QtCore import QObject, QSize, QSettings, QThread, QTimer, Qt, Signal, Slot, QTranslator, QLibraryInfo
from PySide6.QtGui import QAction, QColor, QIcon, QKeySequence, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QColorDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..i18n import Translator
from ..project import Project, SUPPORTED_FRAME_INTERVALS_MS, blank_frame
from ..protocol import ROWS, is_device_connected, send_frames
from .matrix_widget import MatrixWidget
from .widgets import ConfirmDialog, GuideDialog, HintRow, LanguageSwitch, ReorderListWidget, ToggleSwitch

OFF = (0, 0, 0)


class SendWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, frames, speed_code):
        super().__init__()
        self.frames = frames
        self.speed_code = speed_code

    @Slot()
    def run(self):
        try:
            info = send_frames(self.frames, self.speed_code)
            self.finished.emit(info)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    MAX_RECENT_COLORS = 6

    def __init__(self, asset_dir: Path, docs_dir: Path):
        super().__init__()
        self.asset_dir = asset_dir
        self.docs_dir = docs_dir
        self.settings = QSettings("CD2MatrixStudio", "CD2MatrixStudio")

        saved_lang = self.settings.value("language", "")
        if not saved_lang:
            try:
                sys_lang = (locale.getlocale()[0] or "").lower()
            except Exception:
                sys_lang = ""
            saved_lang = "ru" if sys_lang.startswith("ru") else "en"

        self.tx = Translator(saved_lang)
        self.qt_translator = None
        self._apply_qt_translator(saved_lang)
        self.project = Project()
        self.current_frame = 0
        self.current_color = (255, 255, 255)
        self.frame_clipboard = None

        self.undo_stack = []
        self.redo_stack = []

        self._send_thread = None
        self._send_worker = None
        self._previewing = False

        self.recent_colors = self._load_recent_colors()

        self.setWindowTitle(self.tx.tr("app_name"))
        self.resize(1180, 820)
        self.setMinimumSize(980, 700)

        icon_path = self.asset_dir / "app.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._build_ui()
        self._build_menus()
        self._connect_signals()
        self._apply_project()
        self.retranslate_ui()

        self.device_timer = QTimer(self)
        self.device_timer.setInterval(1800)
        self.device_timer.timeout.connect(self._refresh_device_status)
        self.device_timer.start()
        self._refresh_device_status()

        self.preview_timer = QTimer(self)
        self.preview_timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.preview_timer.timeout.connect(self._preview_step)

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        header = QHBoxLayout()
        self.title_label = QLabel("CD2 Matrix Studio")
        self.title_label.setObjectName("Title")
        header.addWidget(self.title_label)
        header.addStretch(1)

        self.language_switch = LanguageSwitch(self.tx.language)
        header.addWidget(self.language_switch)
        header.addSpacing(14)

        self.connection_dot = QLabel("●")
        self.connection_dot.setObjectName("ConnectionDot")
        self.connection_label = QLabel()
        header.addWidget(self.connection_dot)
        header.addWidget(self.connection_label)
        root.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(12)
        root.addLayout(body, 1)

        # Left tool rail
        left = QFrame()
        left.setObjectName("Panel")
        left.setFixedWidth(212)
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(12, 12, 12, 12)
        left_l.setSpacing(7)

        self.color_button = QPushButton()
        left_l.addWidget(self.color_button)

        self.recent_label = QLabel()
        self.recent_label.setObjectName("MutedSmall")
        left_l.addWidget(self.recent_label)

        self.recent_colors_row = QHBoxLayout()
        self.recent_colors_row.setSpacing(5)
        self.recent_buttons = []
        for i in range(self.MAX_RECENT_COLORS):
            btn = QPushButton()
            btn.setObjectName("ColorSwatch")
            btn.setFixedSize(25, 25)
            btn.clicked.connect(lambda checked=False, index=i: self.use_recent_color(index))
            self.recent_colors_row.addWidget(btn)
            self.recent_buttons.append(btn)
        self.recent_colors_row.addStretch(1)
        left_l.addLayout(self.recent_colors_row)

        self.draw_button = QPushButton()
        self.draw_button.setCheckable(True)
        self.draw_button.setChecked(True)

        self.erase_button = QPushButton()
        self.erase_button.setCheckable(True)

        self.pick_button = QPushButton()
        self.pick_button.setCheckable(True)

        self.fill_button = QPushButton()
        self.fill_button.setCheckable(True)

        self.clear_button = QPushButton()

        left_l.addWidget(self.draw_button)
        left_l.addWidget(self.erase_button)
        left_l.addWidget(self.pick_button)
        left_l.addWidget(self.fill_button)
        left_l.addWidget(self.clear_button)

        mirror_row = QFrame()
        mirror_row.setObjectName("SubPanel")
        mirror_l = QHBoxLayout(mirror_row)
        mirror_l.setContentsMargins(10, 7, 8, 7)

        self.mirror_label = QLabel()
        self.mirror_switch = ToggleSwitch()
        self.mirror_switch.setChecked(True)

        mirror_l.addWidget(self.mirror_label)
        mirror_l.addStretch(1)
        mirror_l.addWidget(self.mirror_switch)
        left_l.addWidget(mirror_row)

        left_l.addStretch(1)

        shortcuts = QFrame()
        shortcuts.setObjectName("ShortcutsPanel")
        shortcuts_l = QVBoxLayout(shortcuts)
        shortcuts_l.setContentsMargins(10, 9, 10, 9)
        shortcuts_l.setSpacing(3)

        self.quick_title = QLabel()
        self.quick_title.setObjectName("SectionTitle")
        shortcuts_l.addWidget(self.quick_title)

        self.hint_lmb = HintRow()
        self.hint_rmb = HintRow()
        self.hint_undo = HintRow()
        self.hint_redo = HintRow()

        shortcuts_l.addWidget(self.hint_lmb)
        shortcuts_l.addWidget(self.hint_rmb)
        shortcuts_l.addWidget(self.hint_undo)
        shortcuts_l.addWidget(self.hint_redo)
        left_l.addWidget(shortcuts)

        body.addWidget(left)

        # Matrix
        matrix_panel = QFrame()
        matrix_panel.setObjectName("Panel")
        matrix_l = QVBoxLayout(matrix_panel)
        matrix_l.setContentsMargins(10, 10, 10, 10)

        self.matrix = MatrixWidget()
        matrix_l.addWidget(self.matrix, 1)
        body.addWidget(matrix_panel, 1)

        # Frames
        right = QFrame()
        right.setObjectName("Panel")
        right.setFixedWidth(270)
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(12, 12, 12, 12)
        right_l.setSpacing(7)

        title_row = QHBoxLayout()
        self.frames_label = QLabel()
        self.frames_label.setObjectName("SectionTitle")
        title_row.addWidget(self.frames_label)
        title_row.addStretch(1)

        self.drag_hint = QLabel("↕")
        self.drag_hint.setObjectName("DragHint")
        title_row.addWidget(self.drag_hint)
        right_l.addLayout(title_row)

        self.frame_list = ReorderListWidget()
        self.frame_list.setObjectName("FrameList")
        self.frame_list.setIconSize(QSize(56, 36))
        right_l.addWidget(self.frame_list, 1)

        row1 = QHBoxLayout()
        self.add_frame_button = QPushButton()
        self.duplicate_frame_button = QPushButton()
        row1.addWidget(self.add_frame_button)
        row1.addWidget(self.duplicate_frame_button)
        right_l.addLayout(row1)

        row2 = QHBoxLayout()
        self.move_frame_up_button = QPushButton()
        self.move_frame_down_button = QPushButton()
        row2.addWidget(self.move_frame_up_button)
        row2.addWidget(self.move_frame_down_button)
        right_l.addLayout(row2)

        self.delete_frame_button = QPushButton()
        right_l.addWidget(self.delete_frame_button)
        body.addWidget(right)

        # Bottom animation bar
        bottom = QFrame()
        bottom.setObjectName("AnimationBar")
        bottom_l = QHBoxLayout(bottom)
        bottom_l.setContentsMargins(14, 10, 14, 10)
        bottom_l.setSpacing(12)

        self.animation_label = QLabel()
        self.animation_label.setObjectName("SectionTitle")
        bottom_l.addWidget(self.animation_label)

        self.preview_button = QPushButton()
        self.preview_button.setObjectName("PreviewButton")
        self.preview_button.setMinimumWidth(160)
        bottom_l.addWidget(self.preview_button)

        divider = QFrame()
        divider.setObjectName("VerticalDivider")
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFixedHeight(28)
        bottom_l.addWidget(divider)

        self.speed_label = QLabel()
        self.speed_label.setObjectName("Muted")
        bottom_l.addWidget(self.speed_label)

        self.speed_10_button = QPushButton("10 ms")
        self.speed_10_button.setObjectName("SpeedChoice")
        self.speed_10_button.setCheckable(True)
        self.speed_10_button.setFixedWidth(70)

        self.speed_40_button = QPushButton("40 ms")
        self.speed_40_button.setObjectName("SpeedChoice")
        self.speed_40_button.setCheckable(True)
        self.speed_40_button.setFixedWidth(70)

        self.speed_group = QButtonGroup(self)
        self.speed_group.setExclusive(True)
        self.speed_group.addButton(self.speed_10_button, 10)
        self.speed_group.addButton(self.speed_40_button, 40)

        bottom_l.addWidget(self.speed_10_button)
        bottom_l.addWidget(self.speed_40_button)
        bottom_l.addStretch(1)

        self.send_button = QPushButton()
        self.send_button.setObjectName("PrimaryButton")
        bottom_l.addWidget(self.send_button)

        root.addWidget(bottom)
        self.statusBar().showMessage("")

    def _build_menus(self):
        menu = self.menuBar()

        self.file_menu = menu.addMenu("")
        self.new_action = QAction(self)
        self.open_action = QAction(self)
        self.save_action = QAction(self)
        self.save_as_action = QAction(self)
        self.exit_action = QAction(self)

        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)

        for action in (
            self.new_action,
            self.open_action,
            self.save_action,
            self.save_as_action,
            self.exit_action,
        ):
            self.file_menu.addAction(action)
        self.file_menu.insertSeparator(self.exit_action)

        self.edit_menu = menu.addMenu("")

        self.undo_action = QAction(self)
        self.redo_action = QAction(self)
        self.copy_frame_action = QAction(self)
        self.paste_frame_action = QAction(self)

        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.copy_frame_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.paste_frame_action.setShortcut(QKeySequence.StandardKey.Paste)

        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.copy_frame_action)
        self.edit_menu.addAction(self.paste_frame_action)

        self.help_menu = menu.addMenu("")
        self.guide_action = QAction(self)
        self.about_action = QAction(self)
        self.help_menu.addAction(self.guide_action)
        self.help_menu.addAction(self.about_action)

    def _connect_signals(self):
        self.language_switch.languageChanged.connect(self.set_language)

        self.color_button.clicked.connect(self.choose_color)
        self.draw_button.clicked.connect(lambda: self.set_tool("draw"))
        self.erase_button.clicked.connect(lambda: self.set_tool("erase"))
        self.pick_button.clicked.connect(lambda: self.set_tool("pick"))
        self.fill_button.clicked.connect(lambda: self.set_tool("fill"))
        self.clear_button.clicked.connect(self.clear_frame)
        self.mirror_switch.toggled.connect(self.matrix.set_mirror)

        self.matrix.changed.connect(self._matrix_changed)
        self.matrix.colorPicked.connect(self._color_picked)

        self.frame_list.currentRowChanged.connect(self.select_frame)
        self.frame_list.orderChanged.connect(self.frames_reordered)

        self.add_frame_button.clicked.connect(self.add_frame)
        self.duplicate_frame_button.clicked.connect(self.duplicate_frame)
        self.delete_frame_button.clicked.connect(self.delete_frame)
        self.move_frame_up_button.clicked.connect(lambda: self.move_frame(-1))
        self.move_frame_down_button.clicked.connect(lambda: self.move_frame(1))

        self.preview_button.clicked.connect(self.toggle_preview)
        self.speed_group.idClicked.connect(self.set_frame_interval)
        self.send_button.clicked.connect(self.send_to_dock)

        self.new_action.triggered.connect(self.new_project)
        self.open_action.triggered.connect(self.open_project)
        self.save_action.triggered.connect(self.save_project)
        self.save_as_action.triggered.connect(lambda: self.save_project(save_as=True))
        self.exit_action.triggered.connect(self.close)

        self.undo_action.triggered.connect(self.undo)
        self.redo_action.triggered.connect(self.redo)
        self.copy_frame_action.triggered.connect(self.copy_frame)
        self.paste_frame_action.triggered.connect(self.paste_frame)

        self.guide_action.triggered.connect(self.open_guide)
        self.about_action.triggered.connect(self.show_about)

    def _apply_qt_translator(self, language: str) -> None:
        app = QApplication.instance()
        if app is None:
            return

        if self.qt_translator is not None:
            app.removeTranslator(self.qt_translator)
            self.qt_translator = None

        if language != "ru":
            return

        translator = QTranslator(self)
        translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        loaded = (
            translator.load("qtbase_ru", translations_path)
            or translator.load("qt_ru", translations_path)
        )
        if loaded:
            app.installTranslator(translator)
            self.qt_translator = translator

    def _confirm(self, title: str, text: str) -> bool:
        return ConfirmDialog.ask(
            self,
            title,
            text,
            self.tx.tr("yes"),
            self.tx.tr("no"),
        )

    # ---------- language ----------
    def set_language(self, language):
        self.tx.set_language(language)
        self.settings.setValue("language", language)
        self._apply_qt_translator(language)
        self.language_switch.set_language(language)
        self.retranslate_ui()

    def retranslate_ui(self):
        tr = self.tx.tr

        self.setWindowTitle(tr("app_name"))
        self.connection_label.setText(
            tr("connected") if is_device_connected() else tr("disconnected")
        )

        self.color_button.setText(tr("color"))
        self.recent_label.setText(tr("recent_colors"))
        self.draw_button.setText(tr("draw"))
        self.erase_button.setText(tr("erase"))
        self.pick_button.setText(tr("eyedropper"))
        self.fill_button.setText(tr("fill"))
        self.clear_button.setText(tr("clear"))
        self.mirror_label.setText(tr("mirror"))

        self.quick_title.setText(tr("quick_actions"))
        self.hint_lmb.set_text(tr("hint_lmb_key"), tr("hint_lmb_text"))
        self.hint_rmb.set_text(tr("hint_rmb_key"), tr("hint_rmb_text"))
        self.hint_undo.set_text(tr("hint_undo_key"), tr("hint_undo_text"))
        self.hint_redo.set_text(tr("hint_redo_key"), tr("hint_redo_text"))

        self.frames_label.setText(tr("frames"))
        self.drag_hint.setToolTip(tr("drag_frames_hint"))
        self.add_frame_button.setText(tr("new_frame"))
        self.duplicate_frame_button.setText(tr("duplicate"))
        self.delete_frame_button.setText(tr("delete"))
        self.move_frame_up_button.setText(tr("move_up"))
        self.move_frame_down_button.setText(tr("move_down"))

        self.animation_label.setText(tr("animation"))
        self.preview_button.setText(
            tr("stop_preview") if self._previewing else tr("animation_preview")
        )
        self.speed_label.setText(tr("animation_speed"))
        self.speed_10_button.setToolTip(tr("speed_10_tooltip"))
        self.speed_40_button.setToolTip(tr("speed_40_tooltip"))
        self.send_button.setText(tr("send"))

        self.file_menu.setTitle(tr("file"))
        self.new_action.setText(tr("new_project"))
        self.open_action.setText(tr("open"))
        self.save_action.setText(tr("save"))
        self.save_as_action.setText(tr("save_as"))
        self.exit_action.setText(tr("exit"))

        self.edit_menu.setTitle(tr("edit"))
        self.undo_action.setText(tr("undo"))
        self.redo_action.setText(tr("redo"))
        self.copy_frame_action.setText(tr("copy_frame"))
        self.paste_frame_action.setText(tr("paste_frame"))

        self.help_menu.setTitle(tr("help"))
        self.guide_action.setText(tr("user_guide"))
        self.about_action.setText(tr("about"))

        self.refresh_frame_list()

    # ---------- colors ----------
    def _load_recent_colors(self):
        raw = self.settings.value("recent_colors", [])
        if isinstance(raw, str):
            raw = [raw]

        parsed = []
        for value in raw or []:
            try:
                text = str(value).lstrip("#")
                if len(text) != 6:
                    continue
                parsed.append(
                    (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
                )
            except Exception:
                pass

        defaults = [
            (255, 255, 255),
            (0, 120, 255),
            (255, 60, 60),
            (60, 210, 120),
            (160, 100, 255),
            (255, 175, 70),
        ]

        for color in defaults:
            if color not in parsed:
                parsed.append(color)

        return parsed[: self.MAX_RECENT_COLORS]

    def _save_recent_colors(self):
        values = ["#%02X%02X%02X" % color for color in self.recent_colors]
        self.settings.setValue("recent_colors", values)

    def _remember_color(self, color):
        color = tuple(int(v) for v in color)
        if color in self.recent_colors:
            self.recent_colors.remove(color)
        self.recent_colors.insert(0, color)
        self.recent_colors = self.recent_colors[: self.MAX_RECENT_COLORS]
        self._save_recent_colors()
        self._refresh_recent_color_buttons()

    def _refresh_recent_color_buttons(self):
        for i, btn in enumerate(self.recent_buttons):
            if i >= len(self.recent_colors):
                btn.setVisible(False)
                continue

            btn.setVisible(True)
            r, g, b = self.recent_colors[i]
            btn.setStyleSheet(
                f"background: rgb({r},{g},{b}); "
                "border: 1px solid #4a5260; border-radius: 6px;"
            )
            btn.setToolTip(f"RGB {r}, {g}, {b}")

    def use_recent_color(self, index):
        if index < 0 or index >= len(self.recent_colors):
            return
        self.set_current_color(self.recent_colors[index], remember=True)

    def set_current_color(self, color, remember=False):
        self.current_color = tuple(int(v) for v in color)
        self.matrix.set_selected_color(self.current_color)
        self._update_color_button()

        if remember:
            self._remember_color(self.current_color)

    def choose_color(self):
        initial = QColor(*self.current_color)
        dialog = QColorDialog(initial, self)
        dialog.setWindowTitle(self.tx.tr("color"))
        dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        dialog.setCurrentColor(initial)
        if dialog.exec():
            color = dialog.currentColor()
            self.set_current_color(
                (color.red(), color.green(), color.blue()),
                remember=True,
            )

    def _color_picked(self, color):
        self.set_current_color(color, remember=True)
        self.set_tool("draw")

    def _update_color_button(self):
        r, g, b = self.current_color
        lum = r * 0.299 + g * 0.587 + b * 0.114
        fg = "#111111" if lum > 150 else "#ffffff"
        self.color_button.setStyleSheet(
            f"background: rgb({r},{g},{b}); color: {fg};"
        )

    # ---------- editor ----------
    def set_tool(self, tool):
        self.matrix.set_tool(tool)
        self.draw_button.setChecked(tool == "draw")
        self.erase_button.setChecked(tool == "erase")
        self.pick_button.setChecked(tool == "pick")
        self.fill_button.setChecked(tool == "fill")

    def _snapshot(self):
        self.undo_stack.append(self.project.frames[self.current_frame].copy())
        if len(self.undo_stack) > 80:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _matrix_changed(self):
        self.project.frames[self.current_frame] = self.matrix.colors.copy()
        self.refresh_frame_list(keep_selection=True)

    def clear_frame(self):
        self._snapshot()
        self.project.frames[self.current_frame] = blank_frame()
        self.matrix.set_frame(self.project.frames[self.current_frame])
        self.refresh_frame_list(keep_selection=True)

    def undo(self):
        if not self.undo_stack:
            return

        self.redo_stack.append(self.project.frames[self.current_frame].copy())
        self.project.frames[self.current_frame] = self.undo_stack.pop()

        self.matrix.set_frame(self.project.frames[self.current_frame])
        self.refresh_frame_list(keep_selection=True)

    def redo(self):
        if not self.redo_stack:
            return

        self.undo_stack.append(self.project.frames[self.current_frame].copy())
        self.project.frames[self.current_frame] = self.redo_stack.pop()

        self.matrix.set_frame(self.project.frames[self.current_frame])
        self.refresh_frame_list(keep_selection=True)

    def select_frame(self, row):
        if row < 0 or row >= len(self.project.frames) or self._previewing:
            return

        self.current_frame = row
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.matrix.set_frame(self.project.frames[row])

    # ---------- frame list ----------
    def add_frame(self):
        if len(self.project.frames) >= 200:
            return

        self.project.frames.insert(self.current_frame + 1, blank_frame())
        self.current_frame += 1
        self.refresh_frame_list()
        self.frame_list.setCurrentRow(self.current_frame)

    def duplicate_frame(self):
        if len(self.project.frames) >= 200:
            return

        self.project.frames.insert(
            self.current_frame + 1,
            self.project.frames[self.current_frame].copy(),
        )
        self.current_frame += 1
        self.refresh_frame_list()
        self.frame_list.setCurrentRow(self.current_frame)

    def copy_frame(self):
        self.frame_clipboard = self.project.frames[self.current_frame].copy()

    def paste_frame(self):
        if self.frame_clipboard is None or len(self.project.frames) >= 200:
            return

        self.project.frames.insert(
            self.current_frame + 1,
            self.frame_clipboard.copy(),
        )
        self.current_frame += 1
        self.refresh_frame_list()
        self.frame_list.setCurrentRow(self.current_frame)

    def delete_frame(self):
        if len(self.project.frames) == 1:
            QMessageBox.information(
                self,
                self.tx.tr("delete"),
                self.tx.tr("last_frame"),
            )
            return

        if not self._confirm(
            self.tx.tr("delete"),
            self.tx.tr("confirm_delete_frame"),
        ):
            return

        del self.project.frames[self.current_frame]
        self.current_frame = min(self.current_frame, len(self.project.frames) - 1)

        self.refresh_frame_list()
        self.frame_list.setCurrentRow(self.current_frame)

    def move_frame(self, direction):
        target = self.current_frame + direction
        if target < 0 or target >= len(self.project.frames):
            return

        frame = self.project.frames.pop(self.current_frame)
        self.project.frames.insert(target, frame)
        self.current_frame = target

        self.refresh_frame_list()
        self.frame_list.setCurrentRow(self.current_frame)

    def frames_reordered(self, order):
        if len(order) != len(self.project.frames):
            self.refresh_frame_list()
            return

        old_frames = self.project.frames
        try:
            new_frames = [old_frames[int(i)] for i in order]
        except Exception:
            self.refresh_frame_list()
            return

        self.project.frames = [frame.copy() for frame in new_frames]
        self.current_frame = self.frame_list.currentRow()
        self.refresh_frame_list()
        self.frame_list.setCurrentRow(self.current_frame)

    @staticmethod
    def _frame_icon(frame):
        width, height = 64, 42
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        dx = 3.25
        dy = 2.55
        radius = 0.95
        y0 = 2.4

        index = 0
        for row, count in enumerate(ROWS):
            row_width = (count - 1) * dx
            x0 = width / 2 - row_width / 2
            y = y0 + row * dy

            for col in range(count):
                r, g, b = frame[index]
                x = x0 + col * dx
                painter.setPen(QPen(QColor("#59606c"), 0.35))
                painter.setBrush(QColor(r, g, b))
                painter.drawEllipse(
                    x - radius,
                    y - radius,
                    radius * 2,
                    radius * 2,
                )
                index += 1

        painter.end()
        return QIcon(pixmap)

    def refresh_frame_list(self, keep_selection=False):
        selected = (
            self.current_frame
            if keep_selection
            else self.frame_list.currentRow()
        )

        self.frame_list.blockSignals(True)
        self.frame_list.clear()

        for i, frame in enumerate(self.project.frames):
            lit = sum(1 for rgb in frame if tuple(rgb) != OFF)

            item = QListWidgetItem(
                self._frame_icon(frame),
                f"{self.tx.tr('frame')} {i + 1:02d}\n{lit} {self.tx.tr('leds')}",
            )
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.frame_list.addItem(item)

        row = (
            self.current_frame
            if selected < 0
            else min(selected, len(self.project.frames) - 1)
        )
        self.frame_list.setCurrentRow(row)
        self.frame_list.blockSignals(False)

    # ---------- animation timing ----------
    def set_frame_interval(self, interval_ms):
        interval_ms = int(interval_ms)
        if interval_ms not in SUPPORTED_FRAME_INTERVALS_MS:
            return

        self.project.frame_interval_ms = interval_ms
        self._sync_speed_buttons()

        if self._previewing:
            self.preview_timer.setInterval(interval_ms)

    def _sync_speed_buttons(self):
        self.speed_10_button.setChecked(self.project.frame_interval_ms == 10)
        self.speed_40_button.setChecked(self.project.frame_interval_ms == 40)

    def toggle_preview(self):
        if self._previewing:
            self._previewing = False
            self.preview_timer.stop()
            self.preview_button.setText(self.tx.tr("animation_preview"))
            return

        if len(self.project.frames) < 2:
            return

        self._previewing = True
        self.preview_timer.setInterval(self.project.frame_interval_ms)
        self.preview_timer.start()
        self.preview_button.setText(self.tx.tr("stop_preview"))

    def _preview_step(self):
        self.current_frame = (self.current_frame + 1) % len(self.project.frames)

        self.frame_list.blockSignals(True)
        self.frame_list.setCurrentRow(self.current_frame)
        self.frame_list.blockSignals(False)

        self.matrix.set_frame(self.project.frames[self.current_frame])

    # ---------- project ----------
    def _apply_project(self):
        self.current_frame = 0

        self.matrix.set_frame(self.project.frames[0])
        self.matrix.set_selected_color(self.current_color)
        self.matrix.set_mirror(True)
        self.mirror_switch.setChecked(True)

        self.undo_stack.clear()
        self.redo_stack.clear()

        self._sync_speed_buttons()
        self.refresh_frame_list()
        self.frame_list.setCurrentRow(0)
        self._update_color_button()
        self._refresh_recent_color_buttons()

    def new_project(self):
        if (
            len(self.project.frames) > 1
            or any(rgb != OFF for rgb in self.project.frames[0])
        ):
            if not self._confirm(
                self.tx.tr("new_project"),
                self.tx.tr("confirm_new"),
            ):
                return

        self.project = Project()
        self._apply_project()

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tx.tr("open_project"),
            "",
            self.tx.tr("project_files"),
        )
        if not path:
            return

        try:
            self.project = Project.load(path)
            self._apply_project()
            self.statusBar().showMessage(path, 4000)
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tx.tr("open_error"),
                f"{self.tx.tr('open_error')}:\n{exc}",
            )

    def save_project(self, save_as=False):
        path = None if save_as else self.project.path
        if path is None:
            path, _ = QFileDialog.getSaveFileName(
                self,
                self.tx.tr("save_project"),
                "project.cd2proj",
                self.tx.tr("project_files"),
            )
            if not path:
                return

            if not path.lower().endswith((".cd2proj", ".json")):
                path += ".cd2proj"

        try:
            saved = self.project.save(path)
            self.statusBar().showMessage(str(saved), 4000)
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.tx.tr("save_error"),
                f"{self.tx.tr('save_error')}:\n{exc}",
            )

    # ---------- device ----------
    def _refresh_device_status(self):
        connected = is_device_connected()

        self.connection_label.setText(
            self.tx.tr("connected") if connected else self.tx.tr("disconnected")
        )

        self.connection_dot.setProperty("connected", connected)
        self.connection_dot.style().unpolish(self.connection_dot)
        self.connection_dot.style().polish(self.connection_dot)

        self.send_button.setEnabled(
            connected and self._send_thread is None
        )

    def send_to_dock(self):
        if self._send_thread is not None:
            return

        if not is_device_connected():
            self._refresh_device_status()
            return

        frame_count = len(self.project.frames)

        if frame_count == 1:
            question = self.tx.tr("send_question_single")
        elif self.tx.language == "ru":
            mod10 = frame_count % 10
            mod100 = frame_count % 100
            key = (
                "send_question_few"
                if mod10 in (2, 3, 4) and mod100 not in (12, 13, 14)
                else "send_question_many"
            )
            question = self.tx.tr(
                key,
                frames=frame_count,
                interval=self.project.frame_interval_ms,
            )
        else:
            question = self.tx.tr(
                "send_question_multi",
                frames=frame_count,
                interval=self.project.frame_interval_ms,
            )

        text = question + "\n\n" + self.tx.tr("close_space_station")

        if not self._confirm(
            self.tx.tr("send"),
            text,
        ):
            return

        self.send_button.setEnabled(False)
        self.send_button.setText(self.tx.tr("sending"))
        self.statusBar().showMessage(self.tx.tr("sending"))

        thread = QThread(self)
        worker = SendWorker(
            [frame.copy() for frame in self.project.frames],
            self.project.device_speed_code,
        )
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._send_finished)
        worker.failed.connect(self._send_failed)

        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(self._send_cleanup)

        self._send_thread = thread
        self._send_worker = worker
        thread.start()

    @Slot(object)
    def _send_finished(self, info):
        self.statusBar().showMessage(
            self.tx.tr("sent"),
            5000,
        )

    @Slot(str)
    def _send_failed(self, message):
        display = message
        lowered = message.lower()

        if (
            "open" in lowered
            or "access" in lowered
            or "busy" in lowered
        ):
            display += "\n\n" + self.tx.tr("device_busy")

        QMessageBox.critical(
            self,
            self.tx.tr("send_error"),
            display,
        )

    @Slot()
    def _send_cleanup(self):
        if self._send_thread is not None:
            self._send_thread.deleteLater()

        self._send_thread = None
        self._send_worker = None

        self.send_button.setText(self.tx.tr("send"))
        self._refresh_device_status()

    # ---------- help ----------
    def open_guide(self):
        filename = (
            "USER_GUIDE_RU.md"
            if self.tx.language == "ru"
            else "USER_GUIDE_EN.md"
        )
        path = self.docs_dir / filename

        if not path.exists():
            QMessageBox.information(
                self,
                self.tx.tr("user_guide"),
                self.tx.tr("guide_missing"),
            )
            return

        try:
            markdown = path.read_text(encoding="utf-8")
        except Exception:
            QMessageBox.information(
                self,
                self.tx.tr("user_guide"),
                self.tx.tr("guide_missing"),
            )
            return

        dialog = GuideDialog(
            self.tx.tr("user_guide"),
            markdown,
            self.tx.tr("close"),
            self,
        )
        dialog.exec()

    def show_about(self):
        QMessageBox.about(
            self,
            self.tx.tr("about"),
            (
                f"<b>{self.tx.tr('app_name')}</b><br>"
                f"<span style='color:#9aa3b1'>v{__version__}</span><br><br>"
                + self.tx.tr("about_text").replace("\n", "<br>")
            ),
        )
