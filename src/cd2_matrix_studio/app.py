from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow

QSS = r"""
QWidget {
    background: #111318;
    color: #eef1f5;
    font-family: "Segoe UI";
    font-size: 10pt;
}

QMainWindow {
    background: #111318;
}

QMenuBar {
    background: #111318;
    border-bottom: 1px solid #252a32;
}

QMenuBar::item {
    padding: 5px 8px;
}

QMenuBar::item:selected,
QMenu::item:selected {
    background: #252b36;
}

QMenu {
    background: #171a20;
    border: 1px solid #303641;
    padding: 5px;
}

QFrame#Panel {
    background: #171a20;
    border: 1px solid #272d36;
    border-radius: 12px;
}

QFrame#SubPanel {
    background: #13161b;
    border: 1px solid #2b313b;
    border-radius: 9px;
}

QFrame#ShortcutsPanel {
    background: #13161b;
    border: 1px solid #292f38;
    border-radius: 9px;
}

QFrame#AnimationBar {
    background: #171a20;
    border: 1px solid #272d36;
    border-radius: 12px;
}

QFrame#VerticalDivider {
    color: #343b47;
}

QLabel {
    background: transparent;
}

QLabel#Title {
    font-size: 20pt;
    font-weight: 700;
}

QLabel#SectionTitle {
    font-size: 10.5pt;
    font-weight: 650;
}

QLabel#Muted {
    color: #9aa3b1;
}

QLabel#MutedSmall {
    color: #7f8997;
    font-size: 8.5pt;
}

QLabel#HintDescription {
    color: #aeb6c2;
}

QLabel#KeyBadge {
    background: #222731;
    border: 1px solid #38414e;
    border-radius: 6px;
    color: #e3e8ef;
    padding: 3px 5px;
    font-size: 8.7pt;
    font-weight: 650;
}

QLabel#DragHint {
    color: #7f8997;
    font-size: 13pt;
    font-weight: 700;
}

QLabel#ConnectionDot {
    color: #7a828f;
    font-size: 13pt;
}

QLabel#ConnectionDot[connected="true"] {
    color: #62d48f;
}

QPushButton {
    min-height: 30px;
    padding: 4px 10px;
    border: 1px solid #343b47;
    border-radius: 8px;
    background: #222731;
}

QPushButton:hover {
    background: #2a303c;
    border-color: #465164;
}

QPushButton:pressed {
    background: #191d24;
}

QPushButton:checked {
    background: #273b5d;
    border-color: #4f79b9;
}

QPushButton:disabled {
    color: #666e79;
    background: #191c22;
}

QPushButton#ColorSwatch {
    min-height: 0px;
    padding: 0px;
}

QPushButton#PrimaryButton {
    min-width: 165px;
    background: #3d6fbb;
    border-color: #5f8dd2;
    font-weight: 650;
}

QPushButton#PrimaryButton:hover {
    background: #477bc9;
}

QPushButton#PreviewButton {
    background: #222731;
    border-color: #3b4656;
    font-weight: 600;
}

QPushButton#PreviewButton:hover {
    background: #2a303c;
}

QPushButton#SpeedChoice {
    min-height: 28px;
    padding: 2px 8px;
    background: #181c22;
    border-color: #343b47;
    font-weight: 600;
}

QPushButton#SpeedChoice:hover {
    background: #222832;
}

QPushButton#SpeedChoice:checked {
    background: #273b5d;
    border-color: #5f8dd2;
    color: white;
}

QListWidget#FrameList {
    background: #101217;
    border: 1px solid #2c323c;
    border-radius: 8px;
    padding: 5px;
}

QListWidget::item {
    padding: 7px 8px;
    border-radius: 7px;
}

QListWidget::item:hover {
    background: #1b2028;
}

QListWidget::item:selected {
    background: #273b5d;
}

QDialog {
    background: #15191f;
}

QWidget#DialogPanel {
    background: transparent;
}

QLabel#DialogText {
    color: #e5ebf3;
    padding-top: 2px;
    padding-bottom: 2px;
}

QPushButton#DialogPrimaryButton {
    min-width: 92px;
    background: #3d6fbb;
    border-color: #5f8dd2;
    font-weight: 650;
}

QPushButton#DialogPrimaryButton:hover {
    background: #477bc9;
}

QPushButton#DialogSecondaryButton {
    min-width: 92px;
}

QMessageBox QLabel {
    min-width: 320px;
}

QTextBrowser {
    background: #111318;
    border: 1px solid #2e3540;
    border-radius: 9px;
    padding: 12px;
    selection-background-color: #3d6fbb;
}

QToolTip {
    color: #edf1f6;
    background: #252a33;
    border: 1px solid #3a424e;
    padding: 5px;
}

QStatusBar {
    color: #9ca6b5;
}
"""


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[2]


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("CD2 Matrix Studio")
    app.setOrganizationName("CD2MatrixStudio")
    app.setStyle("Fusion")
    app.setStyleSheet(QSS)

    root = resource_root()
    window = MainWindow(root / "assets", root / "docs")
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
