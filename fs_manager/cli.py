import argparse
import logging
import sys
from fs_manager.core import operations

def setup_logger():
    """Настройка базового логирования в консоль."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def main():
    setup_logger()
    
    parser = argparse.ArgumentParser(
        description="Менеджер файловой системы",
        epilog="Учебный проект для работы с ОС и Git."
    )
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    subparsers.required = True

    parser_copy = subparsers.add_parser("copy", help="Скопировать файл")
    parser_copy.add_argument("source", help="Путь к исходному файлу")
    parser_copy.add_argument("destination", help="Путь назначения")

    parser_delete = subparsers.add_parser("delete", help="Удалить файл или папку")
    parser_delete.add_argument("path", help="Путь к файлу или папке для удаления")

    parser_count = subparsers.add_parser("count", help="Подсчитать количество файлов в папке")
    parser_count.add_argument("path", help="Путь к папке")

    parser_search = subparsers.add_parser("search", help="Найти файлы по регулярному выражению")
    parser_search.add_argument("path", help="Путь к папке для поиска")
    parser_search.add_argument("pattern", help="Регулярное выражение")

    parser_add_date = subparsers.add_parser("add-date", help="Добавить дату создания в имя файла")
    parser_add_date.add_argument("path", help="Путь к файлу или папке")
    parser_add_date.add_argument("--recursive", action="store_true", help="Применить ко всем вложенным файлам (если выбрана папка)")

    parser_analyse = subparsers.add_parser("analyse", help="Анализ размеров файлов и папок")
    parser_analyse.add_argument("path", help="Путь к директории для анализа")

    parser_backup = subparsers.add_parser("backup", help="[Custom] Создать zip-архив файла или папки")
    parser_backup.add_argument("path", help="Путь к исходному файлу или папке")
    parser_backup.add_argument("archive_name", help="Имя создаваемого архива (с или без .zip)")

    args = parser.parse_args()

    try:
        if args.command == "copy":
            operations.copy_file(args.source, args.destination)
        elif args.command == "delete":
            operations.delete_item(args.path)
        elif args.command == "count":
            operations.count_files(args.path)
        elif args.command == "search":
            operations.search_files(args.path, args.pattern)
        elif args.command == "add-date":
            operations.add_date(args.path, args.recursive)
        elif args.command == "analyse":
            operations.analyse_directory(args.path)
        elif args.command == "backup":
            operations.create_backup(args.path, args.archive_name)
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()