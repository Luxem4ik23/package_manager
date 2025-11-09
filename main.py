"""Основной модуль CLI-приложения для визуализации зависимостей пакетов."""

import argparse
import sys
import json
from validators import (
    validate_package_name,
    validate_repository,
    validate_mode,
    validate_version,
    validate_output_file,
    validate_ascii_mode,
    validate_max_depth,
    validate_filter
)
from package_manager import UbuntuPackageManager


def setup_argparse() -> argparse.ArgumentParser:
    """Настраивает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Ubuntu - Этап 2"
    )

    parser.add_argument(
        "--package",
        required=True,
        help="Имя анализируемого пакета"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="URL или путь к тестовому репозиторию"
    )
    parser.add_argument(
        "--mode",
        required=True,
        help="Режим работы с репозиторием (local, remote, mixed)"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Версия пакета (X.Y или X.Y.Z)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Имя сгенерированного файла графа (.png/.jpg/.svg)"
    )
    parser.add_argument(
        "--ascii",
        default="no",
        help="Вывод зависимостей в ASCII-дереве (yes/no)"
    )
    parser.add_argument(
        "--max-depth",
        default="5",
        help="Максимальная глубина анализа зависимостей"
    )
    parser.add_argument(
        "--filter",
        default="",
        help="Подстрока для фильтрации пакетов"
    )

    return parser


def print_configuration(args):
    """Выводит конфигурацию приложения."""
    print("\n=== Конфигурация CLI-приложения ===")
    print(f"Имя анализируемого пакета    : {args.package}")
    print(f"Репозиторий                  : {args.repo}")
    print(f"Режим работы                 : {args.mode}")
    print(f"Версия пакета                : {args.version}")
    print(f"Файл графа                   : {args.output}")
    print(f"ASCII-дерево                 : {args.ascii}")
    print(f"Максимальная глубина         : {args.max_depth}")
    print(f"Фильтр пакетов               : {args.filter or '(не задан)'}")
    print("===================================")


def run_stage_2(package: str, repo: str, version: str):
    """Выполняет этап 2 - сбор данных о зависимостях.

    Args:
        package: Имя пакета
        repo: URL репозитория
        version: Версия пакета
    """
    print(f"\n=== Этап 2: Сбор данных о зависимостях пакета {package} ===")

    # Используем Ubuntu Package Manager
    package_manager = UbuntuPackageManager(repo)

    # Получаем информацию о пакете
    package_info = package_manager.get_package_info(package, version)
    dependencies = package_manager.get_package_dependencies(package, version)

    print(f"\n Информация о пакете {package}:")
    print(f"   Версия: {package_info['version']}")
    print(f"   Архитектура: {package_info['architecture']}")
    print(f"   Описание: {package_info['description'][:100]}...")

    print(f"\n Прямые зависимости пакета {package}:")
    if dependencies:
        for i, dep in enumerate(dependencies, 1):
            print(f"   {i}. {dep}")
    else:
        print("   ✅ Пакет не имеет зависимостей")

    return package_info, dependencies


def save_dependencies_data(package: str, version: str, dependencies: list, package_info: dict):
    """Сохраняет данные о зависимостях в JSON файл.

    Args:
        package: Имя пакета
        version: Версия пакета
        dependencies: Список зависимостей
        package_info: Информация о пакете
    """
    dependency_data = {
        'package': package,
        'version': version,
        'dependencies': dependencies,
        'package_info': package_info
    }

    with open('dependencies.json', 'w', encoding='utf-8') as f:
        json.dump(dependency_data, f, indent=2, ensure_ascii=False)

    print(f"\n Данные сохранены в dependencies.json для использования в следующих этапах")


def main():
    """Основная функция приложения."""
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Валидация входных параметров
        package = validate_package_name(args.package)
        repo = validate_repository(args.repo)
        mode = validate_mode(args.mode)
        version = validate_version(args.version)
        output = validate_output_file(args.output)
        ascii_mode = validate_ascii_mode(args.ascii)
        max_depth = validate_max_depth(args.max_depth)
        substring = validate_filter(args.filter)

        print_configuration(args)

        # Этап 2: Сбор данных о зависимостях
        package_info, dependencies = run_stage_2(package, repo, version)

        # Сохранение результатов
        save_dependencies_data(package, version, dependencies, package_info)

        print(f"\n Этап 2 завершен успешно!")
        print(f" Найдено зависимостей: {len(dependencies)}")

    except ValueError as e:
        print(f"\n❌ Ошибка валидации параметров: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()