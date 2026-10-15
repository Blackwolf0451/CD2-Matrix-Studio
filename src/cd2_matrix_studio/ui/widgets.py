from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(44, 24)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        track = QRectF(1, 3, 42, 18)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#3d6fbb") if self.isChecked() else QColor("#343b47"))
        painter.drawRoundedRect(track, 9, 9)

        knob_x = 23 if self.isChecked() else 3
        painter.setBrush(QColor("#f4f6f8"))
        painter.drawEllipse(QRectF(knob_x, 5, 14, 14))


class LanguageSwitch(QWidget):
    languageChanged = Signal(str)

    def __init__(self, language="en", parent=None):
        super().__init__(parent)
        self.language = language

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.en = QLabel("EN")
        self.ru = QLabel("RU")
        self.cn = QLabel("CN")

        for label in (self.en, self.ru, self.cn,):
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(36, 26)
            label.setCursor(Qt.CursorShape.PointingHandCursor)
            label.installEventFilter(self)

        layout.addWidget(self.en)
        layout.addWidget(self.ru)
        layout.addWidget(self.cn)
        self._refresh()

    def eventFilter(self, obj, event):
        if event.type() == event.Type.MouseButtonPress:
            if obj is self.en:
                self.set_language("en", emit=True)
                return True
            if obj is self.ru:
                self.set_language("ru", emit=True)
                return True
            if obj is self.cn:
                self.set_language("cn", emit=True)
                return True
        return super().eventFilter(obj, event)

    def set_language(self, language: str, emit=False):
        if language not in ("en", "ru", "cn"):
            language = "en"
        self.language = language
        self._refresh()
        if emit:
            self.languageChanged.emit(language)

    def _refresh(self):
        active = """
            background: #3d6fbb;
            color: white;
            border: 1px solid #5f8dd2;
            font-weight: 700;
        """
        inactive = """
            background: #1a1e25;
            color: #9aa3b1;
            border: 1px solid #343b47;
            font-weight: 600;
        """
        self.en.setStyleSheet(active if self.language == "en" else inactive)
        self.ru.setStyleSheet(active if self.language == "ru" else inactive)
        self.cn.setStyleSheet(active if self.language == "cn" else inactive)


class HintRow(QWidget):
    def __init__(self, key="", description="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(8)

        self.key_label = QLabel(key)
        self.key_label.setObjectName("KeyBadge")
        self.key_label.setFixedWidth(58)
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.description_label = QLabel(description)
        self.description_label.setObjectName("HintDescription")

        layout.addWidget(self.key_label)
        layout.addWidget(self.description_label, 1)

    def set_text(self, key, description):
        self.key_label.setText(key)
        self.description_label.setText(description)


class ReorderListWidget(QListWidget):
    orderChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)

    def dropEvent(self, event):
        super().dropEvent(event)
        order = []
        for i in range(self.count()):
            item = self.item(i)
            order.append(int(item.data(Qt.ItemDataRole.UserRole)))
        self.orderChanged.emit(order)


class GuideDialog(QDialog):
    def __init__(self, title: str, markdown: str, close_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(840, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setMarkdown(markdown)
        layout.addWidget(browser, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(close_text)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str, yes_text: str, no_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(460)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(14)

        text_label = QLabel(message)
        text_label.setObjectName("DialogText")
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        root.addWidget(text_label)

        buttons = QHBoxLayout()
        buttons.setContentsMargins(0, 2, 0, 0)
        buttons.setSpacing(10)
        buttons.addStretch(1)

        self.no_button = QPushButton(no_text)
        self.no_button.setObjectName("DialogSecondaryButton")
        self.no_button.setFixedWidth(116)
        self.no_button.clicked.connect(self.reject)

        self.yes_button = QPushButton(yes_text)
        self.yes_button.setObjectName("DialogPrimaryButton")
        self.yes_button.setFixedWidth(116)
        self.yes_button.clicked.connect(self.accept)
        self.yes_button.setDefault(True)

        buttons.addWidget(self.no_button)
        buttons.addWidget(self.yes_button)
        root.addLayout(buttons)

        self.adjustSize()

    @staticmethod
    def ask(parent, title: str, message: str, yes_text: str, no_text: str) -> bool:
        dialog = ConfirmDialog(title, message, yes_text, no_text, parent)
        return dialog.exec() == QDialog.DialogCode.Accepted
