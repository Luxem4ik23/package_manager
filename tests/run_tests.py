"""Скрипт для запуска тестов."""

import subprocess
import sys
import os


def run_tests():
    """Запускает тесты и возвращает результат."""
    print("Запуск тестов для Этапа 1...")
    print("=" * 50)

    # Получаем путь к директории tests
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(tests_dir)

    print(f"Директория тестов: {tests_dir}")
    print(f"Корень проекта: {project_root}")

    try:
        # Меняем рабочую директорию на корень проекта
        os.chdir(project_root)

        # Запуск pytest с явным указанием пути
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short"
        ], capture_output=False)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Ошибка при запуске тестов: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()

    if success:
        print("\n✅ Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n❌ Некоторые тесты не прошли")
        sys.exit(1)