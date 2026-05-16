"""
계약서 자동화 시스템 - 유틸리티 패키지

상수, 로거, 헬퍼 함수 등을 제공합니다.
"""

from .constants import (
    APP_NAME,
    APP_VERSION,
    BASE_DIR,
    CONTRACTS_OUTPUT_DIR,
    PLACEHOLDER_PATTERN,
    ERROR_HANDLING_STRATEGY,
    ensure_directories,
)

from .logger import (
    debug,
    info,
    warning,
    error,
    critical,
    get_log_content,
    get_recent_logs,
    clear_logs,
    save_logs_to_file,
    get_memory_buffer,
)

__all__ = [
    # Constants
    "APP_NAME",
    "APP_VERSION",
    "BASE_DIR",
    "CONTRACTS_OUTPUT_DIR",
    "PLACEHOLDER_PATTERN",
    "ERROR_HANDLING_STRATEGY",
    "ensure_directories",
    # Logger
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "get_log_content",
    "get_recent_logs",
    "clear_logs",
    "save_logs_to_file",
    "get_memory_buffer",
]
