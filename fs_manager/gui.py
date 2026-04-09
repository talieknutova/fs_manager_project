import flet as ft
from fs_manager.core import operations
import sys
import io
import traceback
import logging

class StringIORedirector(io.StringIO):
    """Класс для перехвата стандартного вывода (print) в интерфейс."""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def write(self, s):
        self.callback(s)

class GUILoggingHandler(logging.Handler):
    """Класс для перехвата логов (logging.info) в интерфейс."""
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        self.callback(msg + '\n')

def main_gui(page: ft.Page):
    page.title = "Менеджер файловой системы"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 700
    page.padding = 30
    page.vertical_alignment = ft.MainAxisAlignment.START

    def show_message(msg: str, is_error: bool = False):
        color = ft.colors.ERROR if is_error else ft.colors.GREEN_600
        page.snack_bar = ft.SnackBar(ft.Text(msg, color=ft.colors.WHITE), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    console_output = ft.TextField(
        multiline=True,
        read_only=True,
        expand=True,
        text_size=13,
        border_color=ft.colors.OUTLINE,
        bgcolor=ft.colors.SURFACE_VARIANT,
        label="Вывод результатов",
    )

    def write_to_console(s: str):
        console_output.value = (console_output.value or "") + s
        console_output.update()

    sys.stdout = StringIORedirector(write_to_console)

    gui_logger = GUILoggingHandler(write_to_console)
    gui_logger.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(gui_logger)

    target_input = None

    def on_dialog_result(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            target_input.value = e.files[0].path
            target_input.update()
        elif e.path:
            target_input.value = e.path
            target_input.update()

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)

    def pick_file(input_field):
        nonlocal target_input
        target_input = input_field
        file_picker.pick_files(dialog_title="Выберите файл")

    def pick_folder(input_field):
        nonlocal target_input
        target_input = input_field
        file_picker.get_directory_path(dialog_title="Выберите папку")

    path1_field = ft.TextField(expand=True, label="Путь")
    path1_row = ft.Row([
        path1_field,
        ft.IconButton(icon=ft.icons.INSERT_DRIVE_FILE, tooltip="Выбрать файл", on_click=lambda _: pick_file(path1_field)),
        ft.IconButton(icon=ft.icons.FOLDER, tooltip="Выбрать папку", on_click=lambda _: pick_folder(path1_field)),
    ], visible=False)

    path2_field = ft.TextField(expand=True, label="Куда")
    path2_row = ft.Row([
        path2_field,
        ft.IconButton(icon=ft.icons.INSERT_DRIVE_FILE, tooltip="Выбрать файл", on_click=lambda _: pick_file(path2_field)),
        ft.IconButton(icon=ft.icons.FOLDER, tooltip="Выбрать папку", on_click=lambda _: pick_folder(path2_field)),
    ], visible=False)

    pattern_field = ft.TextField(label="Регулярное выражение", expand=True, visible=False, tooltip="Например: \\.py$ для поиска файлов Python")
    recursive_checkbox = ft.Checkbox(label="Рекурсивно (искать во вложенных папках)", visible=False)

    def update_ui(e=None):
        cmd = dropdown.value
        path1_row.visible = False
        path2_row.visible = False
        pattern_field.visible = False
        recursive_checkbox.visible = False

        if cmd == "copy":
            path1_row.visible = True
            path1_field.label = "Что копируем (исходный файл)"
            path2_row.visible = True
            path2_field.label = "Куда копируем (путь назначения)"
        elif cmd in ["delete", "count", "analyse"]:
            path1_row.visible = True
            path1_field.label = "Укажите путь к файлу или папке"
        elif cmd == "search":
            path1_row.visible = True
            path1_field.label = "Где ищем (папка)"
            pattern_field.visible = True
        elif cmd == "add-date":
            path1_row.visible = True
            path1_field.label = "Укажите путь к файлу или папке"
            recursive_checkbox.visible = True
        elif cmd == "backup":
            path1_row.visible = True
            path1_field.label = "Что бэкапим (файл/папка)"
            path2_row.visible = True
            path2_field.label = "Имя архива (например: backup.zip)"

        page.update()

    dropdown = ft.Dropdown(
        label="Выберите инструмент",
        options=[
            ft.dropdown.Option("copy", "Копирование (copy)"),
            ft.dropdown.Option("delete", "Удаление (delete)"),
            ft.dropdown.Option("count", "Подсчет файлов (count)"),
            ft.dropdown.Option("search", "Поиск (search)"),
            ft.dropdown.Option("add-date", "Добавление даты (add-date)"),
            ft.dropdown.Option("analyse", "Анализ размеров (analyse)"),
            ft.dropdown.Option("backup", "Бэкап в ZIP (backup)"),
        ],
        on_change=update_ui,
        width=300,
        autofocus=True,
    )
    dropdown.value = "copy"

    def execute_command(e):
        cmd = dropdown.value
        console_output.value = ""
        page.update()

        try:
            if path1_row.visible and not path1_field.value:
                raise ValueError("Пожалуйста, заполните основное поле пути.")

            if cmd == "copy":
                if not path2_field.value: raise ValueError("Укажите путь назначения.")
                operations.copy_file(path1_field.value, path2_field.value)
                show_message("Файл успешно скопирован!")

            elif cmd == "delete":
                operations.delete_item(path1_field.value)
                show_message("Удаление завершено успешно.")

            elif cmd == "count":
                count = operations.count_files(path1_field.value)
                show_message(f"Подсчет завершен. Найдено файлов: {count}")

            elif cmd == "search":
                if not pattern_field.value: raise ValueError("Укажите регулярное выражение.")
                operations.search_files(path1_field.value, pattern_field.value)
                show_message("Поиск завершен.")

            elif cmd == "add-date":
                operations.add_date(path1_field.value, recursive_checkbox.value)
                show_message("Даты успешно добавлены к именам.")

            elif cmd == "analyse":
                operations.analyse_directory(path1_field.value)
                show_message("Анализ завершен.")

            elif cmd == "backup":
                if not path2_field.value: raise ValueError("Укажите имя архива.")
                operations.create_backup(path1_field.value, path2_field.value)
                show_message("Бэкап успешно создан!")

        except Exception as ex:
            error_msg = f"Ошибка: {str(ex)}"
            write_to_console(f"\n{error_msg}\n")
            write_to_console(traceback.format_exc())
            show_message(error_msg, is_error=True)

    execute_btn = ft.ElevatedButton(
        "Заполнить и Запустить", 
        icon=ft.icons.PLAY_ARROW, 
        on_click=execute_command, 
        width=300, 
        style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE)
    )

    update_ui()
    
    page.add(
        ft.Text("Файловый Менеджер", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        dropdown,
        path1_row,
        path2_row,
        pattern_field,
        recursive_checkbox,
        ft.Container(height=10),
        execute_btn,
        ft.Divider(),
        console_output
    )

def start():
    ft.app(target=main_gui)

if __name__ == "__main__":
    start()