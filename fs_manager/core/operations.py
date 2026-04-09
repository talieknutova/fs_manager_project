import os
import shutil
import re
from datetime import datetime
import logging

def copy_file(source: str, destination: str) -> None:
    """Копирует файл из source в destination."""
    if not os.path.exists(source):
        raise FileNotFoundError(f"Файл {source} не найден.")
    if os.path.isdir(source):
        raise IsADirectoryError(f"{source} является директорией. Используйте другую команду для папок.")
    
    shutil.copy2(source, destination)
    logging.info(f"Файл успешно скопирован: {source} -> {destination}")

def delete_item(path: str) -> None:
    """Удаляет файл или папку."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь {path} не найден.")
    
    if os.path.isfile(path):
        os.remove(path)
        logging.info(f"Файл удален: {path}")
    elif os.path.isdir(path):
        shutil.rmtree(path)
        logging.info(f"Папка удалена: {path}")

def count_files(path: str) -> int:
    """Подсчитывает количество файлов в папке (включая вложенные)."""
    if not os.path.exists(path) or not os.path.isdir(path):
        raise NotADirectoryError(f"Путь {path} не является директорией.")
    
    count = 0
    for root, _, files in os.walk(path):
        count += len(files)
    
    logging.info(f"Найдено файлов: {count} в папке {path}")
    return count

def search_files(path: str, pattern: str) -> list:
    """Ищет файлы по регулярному выражению."""
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Путь {path} не является директорией.")
    
    matched_files = []
    regex = re.compile(pattern)
    
    for root, _, files in os.walk(path):
        for file in files:
            if regex.search(file):
                full_path = os.path.join(root, file)
                matched_files.append(full_path)
                
    logging.info(f"Найдено {len(matched_files)} файлов по фильтру '{pattern}'")
    for f in matched_files:
        logging.info(f" - {f}")
    return matched_files

def _add_date_to_single_file(file_path: str) -> None:
    """Вспомогательная функция для переименования одного файла."""
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)

    timestamp = os.path.getctime(file_path)
    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    
    new_name = f"{date_str}_{base_name}"
    new_path = os.path.join(dir_name, new_name)
    
    os.rename(file_path, new_path)
    logging.info(f"Переименован: {base_name} -> {new_name}")

def add_date(path: str, recursive: bool = False) -> None:
    """Добавляет дату создания в имя файла(ов)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь {path} не найден.")
    
    if os.path.isfile(path):
        _add_date_to_single_file(path)
    elif os.path.isdir(path):
        if recursive:
            for root, _, files in os.walk(path):
                for file in files:
                    _add_date_to_single_file(os.path.join(root, file))
        else:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    _add_date_to_single_file(item_path)

def format_size(size_bytes: int) -> str:
    """Форматирует байты в читабельный вид."""
    for unit in ['b', 'kb', 'mb', 'gb', 'tb']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0

def get_size(path: str) -> int:
    """Получает размер файла или папки в байтах."""
    if os.path.isfile(path):
        return os.path.getsize(path)
    
    total_size = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def analyse_directory(path: str) -> None:
    """Анализирует размер папки и ее содержимого на первом уровне."""
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Путь {path} не является директорией.")
    
    total_size = get_size(path)
    print(f"full size: {format_size(total_size)}")
    
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        item_size = get_size(item_path)
        print(f"- {item:<20} {format_size(item_size)}")

def create_backup(path: str, archive_name: str) -> None:
    """ДОПОЛНИТЕЛЬНАЯ ФИЧА: Создает zip-архив файла или папки."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Путь {path} не найден.")

    base_name = archive_name.replace('.zip', '')
    
    if os.path.isdir(path):
        shutil.make_archive(base_name, 'zip', path)
    else:
        dir_name = os.path.dirname(path)
        temp_dir = os.path.join(dir_name, "temp_backup_dir")
        os.makedirs(temp_dir, exist_ok=True)
        shutil.copy2(path, temp_dir)
        shutil.make_archive(base_name, 'zip', temp_dir)
        shutil.rmtree(temp_dir)
        
    logging.info(f"Бэкап успешно создан: {base_name}.zip")