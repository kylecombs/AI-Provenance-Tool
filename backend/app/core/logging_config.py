"""Logging configuration for the AI Provenance Tool"""

import logging
import sys
from typing import Dict, Any
from pathlib import Path

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        
        if hasattr(record, 'url'):
            log_entry["url"] = record.url
        
        if hasattr(record, 'client_ip'):
            log_entry["client_ip"] = record.client_ip
        
        if hasattr(record, 'error_id'):
            log_entry["error_id"] = record.error_id
        
        if hasattr(record, 'details'):
            log_entry["details"] = record.details
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Format as key=value pairs for easy parsing
        formatted_pairs = []
        for key, value in log_entry.items():
            if value is not None:
                if isinstance(value, str) and ' ' in value:
                    formatted_pairs.append(f'{key}="{value}"')
                else:
                    formatted_pairs.append(f'{key}={value}')
        
        return ' '.join(formatted_pairs)


def setup_logging() -> None:
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = StructuredFormatter(
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler for errors only
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    root_logger.addHandler(error_handler)
    
    # Configure third-party loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Set application loggers to INFO level
    logging.getLogger("app").setLevel(logging.INFO)
    
    # Log startup message
    logger = logging.getLogger("app.startup")
    logger.info("Logging configured successfully")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(f"app.{name}")


# Correlation ID utilities
def add_correlation_id(record: logging.LogRecord, correlation_id: str) -> None:
    """Add correlation ID to log record"""
    record.correlation_id = correlation_id


def log_api_call(
    logger: logging.Logger,
    service: str,
    method: str,
    url: str,
    status_code: int,
    duration_ms: float,
    request_id: str = None
) -> None:
    """Log external API call"""
    extra_fields = {
        "service": service,
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
        "type": "api_call"
    }
    
    if request_id:
        extra_fields["request_id"] = request_id
    
    if status_code >= 400:
        logger.warning(f"API call failed: {service} {method} {url}", extra=extra_fields)
    else:
        logger.info(f"API call successful: {service} {method} {url}", extra=extra_fields)


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    duration_ms: float,
    rows_affected: int = None,
    request_id: str = None
) -> None:
    """Log database operation"""
    extra_fields = {
        "operation": operation,
        "table": table,
        "duration_ms": round(duration_ms, 2),
        "type": "database_operation"
    }
    
    if rows_affected is not None:
        extra_fields["rows_affected"] = rows_affected
    
    if request_id:
        extra_fields["request_id"] = request_id
    
    logger.info(f"Database operation: {operation} on {table}", extra=extra_fields)