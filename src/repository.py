"""Получение данных о зависимостях из APKINDEX."""

import io
import tarfile
import urllib.request
from typing import Dict, List

from src.errors import ConfigError


class RepositoryError(ConfigError):
    """Ошибка получения данных."""


def download_archive(url: str) -> bytes:
    """Скачивает файл архива по URL."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read()
    except Exception as exc:
        raise RepositoryError(f"Ошибка скачивания: {exc}") from exc


def parse_apkindex(data: str) -> Dict[str, Dict[str, str]]:
    """Парсит текст APKINDEX и возвращает словарь пакетов."""
    packages = {}
    current_pkg = {}

    lines = data.replace("\r\n", "\n").split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            if key == "P":
                if "P" in current_pkg:
                    packages[current_pkg["P"]] = current_pkg
                current_pkg = {"P": value}
            elif key == "D":
                current_pkg["D"] = value

    if "P" in current_pkg:
        packages[current_pkg["P"]] = current_pkg

    return packages


def extract_dependencies(url: str, package_name: str) -> List[str]:
    """Извлекает прямые зависимости для указанного пакета."""
    archive_data = download_archive(url)

    try:
        tar = tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz")
        apkindex_file = next(
            (m for m in tar.getmembers() if "APKINDEX" in m.name), None
        )
        if not apkindex_file:
            raise RepositoryError("APKINDEX не найден в архиве")

        f = tar.extractfile(apkindex_file)
        if not f:
            raise RepositoryError("Не удалось прочитать APKINDEX")

        text = f.read().decode("utf-8")
    except Exception as exc:
        raise RepositoryError(f"Ошибка распаковки: {exc}") from exc

    packages = parse_apkindex(text)
    if package_name not in packages:
        raise RepositoryError(f"Пакет {package_name} не найден")

    deps_str = packages[package_name].get("D", "")
    if not deps_str:
        return []

    deps = []
    for dep in deps_str.split():
        dep_name = dep.split("=")[0].split("<")[0].split(">")[0].strip()
        if dep_name:
            deps.append(dep_name)

    return deps