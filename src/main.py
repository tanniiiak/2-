""""""Точка входа CLI: вывод параметров в формате ключ-значение.""""""

import argparse
import sys
from pathlib import Path

from src.config import AppConfig, load_config
from src.errors import ConfigError

EXIT_OK = 0
EXIT_CONFIG_ERROR = 1
EXIT_USAGE_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """"""Собирает парсер аргументов командной строки.""""""
    parser = argparse.ArgumentParser(
        prog=""depviz"",
        description=""Визуализатор графа зависимостей (этап 1)."",
    )
    parser.add_argument(
        ""-c"",
        ""--config"",
        required=True,
        type=Path,
        help=""Путь к TOML-файлу конфигурации"",
    )
    return parser


def format_value(value: object) -> str:
    """"""Приводит значение к строке для вывода.""""""
    if isinstance(value, bool):
        return ""true"" if value else ""false""
    text = str(value)
    return text if text else ""<empty>""


def print_config(config: AppConfig) -> None:
    """"""Печатает все параметры в формате ключ=значение.""""""
    print(f""package_name={format_value(config.package_name)}"")
    print(
        ""repository_source=""
        f""{format_value(config.repository_source)}""
    )
    print(f""work_mode={format_value(config.work_mode)}"")
    print(
        ""filter_substring=""
        f""{format_value(config.filter_substring)}""
    )


def main(argv: list[str] | None = None) -> int:
    """"""Запускает приложение и возвращает код выхода.""""""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE_ERROR if exc.code else EXIT_OK

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f""Ошибка конфигурации: {exc}"", file=sys.stderr)
        return EXIT_CONFIG_ERROR

    print_config(config)
    return EXIT_OK


if __name__ == ""__main__"":
    raise SystemExit(main())