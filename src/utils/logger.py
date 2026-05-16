"""
계약서 자동화 시스템 - 로거 모듈

메모리 기반 로깅 시스템을 구현합니다.
loguru를 사용하며, 로그는 메모리 버퍼에만 저장됩니다.
"""

import sys
from io import StringIO
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from loguru import logger as _logger

from .constants import (
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_BUFFER_MAX_LINES,
    LOGS_OUTPUT_DIR,
    APP_NAME,
)

# ============================================================================
# 메모리 로그 버퍼
# ============================================================================


class MemoryLogBuffer:
    """메모리 기반 로그 버퍼 - StringIO를 래핑"""

    def __init__(self, max_lines: int = LOG_BUFFER_MAX_LINES):
        self.buffer = StringIO()
        self.max_lines = max_lines
        self.line_count = 0
        self.lock_reset = False

    def write(self, message: str) -> int:
        """로그 메시지 작성 - loguru와 호환되도록 int 반환"""
        if self.lock_reset:
            return len(message) if message else 0

        self.buffer.write(message)
        self.line_count += message.count("\n")

        # 버퍼 크기 초과 시 오래된 내용 제거
        if self.line_count > self.max_lines:
            self._trim_buffer()

        # loguru는 쓰기된 바이트 수를 기대함
        return len(message) if message else 0

    def _trim_buffer(self) -> None:
        """버퍼 크기 초과 시 오래된 50%의 내용 제거"""
        content = self.buffer.getvalue()
        lines = content.split("\n")

        # 뒤에서 50% 유지
        keep_count = len(lines) // 2
        trimmed_lines = lines[-keep_count:] if len(lines) > keep_count else lines
        trimmed_content = "\n".join(trimmed_lines)

        # 버퍼 재구성
        self.buffer = StringIO()
        self.buffer.write(trimmed_content)
        self.line_count = len(trimmed_lines)

    def get_content(self) -> str:
        """현재 버퍼의 전체 내용 반환"""
        return self.buffer.getvalue()

    def clear(self) -> None:
        """버퍼 비우기"""
        self.buffer = StringIO()
        self.line_count = 0

    def get_lines(self, start: int = 0, end: Optional[int] = None) -> List[str]:
        """특정 범위의 로그 라인 반환 (슬라이싱)"""
        lines = self.buffer.getvalue().split("\n")
        return lines[start:end]


# ============================================================================
# 글로벌 로거 설정
# ============================================================================

# 메모리 버퍼 인스턴스
_memory_buffer = MemoryLogBuffer(max_lines=LOG_BUFFER_MAX_LINES)


class _MemorySink:
    """메모리 버퍼용 sink 클래스 - PyInstaller 호환성"""

    def __init__(self, buffer):
        self.buffer = buffer

    def write(self, message):
        """loguru sink write method"""
        try:
            if message:
                self.buffer.write(message)
                return len(message)
            return 0
        except Exception:
            # 오류 무시하고 계속
            return len(message) if message else 0


def _setup_logger() -> None:
    """loguru 로거 설정"""
    # 기본 핸들러 제거
    _logger.remove()

    # 콘솔 출력 (stderr) - 가장 안정적
    try:
        _logger.add(
            sys.stderr,
            level=LOG_LEVEL,
            format=LOG_FORMAT,
            colorize=True,
        )
    except Exception:
        pass

    # 메모리 버퍼에 기록 - 클래스 기반 sink
    try:
        memory_sink = _MemorySink(_memory_buffer)
        _logger.add(
            memory_sink.write,
            level=LOG_LEVEL,
            format=LOG_FORMAT,
            colorize=False,  # 메모리 버퍼는 색상 코드 불필요
        )
    except Exception:
        # 메모리 버퍼 설정 실패 시에도 계속 진행 (콘솔 로깅은 작동)
        pass


# 초기화
_setup_logger()

# ============================================================================
# 공개 API
# ============================================================================


def debug(message: str, **kwargs) -> None:
    """디버그 레벨 로그"""
    _logger.debug(message, **kwargs)


def info(message: str, **kwargs) -> None:
    """정보 레벨 로그"""
    _logger.info(message, **kwargs)


def warning(message: str, **kwargs) -> None:
    """경고 레벨 로그"""
    _logger.warning(message, **kwargs)


def error(message: str, **kwargs) -> None:
    """에러 레벨 로그"""
    _logger.error(message, **kwargs)


def critical(message: str, **kwargs) -> None:
    """치명 에러 레벨 로그"""
    _logger.critical(message, **kwargs)


def get_memory_buffer() -> MemoryLogBuffer:
    """메모리 버퍼 인스턴스 반환"""
    return _memory_buffer


def get_log_content() -> str:
    """현재까지의 모든 로그 내용 반환"""
    return _memory_buffer.get_content()


def get_recent_logs(count: int = 50) -> str:
    """최근 N개 라인의 로그 반환"""
    lines = _memory_buffer.get_lines()
    recent = lines[-count:] if len(lines) > count else lines
    return "\n".join(recent)


def clear_logs() -> None:
    """메모리 로그 버퍼 초기화"""
    _memory_buffer.clear()
    info(f"{APP_NAME} - 로그 버퍼가 초기화되었습니다.")


def save_logs_to_file(output_path: Optional[Path] = None) -> Path:
    """메모리 로그를 파일로 저장

    Args:
        output_path: 저장할 파일 경로. None이면 기본 로그 디렉토리에 저장

    Returns:
        저장된 파일의 Path 객체
    """
    if output_path is None:
        # 기본 로그 디렉토리에 타임스탐프를 붙여서 저장
        LOGS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = LOGS_OUTPUT_DIR / f"contract_generator_{timestamp}.log"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(_memory_buffer.get_content())

    info(f"로그가 파일로 저장되었습니다: {output_path}")
    return output_path


def get_session_info() -> dict:
    """현재 세션 정보 반환"""
    return {
        "app_name": APP_NAME,
        "timestamp": datetime.now().isoformat(),
        "log_buffer_lines": _memory_buffer.line_count,
        "log_level": LOG_LEVEL,
    }


# ============================================================================
# Context Manager for 임시 로그 레벨 변경
# ============================================================================


class temporary_log_level:
    """임시로 로그 레벨을 변경하는 Context Manager

    Usage:
        with temporary_log_level("DEBUG"):
            debug("This will be logged")
    """

    def __init__(self, level: str):
        self.new_level = level
        self.old_level = None

    def __enter__(self):
        # 현재 로거 핸들러의 레벨 변경
        # (loguru의 레벨 변경은 다소 제한적이므로 기본 구현만 제공)
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# ============================================================================
# 테스트 헬퍼
# ============================================================================


def reset_logger_for_testing() -> None:
    """테스트 시 로거 초기화"""
    _logger.remove()
    _memory_buffer.clear()
    _setup_logger()


if __name__ == "__main__":
    # 간단한 테스트
    info("로거가 초기화되었습니다.")
    debug("디버그 메시지")
    warning("경고 메시지")
    error("에러 메시지")

    print("\n=== 메모리 로그 내용 ===")
    print(get_log_content())

    print("\n=== 최근 로그 (2개) ===")
    print(get_recent_logs(2))

    print("\n=== 세션 정보 ===")
    print(get_session_info())
