"""
계약서 자동화 시스템 - 메인 패키지

전체 애플리케이션의 핵심 모듈을 제공합니다.
"""

__version__ = "1.0.0"
__author__ = "교육청"

from .core import (
    ExcelReader,
    HWPXProcessor,
    Validator,
    ValidationResult,
    BatchProcessor,
    BatchResult,
)

from .utils import (
    APP_NAME,
    APP_VERSION,
    ensure_directories,
    debug,
    info,
    warning,
    error,
    critical,
    get_log_content,
)

__all__ = [
    # Core
    "ExcelReader",
    "HWPXProcessor",
    "Validator",
    "ValidationResult",
    "BatchProcessor",
    "BatchResult",
    # Utils
    "APP_NAME",
    "APP_VERSION",
    "ensure_directories",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "get_log_content",
]
