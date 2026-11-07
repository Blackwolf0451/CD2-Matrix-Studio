"""Interactive GIF import, previewed on the dock's exact 162 LED positions."""
from __future__ import annotations

from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
    QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget,
)

from ..gif_import import Crop, POSITIONS, gif_timeline, load_gif, sample_leds
from ..protocol import MAX_FRAMES


LANG = {
    "ru": {
        "title": "Импорт GIF",
        "source": "Исходный GIF",
        "leds": "Как выглядит на 162 LED",
        "fit": "Вписать",
        "fill": "Заполнить / обрезать",
        "mode": "Режим",
        "zoom": "Масштаб",
        "x": "Сдвиг X",
        "y": "Сдвиг Y",
        "clip": "Длина фрагмента",
        "reset": "Сбросить область",
        "cancel": "Отмена",
        "import": "Импортировать",
        "notice": "Импортируется начальный фрагмент GIF. Лимит дока — 200 кадров; предпросмотр учитывает реальную форму матрицы.",
        "frames": "Максимальная длина фрагмента: {ticks} кадров дока",
        "error": "Не удалось импортировать GIF",
        "ms": "мс",
    },
    "en": {
        "title": "Import GIF",
        "source": "Original GIF",
        "leds": "162-LED matrix preview",
        "fit": "Fit",
        "fill": "Fill / crop",
        "mode": "Mode",
        "zoom": "Zoom",
        "x": "Offset X",
        "y": "Offset Y",
        "clip": "Clip length",
        "reset": "Reset crop",
        "cancel": "Cancel",
        "import": "Import",
        "notice": "Imports the beginning of the GIF. The dock supports at most 200 frames; the preview uses its exact physical geometry.",
        "frames": "Maximum imported clip: {ticks} device frames",
        "error": "Could not import GIF",
        "ms": "ms",
    },
}


class LedPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 350)
        self.colors = [(0, 0, 0)] * len(POSITIONS)

    def set_colors(self, colors):
        self.colors = list(colors)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale = min((self.width() - 32) / 16, (self.height() - 32) / 16)
        x0 = (self.width() - 16 * scale) / 2
        y0 = (self.height() - 15 * scale * 0.90) / 2
        radius = min(8.0, scale * 0.29)
        pen = QPen(QColor("#414853"))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        for (x, y), (r, g, b) in zip(POSITIONS, self.colors):
            painter.setBrush(QColor(r, g, b))
            painter.drawEllipse(
                x0 + x * scale - radius,
                y0 + (y - 0.5) * scale * 0.90 - radius,
                radius * 2,
                radius * 2,
            )
        painter.end()


class GifImportDialog(QDialog):
    def __init__(self, file_path, language="en", interval_ms=40, parent=None):
        super().__init__(parent)
        self.tx = LANG.get(language, LANG["en"])
        self.interval_ms = int(interval_ms)
        self.frames, self.delays = load_gif(file_path)
        self.index = 0
        self.result_frames = None
        self.result_durations = None
        self.total_ms = sum(self.delays)
        self.setWindowTitle(self.tx["title"])
        self.setMinimumSize(820, 690)
        self.resize(920, 750)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(10)
        notice = QLabel(self.tx["notice"])
        notice.setWordWrap(True)
        notice.setObjectName("Muted")
        root.addWidget(notice)

        previews = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel(self.tx["source"]))
        self.original = QLabel()
        self.original.setMinimumSize(300, 350)
        self.original.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original.setObjectName("SubPanel")
        left.addWidget(self.original, 1)
        previews.addLayout(left, 1)

        right = QVBoxLayout()
        right.addWidget(QLabel(self.tx["leds"]))
        self.led_preview = LedPreview()
        right.addWidget(self.led_preview, 1)
        previews.addLayout(right, 1)
        root.addLayout(previews, 1)

        settings = QFormLayout()
        settings.setHorizontalSpacing(18)
        settings.setVerticalSpacing(9)
        self.mode = QComboBox()
        self.mode.addItem(self.tx["fill"], "fill")
        self.mode.addItem(self.tx["fit"], "fit")
        settings.addRow(self.tx["mode"], self.mode)
        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(25, 400)
        self.zoom.setValue(100)
        settings.addRow(self.tx["zoom"], self.zoom)
        self.pan_x = QSlider(Qt.Orientation.Horizontal)
        self.pan_x.setRange(-100, 100)
        self.pan_x.setValue(0)
        settings.addRow(self.tx["x"], self.pan_x)
        self.pan_y = QSlider(Qt.Orientation.Horizontal)
        self.pan_y.setRange(-100, 100)
        self.pan_y.setValue(0)
        settings.addRow(self.tx["y"], self.pan_y)
        self.clip_length = QDoubleSpinBox()
        self.clip_length.setDecimals(2)
        self.clip_length.setSingleStep(0.2)
        self.clip_length.setSuffix(" s")
        limit_s = max(self.interval_ms, min(self.total_ms, self.interval_ms * MAX_FRAMES)) / 1000
        self.clip_length.setRange(self.interval_ms / 1000, limit_s)
        self.clip_length.setValue(limit_s)
        settings.addRow(self.tx["clip"], self.clip_length)
        root.addLayout(settings)

        self.summary = QLabel("")
        self.summary.setObjectName("MutedSmall")
        root.addWidget(self.summary)

        actions = QHBoxLayout()
        self.reset_button = QPushButton(self.tx["reset"])
        self.cancel_button = QPushButton(self.tx["cancel"])
        self.import_button = QPushButton(self.tx["import"])
        self.import_button.setObjectName("PrimaryButton")
        actions.addWidget(self.reset_button)
        actions.addStretch(1)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.import_button)
        root.addLayout(actions)

        self.mode.currentIndexChanged.connect(self.refresh)
        self.zoom.valueChanged.connect(self.refresh)
        self.pan_x.valueChanged.connect(self.refresh)
        self.pan_y.valueChanged.connect(self.refresh)
        self.clip_length.valueChanged.connect(self.refresh)
        self.reset_button.clicked.connect(self.reset_crop)
        self.cancel_button.clicked.connect(self.reject)
        self.import_button.clicked.connect(self.accept_import)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.refresh()
        self.timer.start(max(20, min(self.delays[0], 1000)))

    def crop(self) -> Crop:
        return Crop(
            mode=self.mode.currentData(),
            zoom_percent=self.zoom.value(),
            pan_x=self.pan_x.value(),
            pan_y=self.pan_y.value(),
        )

    def reset_crop(self):
        self.mode.setCurrentIndex(0)
        self.zoom.setValue(100)
        self.pan_x.setValue(0)
        self.pan_y.setValue(0)
        self.refresh()

    def refresh(self):
        source = self.frames[self.index]
        # Copy image so its backing memory safely survives Qt conversion.
        pixmap = QPixmap.fromImage(ImageQt(source.copy()))
        self.original.setPixmap(pixmap.scaled(
            300, 350, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
        self.led_preview.set_colors(sample_leds(source, self.crop()))
        clip_ms = round(self.clip_length.value() * 1000)
        ticks = max(1, min(MAX_FRAMES, round(clip_ms / self.interval_ms)))
        self.summary.setText(self.tx["frames"].format(ticks=ticks))

    def next_frame(self):
        self.index = (self.index + 1) % len(self.frames)
        self.refresh()
        self.timer.start(max(20, min(self.delays[self.index], 1000)))

    def accept_import(self):
        try:
            frames, durations = gif_timeline(
                self.frames, self.delays, self.crop(), self.interval_ms,
                round(self.clip_length.value() * 1000),
            )
            self.result_frames = frames
            self.result_durations = durations
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, self.tx["error"], str(exc))
