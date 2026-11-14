"""Алгоритм BFS для построения графа зависимостей."""

from collections import deque
from typing import Dict, List, Set


def bfs_dependencies(
    start_pkg: str,
    graph: Dict[str, List[str]],
    max_depth: int,
    filter_substr: str,
) -> List[str]:
    """Строит список зависимостей с помощью BFS (без рекурсии)."""
    visited: Set[str] = set()
    queue = deque([(start_pkg, 0)])
    result = []

    while queue:
        current, depth = queue.popleft()

        if current in visited:
            continue
        visited.add(current)

        if current != start_pkg:
            if filter_substr and filter_substr in current:
                continue
            result.append(current)

        if max_depth != -1 and depth >= max_depth:
            continue

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))

    return result
def reverse_graph(graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Переворачивает граф для поиска обратных зависимостей."""
    reversed_graph: Dict[str, List[str]] = {}
    for pkg, deps in graph.items():
        if pkg not in reversed_graph:
            reversed_graph[pkg] = []
        for dep in deps:
            if dep not in reversed_graph:
                reversed_graph[dep] = []
            reversed_graph[dep].append(pkg)
    return reversed_graph