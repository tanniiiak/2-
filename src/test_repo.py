"""Чтение графа из тестового файла."""

from typing import Dict, List
from src.errors import ConfigError


class TestRepositoryError(ConfigError):
    """Ошибка чтения тестового репозитория."""


def load_test_repo(path: str) -> Dict[str, List[str]]:
    """Загружает граф зависимостей из текстового файла."""
    graph = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                pkg = parts[0]
                deps = parts[1:] if len(parts) > 1 else []
                graph[pkg] = deps
    except Exception as exc:
        raise TestRepositoryError(f"Ошибка чтения файла: {exc}") from exc
    return graph