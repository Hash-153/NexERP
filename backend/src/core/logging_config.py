"""
NexERP Enterprise - Structured Logging Configuration.
Provides JSON-formatted structured logs for production (ELK / Datadog ingestion)
and human-readable output for development.
"""

import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Emit log records as newline-delimited JSON for log aggregation pipelines.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Merge any extra fields attached to the log record
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "getMessage",
                "exc_info", "exc_text", "stack_info", "lineno", "message"
            ):
                if not key.startswith("_"):
                    log_data[key] = value

        return json.dumps(log_data, default=str)


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure root logger with appropriate handler and formatter.
    Called once at application startup from main.py.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    if log_format.lower() == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S"
            )
        )

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers in production
    for noisy_logger in ["uvicorn.access", "sqlalchemy.engine.Engine", "httpx", "httpcore"]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named module-level logger instance."""
    return logging.getLogger(name)
