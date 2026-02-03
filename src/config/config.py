import logging
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, DotEnvSettingsSource, YamlConfigSettingsSource


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None


class LoggerConfig(BaseModel):
    level: LogLevel = Field(LogLevel.INFO)

    @property
    def numeric_level(self) -> int:
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map[self.level]


class AppInfo(BaseModel):
    name: str
    version: int


from pydantic import BaseModel


class DBConfig(BaseModel):

    logging: bool = False

    # Размер пула постоянных соединений.
    pool_size: int = 5

    # Максимальное количество временных соединений сверх pool_size.
    max_overflow: int = 10

    # Время жизни соединения в секундах перед пересозданием.
    pool_recycle: int = 3600

    # Максимальное время ожидания свободного соединения (в секундах).
    pool_timeout: int = 30


class JwtConfig(BaseModel):
    algorithm: str = "HS256"
    time_expire: int = 30


class Config(BaseSettings):
    app: AppInfo
    db: DBConfig
    logger: LoggerConfig
    jwt: JwtConfig

    jwt_secret_key: str
    postgres_conn: str

    model_config = ConfigDict(extra="allow")

    def __init__(
        self,
        config_file_path: Path | None = None,
        _env_file_path: Path | None = None,
        **data,
    ):
        self._config_file_path = config_file_path or Path("./infra/config.yaml")
        self._env_file_path = _env_file_path or Path("./infra/.env")
        super().__init__(**data)

    def settings_customise_sources(self, settings_cls, **kwargs):
        return (
            DotEnvSettingsSource(
                settings_cls,
                env_file=self._env_file_path,
                env_file_encoding="utf-8",
            ),
            YamlConfigSettingsSource(settings_cls, self._config_file_path),
        )


config = Config()


def get_auth_data():
    return {
        "secret_key": config.jwt_secret_key,
        "algorithm": config.jwt.algorithm,
        "time_expire": config.jwt.time_expire,
    }
