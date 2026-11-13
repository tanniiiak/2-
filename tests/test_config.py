""""""Тесты загрузки и валидации конфигурации.""""""

from pathlib import Path

import pytest

from src.config import load_config
from src.errors import (
    ConfigFileNotFoundError,
    ConfigMissingFieldError,
    ConfigParseError,
    ConfigTypeError,
    ConfigValueError,
)

VALID_TEXT = (
    'package_name = ""openssl""\n'
    'repository_source = ""https://example.org/main""\n'
    'work_mode = ""online""\n'
    'filter_substring = ""-dev""\n'
)


def write_config(tmp_path: Path, text: str) -> Path:
    """"""Пишет TOML-текст во временный файл.""""""
    path = tmp_path / ""config.toml""
    path.write_text(text, encoding=""utf-8"")
    return path


def test_valid_config(tmp_path: Path) -> None:
    config = load_config(write_config(tmp_path, VALID_TEXT))
    assert config.package_name == ""openssl""
    assert config.work_mode == ""online""


def test_valid_test_mode(tmp_path: Path) -> None:
    fake_repo = tmp_path / ""repo.txt""
    fake_repo.write_text(""A B\n"", encoding=""utf-8"")
    text = VALID_TEXT.replace(
        'repository_source = ""https://example.org/main""\n',
        f'repository_source = ""{fake_repo}""\n',
    ).replace(
        'work_mode = ""online""\n',
        'work_mode = ""test""\n',
    )
    config = load_config(write_config(tmp_path, text))
    assert config.work_mode == ""test""


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigFileNotFoundError):
        load_config(tmp_path / ""absent.toml"")


def test_invalid_toml(tmp_path: Path) -> None:
    path = write_config(tmp_path, ""package_name = \n"")
    with pytest.raises(ConfigParseError):
        load_config(path)


def test_missing_field(tmp_path: Path) -> None:
    text = VALID_TEXT.replace('filter_substring = ""-dev""\n', """")
    with pytest.raises(ConfigMissingFieldError):
        load_config(write_config(tmp_path, text))


@pytest.mark.parametrize(
    (""field_line"", ""new_line""),
    [
        ('package_name = ""openssl""\n', ""package_name = 1\n""),
        (
            'repository_source = ""https://example.org/main""\n',
            ""repository_source = 1\n"",
        ),
        ('work_mode = ""online""\n', ""work_mode = 1\n""),
        ('filter_substring = ""-dev""\n', ""filter_substring = 1\n""),
    ],
)
def test_wrong_type(
    tmp_path: Path,
    field_line: str,
    new_line: str,
) -> None:
    text = VALID_TEXT.replace(field_line, new_line)
    with pytest.raises(ConfigTypeError):
        load_config(write_config(tmp_path, text))


def test_empty_package_name(tmp_path: Path) -> None:
    text = VALID_TEXT.replace(
        'package_name = ""openssl""\n',
        'package_name = """"""\n',
    )
    with pytest.raises(ConfigValueError):
        load_config(write_config(tmp_path, text))


def test_empty_repository_source(tmp_path: Path) -> None:
    text = VALID_TEXT.replace(
        'repository_source = ""https://example.org/main""\n',
        'repository_source = """"""\n',
    )
    with pytest.raises(ConfigValueError):
        load_config(write_config(tmp_path, text))


def test_bad_work_mode(tmp_path: Path) -> None:
    text = VALID_TEXT.replace(
        'work_mode = ""online""\n',
        'work_mode = ""offline""\n',
    )
    with pytest.raises(ConfigValueError):
        load_config(write_config(tmp_path, text))


def test_bad_url_in_online_mode(tmp_path: Path) -> None:
    text = VALID_TEXT.replace(
        'repository_source = ""https://example.org/main""\n',
        'repository_source = ""ftp://example.org/main""\n',
    )
    with pytest.raises(ConfigValueError):
        load_config(write_config(tmp_path, text))


def test_test_mode_missing_file(tmp_path: Path) -> None:
    text = VALID_TEXT.replace(
        'repository_source = ""https://example.org/main""\n',
        'repository_source = ""/no/such/file.txt""\n',
    ).replace(
        'work_mode = ""online""\n',
        'work_mode = ""test""\n',
    )
    with pytest.raises(ConfigValueError):
        load_config(write_config(tmp_path, text))