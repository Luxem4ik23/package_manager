"""Минимальный CLI-прототип визуализатора графа зависимостей пакетов."""
import argparse
import sys
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


def main():
    parser = argparse.ArgumentParser(
        description="Этап 1 — минимальный CLI-прототип визуализации графа зависимостей"
    )

    # Обязательные параметры
    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--repo", required=True, help="URL или путь к тестовому репозиторию")
    parser.add_argument("--mode", required=True, help="Режим работы с репозиторием (local, remote, mixed)")
    parser.add_argument("--version", required=True, help="Версия пакета (X.Y или X.Y.Z)")
    parser.add_argument("--output", required=True, help="Имя сгенерированного файла графа (.png/.jpg/.svg)")

    # Необязательные параметры
    parser.add_argument("--ascii", default="no", help="Вывод зависимостей в ASCII-дереве (yes/no)")
    parser.add_argument("--max-depth", default="5", help="Максимальная глубина анализа зависимостей")
    parser.add_argument("--filter", default="", help="Подстрока для фильтрации пакетов")

    args = parser.parse_args()

    try:
        # Валидация всех параметров
        package = validate_package_name(args.package)
        repo = validate_repository(args.repo)
        mode = validate_mode(args.mode)
        version = validate_version(args.version)
        output = validate_output_file(args.output)
        ascii_mode = validate_ascii_mode(args.ascii)
        max_depth = validate_max_depth(args.max_depth)
        substring = validate_filter(args.filter)

        # Вывод всех параметров в формате ключ-значение
        print("\n=== Конфигурация CLI-приложения ===")
        print(f"Имя анализируемого пакета    : {package}")
        print(f"Репозиторий                  : {repo}")
        print(f"Режим работы                 : {mode}")
        print(f"Версия пакета                : {version}")
        print(f"Файл графа                   : {output}")
        print(f"ASCII-дерево                 : {ascii_mode}")
        print(f"Максимальная глубина         : {max_depth}")
        print(f"Фильтр пакетов               : {substring or '(не задан)'}")
        print("===================================")

        print("\n✅ Конфигурация успешно проверена! Этап 1 завершен.")
        print("ℹ️  На данном этапе выполняется только валидация параметров.")
        print("ℹ️  Функциональность анализа зависимостей будет реализована в следующих этапах.")

    except ValueError as e:
        print(f"\n❌ Ошибка валидации параметров: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()