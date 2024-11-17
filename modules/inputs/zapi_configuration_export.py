from modules.models import ExportObjectList
from modules.config import config
from modules.logger import GetLogger
from modules.helpers import sanitize_string
from modules.models import ExportObject
from typing import List, Dict
import concurrent.futures
import zabbix_utils
import re

_AVAIL_EXPORT_TYPES: Dict = {
    "images": {
        "api_method_name": "image",
        "api_id_field": "imageid",
        "api_export_field": "images",
    },
    "hostgroups": {
        "api_method_name": "hostgroup",
        "api_id_field": "groupid",
        "api_export_field": "host_groups",
    },
    "hosts": {
        "api_method_name": "host",
        "api_id_field": "hostid",
        "api_export_field": "hosts",
    },
    "maps": {
        "api_method_name": "map",
        "api_id_field": "sysmapid",
        "api_export_field": "maps",
    },
    "mediatypes": {
        "api_method_name": "mediatype",
        "api_id_field": "mediatypeid",
        "api_export_field": "mediaTypes",
    },
    "templategroups": {
        "api_method_name": "templategroup",
        "api_id_field": "groupid",
        "api_export_field": "template_groups",
    },
    "templates": {
        "api_method_name": "template",
        "api_id_field": "templateid",
        "api_export_field": "templates",
    },
}


def ZConfigGetDataWorker(
    export_type_name: str,
    export_type_data: Dict,
    element: Dict,
    element_counter: str
) -> ExportObject:
    logger = GetLogger()
    logger.debug(f"Exporting {export_type_name} {element_counter}: {element['name']} ({element[export_type_data['api_id_field']]})")

    zapi = zabbix_utils.ZabbixAPI(url=config.zabbix.url, **config.zabbix.auth.model_dump())
    data = zapi.configuration.export(
        options = {
            export_type_data["api_export_field"]: [
                element[export_type_data["api_id_field"]]
            ]
        },
        prettyprint = True,
        format = config.zabbix.export_format,
    )

    return ExportObject(
        type = export_type_name,
        id = element[export_type_data["api_id_field"]],
        name = element["name"],
        name_sanitized = sanitize_string(element["name"]),
        data = data,
    )


def ZConfigGetData(export_type_name: str, export_type_data: dict) -> ExportObjectList:
    data: ExportObjectList = []

    zapi = zabbix_utils.ZabbixAPI(url=config.zabbix.url, **config.zabbix.auth.model_dump())

    api_method_obj = getattr(zapi, export_type_data["api_method_name"])
    api_action_obj = getattr(api_method_obj, "get")

    elements = api_action_obj(
        output=[export_type_data["api_id_field"], "name"],
        limit=2
    )

    elements_filtered: List = []
    for element in elements:
        if not any(
            re.search(pattern, element["name"])
            for pattern in config.inputs.model_dump()[export_type_name]["excludes"]
        ):
            elements_filtered.append(element)

    element_counter: int = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.general.max_threads) as pool:
        pool_jobs: List = []
        for element in elements_filtered:
            element_counter += 1
            element_counter_str: str = f"{element_counter}/{len(elements_filtered)}"

            pool_jobs.append(
                pool.submit(
                    ZConfigGetDataWorker,
                    export_type_name = export_type_name,
                    export_type_data = export_type_data,
                    element = element,
                    element_counter = element_counter_str,
                )
            )

        for job in concurrent.futures.as_completed(pool_jobs):
            data.append(job.result())

    return data


def ZConfigExport() -> ExportObjectList:
    data: ExportObjectList = []

    for export_type_name, export_type_data in _AVAIL_EXPORT_TYPES.items():
        if config.inputs.model_dump()[export_type_name]["enable"]:
            data = data + ZConfigGetData(export_type_name, export_type_data)

    return data


__all__ = ["ZConfigExport"]
