#!/bin/env python3
import sys

import zabbix_utils
from pydantic import ValidationError

import modules.inputs.zapi_configuration_export
import modules.outputs.git
import modules.outputs.s3
from modules.config import config
from modules.logger import get_logger
from modules.models import ExportObjectList


def main() -> None:
    try:
        config.load_data()
    except FileNotFoundError:
        print(f"Configuration file not found: {config.config_file}")
        sys.exit(1)
    except ValidationError as e:
        print(f"{e.error_count()} found in configuration file:")

        for error in e.errors():
            print(".".join(error["loc"]))
            print(f"    {error['msg']}")
        sys.exit(1)
    except Exception as e:
        print(f"Error on processing configuration file: {e}")
        sys.exit(1)

    logger = get_logger()
    try:
        zapi = zabbix_utils.ZabbixAPI(url=config.zabbix.url, **config.zabbix.auth.model_dump())
        logger.debug(f"Connected to Zabbix instance with version {zapi.api_version()}")
    except zabbix_utils.exceptions.APIRequestError as e:
        logger.error(f"ZBX API: {e}")
        sys.exit(1)
    except zabbix_utils.exceptions.ProcessingError as e:
        logger.error(f"ZBX API: {e}")
        sys.exit(1)

    if zapi.version < 5.4:
        config.zabbix.export_format = "xml"
        logger.warning(f"Zabbix version < 5.4 detected. Forcing zabbix.export_format to {config.zabbix.export_format}")

    try:
        export_data: ExportObjectList = modules.inputs.zapi_configuration_export.zconfig_export()
    except zabbix_utils.exceptions.APIRequestError as e:
        logger.error(f"ZBX API: {e}")
        sys.exit(1)
    except zabbix_utils.exceptions.ProcessingError as e:
        logger.error(f"ZBX API: {e}")
        sys.exit(1)

    try:
        modules.outputs.git.export_git(export_data)
    except AttributeError:
        raise
    except Exception as e:
        logger.error(f"Output - Git: {e}")
        sys.exit(1)

    modules.outputs.s3.export_s3(export_data)


if __name__ == "__main__":
    main()
