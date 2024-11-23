from pydantic import BaseModel, ConfigDict, model_validator, field_validator
from typing import List, Optional
from argparse import ArgumentParser
import logging
import yaml
import pathlib

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
    loglevel: Optional[str] = "INFO"
    loglevel_numeric: Optional[int] = logging.INFO
    dryrun: Optional[bool] = False
    max_threads: Optional[int] = 10
    encryption: Optional[bool] = False
    encryption_key: Optional[str]

    @model_validator(mode="before")
    def convert_loglevel(cls, values):
        loglevel = values.get("loglevel")

        if loglevel:
            if loglevel.upper() not in loglevel_map:
                raise ValueError(f"Invalid loglevel: {loglevel}")

            values["loglevel_numeric"] = loglevel_map[loglevel.upper()]
        return values


class ZabbixAuthConfig(BaseModel):
    user: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None

    @model_validator(mode="before")
    def check_auth_fields(cls, values):
        user = values.get("user")
        password = values.get("password")
        token = values.get("token")

        if token:
            if user or password:
                raise ValueError("If 'token' is defined, 'user' and 'password' must not be set.")
        else:
            if not (user and password):
                raise ValueError("If 'token' is not defined, both 'user' and 'password' must be set.")

        return values


class ZabbixConfig(BaseModel):
    url: str
    auth: ZabbixAuthConfig
    export_format: Optional[str] = "yaml"

    @field_validator("export_format")
    def check_export_format(cls, value):
        allowed_formats = {"yaml", "json", "xml"}
        if value not in allowed_formats:
            raise ValueError(f"Allowed values are: {', '.join(allowed_formats)}.")
        return value


class TemplatesConfig(BaseModel):
    enable: bool
    encryption: Optional[bool] = False
    excludes: Optional[List[str]] = []


class TemplategroupsConfig(BaseModel):
    enable: bool
    encryption: Optional[bool] = False
    excludes: Optional[List[str]] = []


class HostsConfig(BaseModel):
    enable: bool
    encryption: Optional[bool] = False
    excludes: Optional[List[str]] = []


class HostgroupsConfig(BaseModel):
    enable: bool
    encryption: Optional[bool] = False
    excludes: Optional[List[str]] = []


class MapsConfig(BaseModel):
    enable: bool
    encryption: Optional[bool] = False
    excludes: Optional[List[str]] = []


class ImagesConfig(BaseModel):
    enable: bool
    encryption: Optional[bool] = False
    excludes: Optional[List[str]] = []


class MediatypesConfig(BaseModel):
    enable: bool
    encryption: Optional[bool] = False
    excludes: Optional[List[str]] = []


class InputsConfig(BaseModel):
    templates: TemplatesConfig
    templategroups: TemplategroupsConfig
    hosts: HostsConfig
    hostgroups: HostgroupsConfig
    maps: MapsConfig
    images: ImagesConfig
    mediatypes: MediatypesConfig


class GitConfig(BaseModel):
    enable: bool
    repo: str


class OutputsConfig(BaseModel):
    git: GitConfig


class Configuration(BaseModel):
    model_config = ConfigDict(extra="ignore")

    general: GeneralConfig
    zabbix: ZabbixConfig
    inputs: InputsConfig
    outputs: OutputsConfig


###################################################################

class ConfigParser():
    def __init__(self):
        self.config_file = pathlib.Path(__file__).parent.parent / "config.yaml"
        self.argsparser = ArgumentParser()
        self.argsparser.add_argument("-c", "--config", default=self.config_file, help=f"Configuration file (default: {self.config_file})", required=False)

    def load_data(self):
        self.args = self.argsparser.parse_args()
        self.config_file = self.args.config
        with open(self.config_file, "r") as file:
            config_dict = yaml.safe_load(file)
        config_data = Configuration.model_validate(config_dict)

        return config_data

    def __getattr__(self, name: str):
        config_data = self.load_data()
        if hasattr(config_data, name):
            return getattr(config_data, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __repr__(self):
        return str(self.load_data().model_dump())

    def add_argument(self, *args, **kwargs):
        self.argsparser.add_argument(*args, **kwargs)

config = ConfigParser()
