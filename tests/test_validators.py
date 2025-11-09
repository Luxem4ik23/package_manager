"""Тесты для модуля validators."""

import pytest
import os
import tempfile
import sys
import os

# Добавляем корень проекта в путь для импортов
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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


class TestValidatePackageName:
    """Тесты для функции validate_package_name."""

    def test_valid_package_names(self):
        """Тестирование валидных имен пакетов."""
        assert validate_package_name("bash") == "bash"
        assert validate_package_name("python3") == "python3"
        assert validate_package_name("my-package") == "my-package"

    def test_invalid_package_names(self):
        """Тестирование невалидных имен пакетов."""
        with pytest.raises(ValueError):
            validate_package_name("")

        with pytest.raises(ValueError):
            validate_package_name("invalid@name")


class TestValidateRepository:
    """Тесты для функции validate_repository."""

    def test_valid_url(self):
        """Тестирование валидных URL."""
        url = "https://example.com/repo"
        assert validate_repository(url) == url

    def test_valid_local_path(self):
        """Тестирование валидных локальных путей."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_repository(temp_dir)
            assert os.path.isabs(result)


class TestValidateMode:
    """Тесты для функции validate_mode."""

    def test_valid_modes(self):
        """Тестирование валидных режимов работы."""
        assert validate_mode("local") == "local"
        assert validate_mode("remote") == "remote"
        assert validate_mode("mixed") == "mixed"

    def test_invalid_modes(self):
        """Тестирование невалидных режимов работы."""
        with pytest.raises(ValueError):
            validate_mode("invalid")


class TestValidateVersion:
    """Тесты для функции validate_version."""

    def test_valid_versions(self):
        """Тестирование валидных версий."""
        assert validate_version("1.0") == "1.0"
        assert validate_version("2.1.3") == "2.1.3"

    def test_invalid_versions(self):
        """Тестирование невалидных версий."""
        with pytest.raises(ValueError):
            validate_version("1")


class TestValidateOutputFile:
    """Тесты для функции validate_output_file."""

    def test_valid_output_files(self):
        """Тестирование валидных имен файлов."""
        assert validate_output_file("graph.png") == "graph.png"
        assert validate_output_file("output.svg") == "output.svg"

    def test_invalid_output_files(self):
        """Тестирование невалидных имен файлов."""
        with pytest.raises(ValueError):
            validate_output_file("graph.pdf")


class TestValidateAsciiMode:
    """Тесты для функции validate_ascii_mode."""

    def test_valid_ascii_modes(self):
        """Тестирование валидных значений ASCII-режима."""
        assert validate_ascii_mode("yes") == "yes"
        assert validate_ascii_mode("no") == "no"

    def test_invalid_ascii_modes(self):
        """Тестирование невалидных значений ASCII-режима."""
        with pytest.raises(ValueError):
            validate_ascii_mode("invalid")


class TestValidateMaxDepth:
    """Тесты для функции validate_max_depth."""

    def test_valid_max_depth(self):
        """Тестирование валидных значений глубины."""
        assert validate_max_depth("1") == 1
        assert validate_max_depth("5") == 5

    def test_invalid_max_depth(self):
        """Тестирование невалидных значений глубины."""
        with pytest.raises(ValueError):
            validate_max_depth("not_a_number")


class TestValidateFilter:
    """Тесты для функции validate_filter."""

    def test_valid_filters(self):
        """Тестирование валидных фильтров."""
        assert validate_filter("") == ""
        assert validate_filter("lib") == "lib"

    def test_invalid_filters(self):
        """Тестирование невалидных фильтров."""
        with pytest.raises(ValueError):
            validate_filter("a")