from pydantic import BaseModel, field_validator

from modules.exceptions import NotAllowedValueError


class ExportObject(BaseModel):
    type: str
    id: int
    name: str
    name_sanitized: str
    data: str

    @field_validator("type")
    def check_type(cls, value: str) -> str:
        allowed_formats = [
            "templates",
            "templategroups",
            "hosts",
            "hostgroups",
            "maps",
            "images",
            "mediatypes",
        ]
        if value not in allowed_formats:
            raise NotAllowedValueError(value, allowed_formats)
        return value


class ExportObjectList(BaseModel):
    data: list[ExportObject]
