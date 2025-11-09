"""Функции валидации входных параметров CLI."""

import os
import re
from urllib.parse import urlparse


def validate_package_name(name: str) -> str:
    if not name:
        raise ValueError("Имя пакета не может быть пустым")

    if not re.match(r"^[a-zA-Z0-9._\-]+$", name):
        raise ValueError("Некорректное имя пакета. Допустимы буквы, цифры, _, - и .")

    return name


def validate_repository(url_or_path: str) -> str:
    if not url_or_path:
        raise ValueError("Репозиторий не может быть пустым")

    # Проверка локального пути
    if os.path.exists(url_or_path):
        return os.path.abspath(url_or_path)

    # Проверка URL
    parsed = urlparse(url_or_path)
    if parsed.scheme and parsed.netloc:
        return url_or_path

    raise ValueError("Некорректный путь или URL репозитория. Должен быть существующий путь или валидный URL")


def validate_mode(mode: str) -> str:
    valid_modes = ["local", "remote", "mixed"]

    if not mode:
        raise ValueError("Режим работы не может быть пустым")

    if mode not in valid_modes:
        raise ValueError(f"Некорректный режим работы. Доступные значения: {', '.join(valid_modes)}")

    return mode


def validate_version(version: str) -> str:
    if not version:
        raise ValueError("Версия пакета не может быть пустой")

    if not re.match(r"^[0-9]+\.[0-9]+(\.[0-9]+)?$", version):
        raise ValueError("Некорректная версия пакета. Формат: X.Y или X.Y.Z")

    return version


def validate_output_file(filename: str) -> str:
    if not filename:
        raise ValueError("Имя файла графа не может быть пустым")

    supported_formats = [".png", ".jpg", ".svg"]
    if not any(filename.endswith(fmt) for fmt in supported_formats):
        raise ValueError(f"Имя файла для графа должно оканчиваться на {', '.join(supported_formats)}")

    return filename


def validate_ascii_mode(value: str) -> str:
    if not value:
        raise ValueError("Параметр ASCII-вывода не может быть пустым")

    value_lower = value.lower()
    if value_lower not in ["yes", "no"]:
        raise ValueError("Режим вывода ASCII-дерева должен быть 'yes' или 'no'")

    return value_lower


def validate_max_depth(value: str) -> int:
    if not value:
        raise ValueError("Максимальная глубина не может быть пустой")

    try:
        depth = int(value)
        if depth <= 0:
            raise ValueError("Максимальная глубина должна быть положительным числом")
        return depth
    except ValueError:
        raise ValueError("Максимальная глубина должна быть целым числом")


def validate_filter(substring: str) -> str:
    # Пустой фильтр допустим
    if not substring:
        return ""

    if len(substring) < 2:
        raise ValueError("Фильтр должен содержать не менее 2 символов")

    return substring
