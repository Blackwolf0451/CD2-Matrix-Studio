from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..protocol import LED_COUNT, ROWS

RGB = tuple[int, int, int]
OFF: RGB = (0, 0, 0)


class MatrixWidget(QWidget):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(560, 520)
        self.setMouseTracking(True)

        self.colors: list[RGB] = [OFF] * LED_COUNT
        self.selected_color: RGB = (255, 255, 255)
        self.tool = "draw"
        self.mirror = True

        self._points: list[QPointF] = []
        self._radius = 10.0
        self._drag_button = Qt.MouseButton.NoButton
        self._stroke_started = False

    def set_frame(self, colors: list[RGB]) -> None:
        self.colors = [tuple(c) for c in colors]
        self.update()

    def set_tool(self, tool: str) -> None:
        self.tool = tool

    def set_selected_color(self, color: RGB) -> None:
        self.selected_color = tuple(color)

    def set_mirror(self, enabled: bool) -> None:
        self.mirror = enabled

    def _layout_points(self) -> None:
        w = max(1, self.width())
        h = max(1, self.height())

        usable_w = w * 0.83
        usable_h = h * 0.84
        dx = min(usable_w / max(ROWS), usable_h / (len(ROWS) * 0.90))
        dy = dx * 0.90
        self._radius = max(5.5, dx * 0.30)

        total_h = (len(ROWS) - 1) * dy
        y0 = (h - total_h) / 2

        points: list[QPointF] = []
        for row, count in enumerate(ROWS):
            row_w = (count - 1) * dx
            x0 = (w - row_w) / 2
            y = y0 + row * dy
            for col in range(count):
                points.append(QPointF(x0 + col * dx, y))
        self._points = points

    def paintEvent(self, event) -> None:
        self._layout_points()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        outline = QPen(QColor("#414853"))
        outline.setWidthF(1.1)
        painter.setPen(outline)

        for point, color in zip(self._points, self.colors):
            painter.setBrush(QColor(*color))
            painter.drawEllipse(point, self._radius, self._radius)

    def resizeEvent(self, event) -> None:
        self._layout_points()
        super().resizeEvent(event)

    def _closest_index(self, pos) -> int | None:
        if not self._points:
            self._layout_points()

        best_i = None
        best_d2 = (self._radius * 1.55) ** 2
        for i, p in enumerate(self._points):
            dx = p.x() - pos.x()
            dy = p.y() - pos.y()
            d2 = dx * dx + dy * dy
            if d2 <= best_d2:
                best_d2 = d2
                best_i = i
        return best_i

    @staticmethod
    def _row_col(index: int) -> tuple[int, int]:
        start = 0
        for row, count in enumerate(ROWS):
            if index < start + count:
                return row, index - start
            start += count
        raise IndexError(index)

    @staticmethod
    def _index(row: int, col: int) -> int:
        return sum(ROWS[:row]) + col

    def _paint_index(self, index: int, color: RGB) -> None:
        self.colors[index] = color
        if self.mirror:
            row, col = self._row_col(index)
            mirror_col = ROWS[row] - 1 - col
            self.colors[self._index(row, mirror_col)] = color

    def _apply_at(self, pos, button) -> bool:
        index = self._closest_index(pos)
        if index is None:
            return False

        if button == Qt.MouseButton.RightButton or self.tool == "erase":
            color = OFF
        elif self.tool == "fill":
            self.colors = [self.selected_color] * LED_COUNT
            self.changed.emit()
            self.update()
            return True
        else:
            color = self.selected_color

        self._paint_index(index, color)
        self.changed.emit()
        self.update()
        return True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self._drag_button = event.button()
            self._apply_at(event.position(), event.button())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_button != Qt.MouseButton.NoButton:
            self._apply_at(event.position(), self._drag_button)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_button = Qt.MouseButton.NoButton
