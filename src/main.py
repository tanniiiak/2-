"""Точка входа CLI: вывод параметров в формате ключ-значение."""

import argparse
import sys
from pathlib import Path

from src.config import AppConfig, load_config
from src.errors import ConfigError
from src.bfs import bfs_dependencies

EXIT_OK = 0
EXIT_CONFIG_ERROR = 1
EXIT_USAGE_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Собирает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="depviz",
        description="Визуализатор графа (этап 1-3).",
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        type=Path,
        help="Путь к TOML-файлу",
    )
    return parser


def format_value(value: object) -> str:
    """Приводит значение к строке для вывода."""
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value)
    return text if text else "<empty>"


def print_config(config: AppConfig) -> None:
    """Печатает все параметры в формате ключ=значение."""
    print(f"package_name={format_value(config.package_name)}")
    print(
        "repository_source="
        f"{format_value(config.repository_source)}"
    )
    print(f"work_mode={format_value(config.work_mode)}")
    print(
        "filter_substring="
        f"{format_value(config.filter_substring)}"
    )
    print(f"max_depth={format_value(config.max_depth)}")


def main(argv: list[str] | None = None) -> int:
    """Запускает приложение и возвращает код выхода."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE_ERROR if exc.code else EXIT_OK

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return EXIT_CONFIG_ERROR

    print_config(config)
    print("---")
    
    graph = {}
    if config.work_mode == "online":
        from src.repository import extract_dependencies
        try:
            deps = extract_dependencies(
                config.repository_source, 
                config.package_name
            )
            graph[config.package_name] = deps
            for d in deps:
                graph[d] = []
        except Exception as exc:
            print(f"Ошибка: {exc}", file=sys.stderr)
            return EXIT_CONFIG_ERROR
    else:
        from src.test_repo import load_test_repo
        try:
            graph = load_test_repo(config.repository_source)
        except Exception as exc:
            print(f"Ошибка: {exc}", file=sys.stderr)
            return EXIT_CONFIG_ERROR

    print(f"Транзитивные зависимости {config.package_name} (BFS):")
    deps = bfs_dependencies(
        config.package_name,
        graph,
        config.max_depth,
        config.filter_substring
    )
    for dep in deps:
        print(f"  - {dep}")
            
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())