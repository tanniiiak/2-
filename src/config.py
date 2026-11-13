"""Загрузка и валидация TOML-конфигурации."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from src.errors import (
    ConfigFileNotFoundError,
    ConfigMissingFieldError,
    ConfigParseError,
    ConfigTypeError,
    ConfigValueError,
)

REQUIRED_FIELDS = (
    "package_name",
    "repository_source",
    "work_mode",
    "filter_substring",
)

ALLOWED_MODES = ("online", "test")

ONLINE_MODE = "online"
TEST_MODE = "test"


@dataclass(frozen=True)
class AppConfig:
    """Параметры, настраиваемые пользователем."""

    package_name: str
    repository_source: str
    work_mode: str
    filter_substring: str


def load_toml(path: Path) -> dict:
    """Читает TOML-файл и возвращает словарь."""
    if not path.is_file():
        raise ConfigFileNotFoundError(
            f"Файл конфигурации не найден: {path}"
        )
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigParseError(
            f"Некорректный TOML в {path}: {exc}"
        ) from exc


def check_required_fields(data: dict) -> None:
    """Проверяет наличие всех обязательных полей."""
    missing = [name for name in REQUIRED_FIELDS if name not in data]
    if missing:
        raise ConfigMissingFieldError(
            f"Отсутствуют поля: {', '.join(missing)}"
        )


def check_string_field(
    data: dict,
    name: str,
    allow_empty: bool,
) -> None:
    """Проверяет, что поле - строка."""
    value = data[name]
    if not isinstance(value, str):
        raise ConfigTypeError(
            f"Поле '{name}' должно быть строкой"
        )
    if not allow_empty and not value.strip():
        raise ConfigValueError(
            f"Поле '{name}' не должно быть пустым"
        )


def check_work_mode(data: dict) -> None:
    """Проверяет допустимость work_mode."""
    mode = data["work_mode"]
    if mode not in ALLOWED_MODES:
        raise ConfigValueError(
            "work_mode должен быть 'online' или 'test'"
        )


def check_online_source(data: dict) -> None:
    """В режиме online источник - валидный http(s)-URL."""
    source = data["repository_source"].strip()
    parsed = urlparse(source)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ConfigValueError(
            "В режиме online repository_source "
            "должен быть http(s)-URL"
        )


def check_test_source(data: dict) -> None:
    """В режиме test источник - существующий файл."""
    source = data["repository_source"].strip()
    if not Path(source).is_file():
        raise ConfigValueError(
            "В режиме test repository_source "
            f"должен указывать на файл: {source}"
        )


def validate(data: dict) -> AppConfig:
    """Полная валидация и сборка AppConfig."""
    check_required_fields(data)
    check_string_field(data, "package_name", allow_empty=False)
    check_string_field(data, "repository_source", allow_empty=False)
    check_string_field(data, "work_mode", allow_empty=False)
    check_string_field(data, "filter_substring", allow_empty=True)
    check_work_mode(data)
    if data["work_mode"] == ONLINE_MODE:
        check_online_source(data)
    else:
        check_test_source(data)
    return AppConfig(
        package_name=data["package_name"],
        repository_source=data["repository_source"],
        work_mode=data["work_mode"],
        filter_substring=data["filter_substring"],
    )


def load_config(path: Path) -> AppConfig:
    """Загружает TOML и возвращает валидную конфигурацию."""
    data = load_toml(path)
    return validate(data)