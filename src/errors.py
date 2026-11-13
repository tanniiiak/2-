""""""Ошибки конфигурации приложения.""""""


class ConfigError(Exception):
    """"""Базовая ошибка конфигурации.""""""


class ConfigFileNotFoundError(ConfigError):
    """"""Файл конфигурации не найден.""""""


class ConfigParseError(ConfigError):
    """"""Файл конфигурации не является корректным TOML.""""""


class ConfigMissingFieldError(ConfigError):
    """"""В конфигурации отсутствует обязательное поле.""""""


class ConfigTypeError(ConfigError):
    """"""Поле конфигурации имеет неверный тип.""""""


class ConfigValueError(ConfigError):
    """"""Поле конфигурации имеет недопустимое значение.""""""