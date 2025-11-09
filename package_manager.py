"""Модуль для работы с пакетами Ubuntu (APT)."""

import re
import requests
from urllib.parse import urlparse, urljoin
from typing import List, Dict
import gzip
import io


class UbuntuPackageManager:
    """Класс для управления пакетами Ubuntu и их зависимостями."""

    def __init__(self, repository_url: str):
        self.repository_url = repository_url
        self.package_cache = {}

    def _download_packages_file(self) -> str:
        """Скачивает файл Packages.gz и распаковывает его."""
        # Рабочие URL для Ubuntu 20.04 LTS (Focal Fossa)
        packages_urls = [
            # Main repository
            "http://archive.ubuntu.com/ubuntu/dists/focal/main/binary-amd64/Packages.gz",
            "http://archive.ubuntu.com/ubuntu/dists/focal/universe/binary-amd64/Packages.gz",
            # Security updates
            "http://security.ubuntu.com/ubuntu/dists/focal-security/main/binary-amd64/Packages.gz",
            # Ports for different architectures
            "http://ports.ubuntu.com/ubuntu-ports/dists/focal/main/binary-amd64/Packages.gz",
        ]

        for packages_url in packages_urls:
            print(f"Попытка загрузки: {packages_url}")

            try:
                response = requests.get(packages_url, timeout=30)
                if response.status_code == 200:
                    print(f"✅ Файл успешно загружен ({len(response.content)} bytes)")

                    # Распаковываем .gz файл
                    with gzip.open(io.BytesIO(response.content), 'rt', encoding='utf-8') as f:
                        content = f.read()
                        print(f"Распаковано {len(content)} символов")
                        return content
                else:
                    print(f"❌ HTTP {response.status_code} для {packages_url}")

            except Exception as e:
                print(f"❌ Ошибка: {e}")
                continue

        raise Exception("Не удалось загрузить файл Packages ни из одного источника")

    def _parse_packages_file(self, content: str) -> Dict:
        """Парсит содержимое файла Packages."""
        packages = {}
        current_package = {}
        package_count = 0

        for line in content.split('\n'):
            if line == '':
                if current_package and 'Package' in current_package:
                    package_name = current_package['Package']
                    packages[package_name] = {
                        'name': package_name,
                        'version': current_package.get('Version', ''),
                        'description': current_package.get('Description', ''),
                        'depends': self._parse_dependencies(current_package.get('Depends', '')),
                        'pre_depends': self._parse_dependencies(current_package.get('Pre-Depends', '')),
                        'architecture': current_package.get('Architecture', '')
                    }
                    package_count += 1
                current_package = {}
            else:
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    # Для многострочных описаний
                    if key in current_package and key in ['Description']:
                        current_package[key] += '\n' + value
                    else:
                        current_package[key] = value

        print(f"Успешно распаршено {package_count} пакетов")
        return packages

    def _parse_dependencies(self, deps_string: str) -> List[str]:
        """Парсит строку зависимостей."""
        if not deps_string:
            return []

        dependencies = []

        for dep_group in deps_string.split(','):
            dep_group = dep_group.strip()
            if not dep_group:
                continue

            # Обрабатываем альтернативы (разделенные |)
            alternatives = dep_group.split('|')
            first_alternative = alternatives[0].strip()

            # Убираем версии и условия
            clean_dep = first_alternative.split(' ')[0].split('(')[0].strip()

            if clean_dep and clean_dep not in dependencies:
                dependencies.append(clean_dep)

        return dependencies

    def get_package_dependencies(self, package_name: str, version: str) -> List[str]:
        """Получает зависимости пакета."""
        if not self.package_cache:
            print("🔍 Загрузка данных о пакетах...")
            content = self._download_packages_file()
            self.package_cache = self._parse_packages_file(content)

        package_info = self._find_package(package_name, version)

        # Объединяем обычные и pre-зависимости
        all_dependencies = package_info['depends'] + package_info['pre_depends']
        return all_dependencies

    def get_package_info(self, package_name: str, version: str) -> Dict:
        """Получает информацию о пакете."""
        if not self.package_cache:
            content = self._download_packages_file()
            self.package_cache = self._parse_packages_file(content)

        return self._find_package(package_name, version)

    def _find_package(self, package_name: str, version: str) -> Dict:
        """Находит пакет в кэше."""
        # Прямой поиск
        if package_name in self.package_cache:
            pkg_info = self.package_cache[package_name]
            print(f"✅ Найден пакет {package_name} версии {pkg_info['version']}")
            return pkg_info

        # Поиск похожих пакетов
        similar = [pkg for pkg in self.package_cache.keys() if package_name.lower() in pkg.lower()]

        if similar:
            raise Exception(f"Пакет '{package_name}' не найден. Похожие пакеты: {', '.join(similar[:5])}")
        else:
            # Покажем несколько случайных пакетов для примера
            available = list(self.package_cache.keys())[:10]
            raise Exception(f"Пакет '{package_name}' не найден. Примеры доступных пакетов: {', '.join(available)}")