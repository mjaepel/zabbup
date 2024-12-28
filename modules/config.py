import logging
from argparse import ArgumentParser
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from modules.exceptions import NotAllowedValueError, UnknownConfigAttributeError, UnknownLogLevelError, ZabbixAuthConfigError
from modules.logger import get_logger, set_log_level

###################################################################


loglevel_map = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


###################################################################


class GeneralConfig(BaseModel):
    loglevel: str = "INFO"
    loglevel_numeric: int = logging.INFO
    dryrun: bool = False
    max_threads: int | None = 10
    encryption: bool = False
    encryption_key: str | None
    encryption_deterministic: bool = False

    @model_validator(mode="before")
    def convert_loglevel(cls, values: dict) -> dict:
        loglevel = values.get("loglevel")

        if loglevel:
            if loglevel.upper() not in loglevel_map:
                raise UnknownLogLevelError(loglevel, loglevel_map.keys())

            values["loglevel_numeric"] = loglevel_map[loglevel.upper()]
        return values


class ZabbixAuthConfig(BaseModel):
    user: str | None = None
    password: str | None = None
    token: str | None = None

    @model_validator(mode="before")
    def check_auth_fields(cls, values: dict) -> dict:
        if values.get("token") and (values.get("user") or values.get("password")):
            logger = get_logger()
            logger.warning("Both 'token' and 'user'/'password' are set. Using 'token' for authentication.")
            values["user"] = None
            values["password"] = None
        elif not values.get("token") and not (values.get("user") and values.get("password")):
            raise ZabbixAuthConfigError

        return values


class ZabbixConfig(BaseModel):
    url: str
    auth: ZabbixAuthConfig
    export_format: str | None = "yaml"

    @field_validator("export_format")
    def check_export_format(cls, value: str) -> str:
        allowed_formats = {"yaml", "json", "xml"}
        if value not in allowed_formats:
            raise NotAllowedValueError(value, allowed_formats)
        return value


class TemplatesConfig(BaseModel):
    enable: bool
    encryption: bool | None = None
    encryption_deterministic: bool | None = None
    excludes: list[str] | None = []


class TemplategroupsConfig(BaseModel):
    enable: bool
    encryption: bool | None = None
    encryption_deterministic: bool | None = None
    excludes: list[str] | None = []


class HostsConfig(BaseModel):
    enable: bool
    encryption: bool | None = None
    encryption_deterministic: bool | None = None
    excludes: list[str] | None = []


class HostgroupsConfig(BaseModel):
    enable: bool
    encryption: bool | None = None
    encryption_deterministic: bool | None = None
    excludes: list[str] | None = []


class MapsConfig(BaseModel):
    enable: bool
    encryption: bool | None = None
    encryption_deterministic: bool | None = None
    excludes: list[str] | None = []


class ImagesConfig(BaseModel):
    enable: bool
    encryption: bool | None = None
    encryption_deterministic: bool | None = None
    excludes: list[str] | None = []


class MediatypesConfig(BaseModel):
    enable: bool
    encryption: bool | None = None
    encryption_deterministic: bool | None = None
    excludes: list[str] | None = []


class InputsConfig(BaseModel):
    templates: TemplatesConfig
    templategroups: TemplategroupsConfig
    hosts: HostsConfig
    hostgroups: HostgroupsConfig
    maps: MapsConfig
    images: ImagesConfig
    mediatypes: MediatypesConfig

    def set_attribute(self, key: str, value: dict) -> None:
        for attr in self.__dict__:
            if key in self.__dict__[attr].__dict__ and self.__dict__[attr].__dict__[key] is None:
                self.__dict__[attr].__dict__[key] = value

class GitConfig(BaseModel):
    enable: bool
    repo: str


class S3LifecycleConfig(BaseModel):
    enable: bool
    days: int


class S3RetentionConfig(BaseModel):
    enable: bool
    days: int


class S3Config(BaseModel):
    enable: bool
    url: str
    access_key: str
    secret_key: str
    bucket: str
    bucket_path: str | None = "."
    lifecycle: S3LifecycleConfig
    retention: S3RetentionConfig


class OutputsConfig(BaseModel):
    git: GitConfig
    s3: S3Config


class Configuration(BaseModel):
    model_config = ConfigDict(extra="ignore")

    general: GeneralConfig
    zabbix: ZabbixConfig
    inputs: InputsConfig
    outputs: OutputsConfig


###################################################################


class ConfigParser:
    def __init__(self) -> None:
        self.config_file = Path(__file__).parent.parent / "config.yaml"
        self.argsparser = ArgumentParser()
        self.argsparser.add_argument(
            "-c",
            "--config",
            default=self.config_file,
            help=f"Configuration file (default: {self.config_file})",
            required=False,
        )

    def load_data(self) -> Configuration:
        self.args = self.argsparser.parse_args()
        self.config_file = self.args.config
        with Path.open(self.config_file, "r") as file:
            config_dict = yaml.safe_load(file)

        config_data = Configuration.model_validate(config_dict)
        set_log_level(config_data.general.loglevel_numeric)

        config_data.inputs.set_attribute("encryption", config_data.general.encryption)
        config_data.inputs.set_attribute("encryption_deterministic", config_data.general.encryption_deterministic)

        return config_data

    def __getattr__(self, name: str) -> BaseModel:
        config_data = self.load_data()
        if hasattr(config_data, name):
            return getattr(config_data, name)
        raise UnknownConfigAttributeError(name)

    def __repr__(self) -> str:
        return str(self.load_data().model_dump())

    def add_argument(self, *args: int, **kwargs: int) -> None:
        self.argsparser.add_argument(*args, **kwargs)


config = ConfigParser()
