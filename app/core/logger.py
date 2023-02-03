import datetime
import json
import logging
import traceback
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


def get_log_config(debug: bool) -> Dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "app.core.logger.JSONLogFormatter",
            },
        },
        "handlers": {
            "json": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "json",
            },
        },
        "loggers": {
            "app": {
                "handlers": ["json"],
                "level": "DEBUG" if debug else "INFO",
                "propagate": False,
            },
            "sqlalchemy": {
                "handlers": ["json"],
                "level": "INFO" if debug else "ERROR",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["json"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["json"],
                "level": "ERROR",
                "propagate": False,
            },
        },
    }


class BaseJSONLogSchema(BaseModel):
    level_name: str
    message: str
    source: str
    timestamp: str
    exceptions: Union[List[str], str, None] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_id: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class JSONLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord, *args: Any, **kwargs: Any) -> str:
        log_object: Dict = self._format_log_object(record)
        return json.dumps(log_object, ensure_ascii=False)

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> Dict:
        now = (
            datetime.datetime.fromtimestamp(record.created)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        json_log_fields = BaseJSONLogSchema(
            timestamp=now,
            level_name=logging.getLevelName(record.levelno),
            message=record.getMessage(),
            source=record.name,
        )

        if hasattr(record, "props"):
            json_log_fields.props = record.props  # type: ignore

        if record.exc_info:
            json_log_fields.exceptions = traceback.format_exception(*record.exc_info)

        elif record.exc_text:
            json_log_fields.exceptions = record.exc_text

        json_log_object = json_log_fields.dict(
            exclude_unset=True,
        )
        if hasattr(record, "request_json_fields"):
            json_log_object.update(record.request_json_fields)  # type: ignore

        return json_log_object
