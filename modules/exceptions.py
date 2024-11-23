class NotAllowedValueError(Exception):
    def __init__(self, value: any, allowed_values: list[any]) -> None:
        self.value = value
        self.allowed_values = allowed_values

    def __str__(self) -> str:
        return f"Value '{self.value}' is not allowed. Allowed values are: {', '.join(self.allowed_values)}."


class UnknownLogLevelError(Exception):
    def __init__(self, value: any, allowed_values: list) -> None:
        self.value = value
        self.allowed_values = allowed_values

    def __str__(self) -> str:
        return f"Log level '{self.value}' is unknown. Allowed values are: {', '.join(self.allowed_values)}."


class UnknownConfigAttributeError(Exception):
    def __init__(self, attribute: str) -> None:
        self.attribute = attribute

    def __str__(self) -> str:
        return f"Configuration has no attribute '{self.attribute}'"


class ZabbixAuthConfigError(Exception):
    def __str__(self) -> str:
        return "You have to set token or username/password for Zabbix API"
