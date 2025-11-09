"""Модуль для построения графа зависимостей."""

from typing import Dict, List, Set, Optional
from package_manager import UbuntuPackageManager


class DependencyGraph:
    """Класс для построения и анализа графа зависимостей."""

    def __init__(self, package_manager: UbuntuPackageManager):
        self.package_manager = package_manager
        self.visited = set()
        self.cycle_detected = False

    def build_dependency_graph(self,
                               package_name: str,
                               version: str,
                               max_depth: int = 5,
                               filter_substring: str = "") -> Dict:
        """Строит граф зависимостей с помощью DFS.

        Args:
            package_name: Имя корневого пакета
            version: Версия пакета
            max_depth: Максимальная глубина рекурсии
            filter_substring: Подстрока для фильтрации пакетов

        Returns:
            Словарь с графом зависимостей
        """
        self.visited = set()
        self.cycle_detected = False

        graph = {
            'root': package_name,
            'dependencies': {},
            'cycles': [],
            'filtered_count': 0
        }

        print(f"🔍 Построение графа зависимостей для {package_name}...")
        self._dfs_build_graph(package_name, version, graph['dependencies'],
                              max_depth, 0, filter_substring, [])

        if self.cycle_detected:
            print("⚠️  Обнаружены циклические зависимости!")
        else:
            print("✅ Циклические зависимости не обнаружены")

        return graph

    def _dfs_build_graph(self,
                         package_name: str,
                         version: str,
                         graph_node: Dict,
                         max_depth: int,
                         current_depth: int,
                         filter_substring: str,
                         path: List[str]) -> None:
        """Рекурсивно строит граф с помощью DFS.

        Args:
            package_name: Имя текущего пакета
            version: Версия пакета
            graph_node: Текущий узел графа
            max_depth: Максимальная глубина
            current_depth: Текущая глубина
            filter_substring: Подстрока для фильтрации
            path: Текущий путь для обнаружения циклов
        """
        if current_depth > max_depth:
            return

        # Проверка на циклы
        if package_name in path:
            cycle = path[path.index(package_name):] + [package_name]
            cycle_str = " -> ".join(cycle)
            print(f" Обнаружен цикл: {cycle_str}")
            self.cycle_detected = True
            graph_node['cycle'] = cycle_str
            return

        current_path = path + [package_name]

        try:
            # Получаем информацию о пакете
            package_info = self.package_manager.get_package_info(package_name, version)
            dependencies = self.package_manager.get_package_dependencies(package_name, version)

            # Заполняем информацию о текущем пакете
            graph_node['package'] = package_name
            graph_node['version'] = package_info['version']
            graph_node['depth'] = current_depth
            graph_node['dependencies'] = {}

            print(f"{'  ' * current_depth} {package_name} (глубина {current_depth})")

            # Фильтрация зависимостей
            filtered_dependencies = []
            for dep in dependencies:
                if filter_substring and filter_substring.lower() in dep.lower():
                    print(f"{'  ' * (current_depth + 1)} Отфильтровано: {dep}")
                    graph_node['filtered_count'] = graph_node.get('filtered_count', 0) + 1
                    continue
                filtered_dependencies.append(dep)

            if not filtered_dependencies:
                print(f"{'  ' * (current_depth + 1)}✅ Нет зависимостей")
                return

            # Рекурсивный обход зависимостей
            for dep in filtered_dependencies:
                print(f"{'  ' * (current_depth + 1)}🔗 Зависимость: {dep}")

                if dep not in graph_node['dependencies']:
                    graph_node['dependencies'][dep] = {}

                    # Рекурсивный вызов для зависимости
                    self._dfs_build_graph(dep, "", graph_node['dependencies'][dep],
                                          max_depth, current_depth + 1,
                                          filter_substring, current_path)

        except Exception as e:
            graph_node['error'] = str(e)
            print(f"{'  ' * current_depth}❌ Ошибка для {package_name}: {e}")

    def print_ascii_tree(self, graph: Dict, indent: int = 0) -> None:
        """Выводит граф в виде ASCII-дерева.

        Args:
            graph: Граф зависимостей
            indent: Уровень отступа
        """
        if not graph or not isinstance(graph, dict):
            return

        try:
            # Выводим информацию о текущем пакете
            if 'package' in graph:
                package_name = graph['package']
                version = graph.get('version', '')
                version_str = f" ({version})" if version else ""
                prefix = "    " * indent
                print(f"{prefix} {package_name}{version_str}")

            # Обрабатываем ошибки
            if 'error' in graph:
                error_prefix = "    " * (indent + 1)
                print(f"{error_prefix}❌ {graph['error']}")
                return

            # Обрабатываем циклы
            if 'cycle' in graph:
                cycle_prefix = "    " * (indent + 1)
                print(f"{cycle_prefix} Цикл: {graph['cycle']}")
                return

            # Обрабатываем зависимости
            if 'dependencies' in graph and isinstance(graph['dependencies'], dict):
                deps = graph['dependencies']
                dep_names = list(deps.keys())

                for i, dep_name in enumerate(dep_names):
                    dep_graph = deps[dep_name]
                    is_last = i == len(dep_names) - 1
                    prefix = "    " * indent + ("└── " if is_last else "├── ")

                    print(f"{prefix}{dep_name}")

                    # Рекурсивно обрабатываем поддерево зависимости
                    if isinstance(dep_graph, dict):
                        new_indent = indent + 1
                        self.print_ascii_tree(dep_graph, new_indent)

        except Exception as e:
            print(f"❌ Ошибка при выводе дерева: {e}")

    def get_statistics(self, graph: Dict) -> Dict:
        """Возвращает статистику по графу.

        Args:
            graph: Граф зависимостей

        Returns:
            Словарь со статистикой
        """

        def count_nodes(node):
            if not node:
                return 0, 0

            total = 1
            errors = 1 if 'error' in node else 0
            cycles = 1 if 'cycle' in node else 0

            if 'dependencies' in node:
                for dep in node['dependencies'].values():
                    dep_total, dep_errors, dep_cycles = count_nodes(dep)
                    total += dep_total
                    errors += dep_errors
                    cycles += dep_cycles

            return total, errors, cycles

        total, errors, cycles = count_nodes(graph.get('dependencies', {}))

        return {
            'total_packages': total,
            'root_package': graph.get('root', ''),
            'max_depth_reached': self._get_max_depth(graph),
            'errors_count': errors,
            'cycles_count': cycles,
            'filtered_count': graph.get('filtered_count', 0)
        }

    def _get_max_depth(self, graph: Dict) -> int:
        """Находит максимальную глубину графа."""

        def find_depth(node, current_depth):
            max_depth = current_depth
            if 'dependencies' in node:
                for dep in node['dependencies'].values():
                    max_depth = max(max_depth, find_depth(dep, current_depth + 1))
            return max_depth

        return find_depth(graph.get('dependencies', {}), 0)