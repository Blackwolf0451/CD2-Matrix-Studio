from __future__ import annotations

STRINGS = {
    "en": {
        "app_name": "CD2 Matrix Studio",
        "connected": "Dock connected",
        "disconnected": "Dock not found",

        "draw": "Draw",
        "erase": "Erase",
        "fill": "Fill",
        "clear": "Clear frame",
        "mirror": "Mirror",
        "color": "Color",
        "recent_colors": "Recent colors",

        "frames": "Frames",
        "new_frame": "Add",
        "duplicate": "Duplicate",
        "delete": "Delete",
        "move_up": "Move up",
        "move_down": "Move down",
        "drag_frames_hint": "Drag frames to reorder",
        "copy_frame": "Copy frame",
        "paste_frame": "Paste frame",

        "animation": "Animation",
        "animation_preview": "Preview animation",
        "stop_preview": "Stop",
        "animation_speed": "Animation speed",
        "speed_10_tooltip": "10 ms per frame — faster",
        "speed_40_tooltip": "40 ms per frame — slower",

        "send": "Send to Dock",
        "sending": "Sending…",
        "sent": "Sent successfully",

        "file": "File",
        "new_project": "New project",
        "open": "Open…",
        "save": "Save",
        "save_as": "Save as…",
        "exit": "Exit",

        "edit": "Edit",
        "undo": "Undo",
        "redo": "Redo",

        "help": "Help",
        "user_guide": "User guide",
        "about": "About",
        "close": "Close",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "cancel": "Cancel",

        "project_files": "CD2 Matrix Studio project (*.cd2proj *.json)",
        "save_project": "Save project",
        "open_project": "Open project",
        "confirm_new": "Discard the current project and start a new one?",
        "confirm_delete_frame": "Delete this frame?",
        "last_frame": "At least one frame must remain.",
        "frame": "Frame",
        "leds": "LEDs",

        "send_question_single": "Send this frame to the dock?",
        "send_question_multi": "Send {frames} frames to the dock at {interval} ms?",
        "send_question_few": "Send {frames} frames to the dock at {interval} ms?",
        "send_question_many": "Send {frames} frames to the dock at {interval} ms?",
        "close_space_station": "If Flydigi Space Station is open, close it before sending.",
        "device_busy": "The dock could not be opened. Close Flydigi Space Station and try again.",
        "send_error": "Could not send to the dock",
        "open_error": "Could not open the project",
        "save_error": "Could not save the project",
        "guide_missing": "The built-in guide could not be loaded.",

        "about_text": (
            "Unofficial community LED matrix editor for the Flydigi Charging Dock 2 Pro.\n\n"
            "Not affiliated with or endorsed by Flydigi."
        ),

        "quick_actions": "Shortcuts",
        "hint_lmb_key": "LMB",
        "hint_lmb_text": "Draw",
        "hint_rmb_key": "RMB",
        "hint_rmb_text": "Erase",
        "hint_undo_key": "Ctrl+Z",
        "hint_undo_text": "Undo",
        "hint_redo_key": "Ctrl+Y",
        "hint_redo_text": "Redo",
    },

    "ru": {
        "app_name": "CD2 Matrix Studio",
        "connected": "Док подключён",
        "disconnected": "Док не найден",

        "draw": "Рисование",
        "erase": "Ластик",
        "fill": "Заливка",
        "clear": "Очистить кадр",
        "mirror": "Симметрия",
        "color": "Цвет",
        "recent_colors": "Последние цвета",

        "frames": "Кадры",
        "new_frame": "Добавить",
        "duplicate": "Дублировать",
        "delete": "Удалить",
        "move_up": "Выше",
        "move_down": "Ниже",
        "drag_frames_hint": "Кадры можно перетаскивать мышкой",
        "copy_frame": "Копировать кадр",
        "paste_frame": "Вставить кадр",

        "animation": "Анимация",
        "animation_preview": "Просмотр анимации",
        "stop_preview": "Остановить",
        "animation_speed": "Скорость анимации",
        "speed_10_tooltip": "10 мс на кадр — быстрее",
        "speed_40_tooltip": "40 мс на кадр — медленнее",

        "send": "Отправить на док",
        "sending": "Отправка…",
        "sent": "Готово",

        "file": "Файл",
        "new_project": "Новый проект",
        "open": "Открыть…",
        "save": "Сохранить",
        "save_as": "Сохранить как…",
        "exit": "Выход",

        "edit": "Правка",
        "undo": "Отменить",
        "redo": "Повторить",

        "help": "Справка",
        "user_guide": "Инструкция",
        "about": "О программе",
        "close": "Закрыть",
        "yes": "Да",
        "no": "Нет",
        "ok": "ОК",
        "cancel": "Отмена",

        "project_files": "Проект CD2 Matrix Studio (*.cd2proj *.json)",
        "save_project": "Сохранить проект",
        "open_project": "Открыть проект",
        "confirm_new": "Закрыть текущий проект и создать новый?",
        "confirm_delete_frame": "Удалить этот кадр?",
        "last_frame": "В проекте должен остаться хотя бы один кадр.",
        "frame": "Кадр",
        "leds": "LED",

        "send_question_single": "Отправить этот кадр на док?",
        "send_question_few": "Отправить на док {frames} кадра с интервалом {interval} мс?",
        "send_question_many": "Отправить на док {frames} кадров с интервалом {interval} мс?",
        "send_question_multi": "Отправить на док {frames} кадров с интервалом {interval} мс?",
        "close_space_station": "Если открыт Flydigi Space Station, полностью закрой его перед отправкой.",
        "device_busy": "Не удалось открыть док. Закрой Flydigi Space Station и попробуй снова.",
        "send_error": "Не удалось отправить данные на док",
        "open_error": "Не удалось открыть проект",
        "save_error": "Не удалось сохранить проект",
        "guide_missing": "Не удалось загрузить встроенную инструкцию.",

        "about_text": (
            "Неофициальный редактор LED-матрицы для Flydigi Charging Dock 2 Pro.\n\n"
            "Проект сообщества и не связан с Flydigi."
        ),

        "quick_actions": "Быстрые действия",
        "hint_lmb_key": "ЛКМ",
        "hint_lmb_text": "Рисовать",
        "hint_rmb_key": "ПКМ",
        "hint_rmb_text": "Стирать",
        "hint_undo_key": "Ctrl+Z",
        "hint_undo_text": "Отмена",
        "hint_redo_key": "Ctrl+Y",
        "hint_redo_text": "Повтор",
    },
}


class Translator:
    def __init__(self, language: str = "en"):
        self.language = language if language in STRINGS else "en"

    def set_language(self, language: str) -> None:
        self.language = language if language in STRINGS else "en"

    def tr(self, key: str, **kwargs) -> str:
        value = STRINGS[self.language].get(key, key)
        return value.format(**kwargs) if kwargs else value
