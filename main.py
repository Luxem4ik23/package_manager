"""Основной модуль CLI-приложения для визуализации зависимостей пакетов."""

import argparse
import sys
import json
import os
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
from dependency_graph import DependencyGraph


def setup_argparse() -> argparse.ArgumentParser:
    """Настраивает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Ubuntu - Этап 3"
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
    """Выполняет этап 2 - сбор данных о зависимостях."""
    print(f"\n=== Этап 2: Сбор данных о зависимостях пакета {package} ===")

    package_manager = UbuntuPackageManager(repo)
    package_info = package_manager.get_package_info(package, version)
    dependencies = package_manager.get_package_dependencies(package, version)

    print(f"\n📦 Информация о пакете {package}:")
    print(f"   Версия: {package_info['version']}")
    print(f"   Архитектура: {package_info['architecture']}")
    print(f"   Описание: {package_info['description'][:100]}...")

    print(f"\n🔗 Прямые зависимости пакета {package}:")
    if dependencies:
        for i, dep in enumerate(dependencies, 1):
            print(f"   {i}. {dep}")
    else:
        print("   ✅ Пакет не имеет зависимостей")

    return package_manager, package_info, dependencies


def run_stage_3(package_manager: UbuntuPackageManager,
                package: str,
                version: str,
                max_depth: int,
                filter_substring: str,
                ascii_mode: str):
    """Выполняет этап 3 - построение графа зависимостей."""
    print(f"\n=== Этап 3: Построение графа зависимостей ===")
    print(f"Максимальная глубина: {max_depth}")
    print(f"Фильтр: '{filter_substring}'" if filter_substring else "Фильтр: не задан")

    # Строим граф зависимостей
    graph_builder = DependencyGraph(package_manager)
    dependency_graph = graph_builder.build_dependency_graph(
        package, version, max_depth, filter_substring
    )

    # Выводим ASCII-дерево если нужно
    if ascii_mode == "yes":
        print(f"\n🌳 Дерево зависимостей пакета {package}:")
        print("=" * 50)
        graph_builder.print_ascii_tree(dependency_graph.get('dependencies', {}))
        print("=" * 50)

    # Выводим статистику
    stats = graph_builder.get_statistics(dependency_graph)
    print(f"\n📊 Статистика графа:")
    print(f"   Всего пакетов: {stats['total_packages']}")
    print(f"   Максимальная глубина: {stats['max_depth_reached']}")
    print(f"   Ошибок: {stats['errors_count']}")
    print(f"   Циклов: {stats['cycles_count']}")
    print(f"   Отфильтровано: {stats['filtered_count']}")

    return dependency_graph, stats


def save_dependencies_data(package: str, version: str, graph: dict, stats: dict):
    """Сохраняет данные о зависимостях в JSON файл."""
    dependency_data = {
        'package': package,
        'version': version,
        'graph': graph,
        'statistics': stats,
        'timestamp': str(__import__('datetime').datetime.now())
    }

    with open('dependencies.json', 'w', encoding='utf-8') as f:
        json.dump(dependency_data, f, indent=2, ensure_ascii=False)

    print(f"\n Данные сохранены в dependencies.json")


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
        filter_substring = validate_filter(args.filter)

        print_configuration(args)

        # Этап 2: Сбор данных о зависимостях
        package_manager, package_info, dependencies = run_stage_2(package, repo, version)

        # Этап 3: Построение графа зависимостей
        dependency_graph, stats = run_stage_3(
            package_manager, package, version, max_depth,
            filter_substring, ascii_mode
        )

        # Сохранение результатов
        save_dependencies_data(package, version, dependency_graph, stats)

        print(f"\n Все этапы завершены успешно!")
        print(f" Корневой пакет: {package}")
        print(f" Всего пакетов в графе: {stats['total_packages']}")

    except ValueError as e:
        print(f"\n❌ Ошибка валидации параметров: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()