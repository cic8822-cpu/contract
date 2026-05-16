"""
계약서 자동화 시스템 - 상수 정의

프로그램 전체에서 사용되는 설정값, 경로, 정규식 등을 정의합니다.
"""

import os
from pathlib import Path

# ============================================================================
# 프로그램 메타정보
# ============================================================================

APP_NAME = "신규채용자 계약서 작성 자동화"
APP_VERSION = "1.0.0"
APP_AUTHOR = "교육청"

# ============================================================================
# 파일 경로 및 디렉토리
# ============================================================================

# 기본 디렉토리 (실행 시 __main__ 또는 EXE 기준으로 설정)
BASE_DIR = Path(__file__).parent.parent.parent  # 프로젝트 루트

# 리소스 디렉토리
RESOURCES_DIR = BASE_DIR / "resources"
SAMPLE_TEMPLATE_DIR = RESOURCES_DIR / "templates"
SAMPLE_DATA_DIR = RESOURCES_DIR / "sample_data"

# 출력 디렉토리
OUTPUT_DIR = BASE_DIR / "outputs"
CONTRACTS_OUTPUT_DIR = OUTPUT_DIR / "contracts"
LOGS_OUTPUT_DIR = OUTPUT_DIR / "logs"

# 사용자 설정 디렉토리
USER_CONFIG_DIR = Path.home() / ".contract_generator"
USER_SETTINGS_FILE = USER_CONFIG_DIR / "settings.json"

# 임시 디렉토리
TEMP_DIR = Path.home() / ".contract_generator" / "temp"

# ============================================================================
# 파일 확장자
# ============================================================================

EXCEL_EXTENSIONS = (".xlsx", ".xls")
HWPX_EXTENSION = ".hwpx"
HWPX_MIME_TYPE = "application/vnd.hancom.hwpx"

# ============================================================================
# Excel 읽기 설정
# ============================================================================

# 헤더 행 번호 (0-indexed)
EXCEL_HEADER_ROW = 0

# 데이터 읽기 시작 행
EXCEL_DATA_START_ROW = 1

# 대용량 파일 처리 청크 크기
EXCEL_CHUNK_SIZE = 1000

# ============================================================================
# 플레이스홀더 설정
# ============================================================================

# 플레이스홀더 정규식 패턴
# {{이름}}, {{주소}}, {{생일}} 형식
PLACEHOLDER_PATTERN = r"\{\{([A-Za-z0-9_가-힣\-]+)\}\}"

# 플레이스홀더 시작/종료 문자
PLACEHOLDER_START = "{{"
PLACEHOLDER_END = "}}"

# ============================================================================
# HWPX 처리 설정
# ============================================================================

# HWPX 내부 주요 파일
HWPX_CONTENT_XML = "content.xml"
HWPX_STYLES_XML = "styles.xml"
HWPX_SETTINGS_XML = "settings.xml"
HWPX_MIMETYPE_FILE = "mimetype"

# HWPX ZIP 내부 메타정보
HWPX_META_INF = "META-INF"
HWPX_MANIFEST = "META-INF/manifest.xml"

# XML 인코딩
XML_ENCODING = "utf-8"

# ============================================================================
# 에러 처리 설정
# ============================================================================

# 에러 처리 전략: "all_or_nothing" 또는 "skip_on_error"
ERROR_HANDLING_STRATEGY = "all_or_nothing"

# 최대 재시도 횟수
MAX_RETRIES = 3

# ============================================================================
# 로그 설정
# ============================================================================

# 로그 레벨
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 로그 포맷
LOG_FORMAT = (
    "[{time:YYYY-MM-DD HH:mm:ss}] {level: <8} | {name}:{function}:{line} - {message}"
)

# 메모리 로그 버퍼 최대 크기 (라인 수)
LOG_BUFFER_MAX_LINES = 10000

# 로그 파일 자동 회전
LOG_ROTATION_SIZE = "100 MB"
LOG_RETENTION_DAYS = 7

# ============================================================================
# GUI 설정
# ============================================================================

# 메인 윈도우
GUI_WINDOW_TITLE = APP_NAME
GUI_WINDOW_WIDTH = 600
GUI_WINDOW_HEIGHT = 500
GUI_WINDOW_MIN_WIDTH = 500
GUI_WINDOW_MIN_HEIGHT = 400

# 색상
GUI_COLOR_PRIMARY = "#4CAF50"  # 초록색 (버튼)
GUI_COLOR_SUCCESS = "#8BC34A"  # 밝은 초록
GUI_COLOR_ERROR = "#F44336"  # 빨간색
GUI_COLOR_WARNING = "#FF9800"  # 주황색
GUI_COLOR_INFO = "#2196F3"  # 파란색

# 폰트
GUI_FONT_NORMAL = ("Arial", 10)
GUI_FONT_BUTTON = ("Arial", 12, "bold")
GUI_FONT_TITLE = ("Arial", 14, "bold")
GUI_FONT_MONO = ("Courier New", 9)

# 진행률 대화창
PROGRESS_DIALOG_WIDTH = 400
PROGRESS_DIALOG_HEIGHT = 150

# ============================================================================
# 배치 처리 설정
# ============================================================================

# 배치 처리 시 한 번에 처리할 파일 수
BATCH_SIZE = 10

# 진행률 업데이트 간격 (밀리초)
PROGRESS_UPDATE_INTERVAL = 100

# ============================================================================
# 파일명 생성 설정
# ============================================================================

# 파일명 충돌 시 처리 방식
# "overwrite": 덮어쓰기
# "rename": 이름 변경 (1, 2, 3...)
# "skip": 건너뛰기
FILENAME_CONFLICT_STRATEGY = "rename"

# 파일명에서 금지된 문자
FILENAME_FORBIDDEN_CHARS = r'[<>:"/\\|?*]'

# 파일명 최대 길이 (Windows: 255, 확장자 포함)
FILENAME_MAX_LENGTH = 250

# ============================================================================
# 유효성 검사
# ============================================================================

# Dry-run 검증 활성화 여부
ENABLE_DRY_RUN = True

# 필수 칼럼 확인 여부
VALIDATE_REQUIRED_COLUMNS = True

# ============================================================================
# 설정 파일 (JSON)
# ============================================================================

# 기본 설정값
DEFAULT_SETTINGS = {
    "last_excel_path": "",
    "last_template_path": "",
    "last_output_dir": "",
    "filename_column": "이름",  # 파일명 생성 기준 칼럼
    "use_row_number_as_filename": False,
    "auto_open_output_on_complete": True,
    "log_to_file": False,
}

# ============================================================================
# 메시지 (사용자 표시용)
# ============================================================================

MESSAGES = {
    "error_invalid_excel": "유효한 Excel 파일을 선택해주세요.",
    "error_invalid_template": "유효한 HWPX 템플릿 파일을 선택해주세요.",
    "error_no_placeholders": "템플릿에서 플레이스홀더를 찾을 수 없습니다.",
    "error_column_mismatch": "Excel 칼럼과 템플릿 플레이스홀더가 일치하지 않습니다.",
    "error_all_or_nothing": "배치 처리 중 오류가 발생했습니다. 생성된 파일이 없습니다.",
    "success_contracts_created": "{count}개의 계약서가 생성되었습니다.",
    "warning_dry_run_failed": "검증 실패: 실제 생성을 진행하지 않습니다.",
}

# ============================================================================
# 초기화 함수
# ============================================================================


def ensure_directories():
    """필요한 모든 디렉토리 생성"""
    directories = [
        CONTRACTS_OUTPUT_DIR,
        LOGS_OUTPUT_DIR,
        USER_CONFIG_DIR,
        TEMP_DIR,
        SAMPLE_TEMPLATE_DIR,
        SAMPLE_DATA_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_app_info():
    """애플리케이션 정보 반환"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "author": APP_AUTHOR,
    }
