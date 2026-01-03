"""
Structured Logger Implementation
Provides structured JSON logging with correlation IDs
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar


# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredLogger:
    """Structured logger with JSON output and correlation IDs"""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create handler if not exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = StructuredFormatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _get_correlation_id(self) -> str:
        """Get or create correlation ID"""
        correlation_id = correlation_id_var.get()
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
            correlation_id_var.set(correlation_id)
        return correlation_id
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """Log structured message"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": logging.getLevelName(level),
            "logger": self.logger.name,
            "correlation_id": self._get_correlation_id(),
            "message": message,
            **kwargs
        }
        
        self.logger.log(level, json.dumps(log_data))
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def log_request(self, method: str, path: str, status_code: int, duration: float, **kwargs) -> None:
        """Log HTTP request"""
        self.info(
            "HTTP Request",
            event_type="http_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration * 1000,
            **kwargs
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error with exception details"""
        self.error(
            "Error occurred",
            event_type="error",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context or {},
            stack_trace=self._get_stack_trace(error)
        )
    
    def _get_stack_trace(self, error: Exception) -> Optional[str]:
        """Get stack trace for error"""
        import traceback
        return traceback.format_exc()


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        try:
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add correlation ID if available
            correlation_id = correlation_id_var.get()
            if correlation_id:
                log_data["correlation_id"] = correlation_id
            
            # Add extra fields
            for key, value in record.__dict__.items():
                if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                             "filename", "module", "lineno", "funcName", "created", "msecs", 
                             "relativeCreated", "thread", "threadName", "processName", 
                             "process", "getMessage", "exc_info", "exc_text", "stack_info"]:
                    log_data[key] = value
            
            return json.dumps(log_data)
        
        except Exception:
            # Fallback to standard formatting
            return super().format(record)


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context"""
    correlation_id_var.set(correlation_id)
