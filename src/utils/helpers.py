"""
계약서 자동화 시스템 - 헬퍼 함수

파일명 정규화, 플레이스홀더 추출, 문자열 처리 등 공용 유틸리티 함수 모음
"""

import re
from pathlib import Path
from typing import Set, Dict, List, Tuple, Optional
from datetime import datetime

from .constants import (
    PLACEHOLDER_PATTERN,
    FILENAME_FORBIDDEN_CHARS,
    FILENAME_MAX_LENGTH,
    PLACEHOLDER_START,
    PLACEHOLDER_END,
)
from .logger import warning, debug

# ============================================================================
# 파일명 정규화
# ============================================================================


def normalize_filename(
    filename: str,
    max_length: int = FILENAME_MAX_LENGTH,
    replace_spaces: bool = True,
) -> str:
    """파일명을 정규화합니다.

    - 금지된 문자 제거
    - 공백 처리
    - 길이 제한
    - 확장자 보존

    Args:
        filename: 원본 파일명
        max_length: 최대 길이 (확장자 포함)
        replace_spaces: 공백을 언더스코어로 변경 여부

    Returns:
        정규화된 파일명

    Examples:
        >>> normalize_filename("김철수 계약서.hwpx")
        "김철수_계약서.hwpx"
        >>> normalize_filename("파일<이름>.txt")
        "파일이름.txt"
    """
    if not filename:
        return "unnamed"

    # 확장자 분리
    path = Path(filename)
    name = path.stem
    ext = path.suffix

    # 공백 처리
    if replace_spaces:
        name = name.replace(" ", "_")

    # 금지된 문자 제거
    name = re.sub(FILENAME_FORBIDDEN_CHARS, "", name)

    # 빈 문자열 체크
    if not name:
        name = "unnamed"

    # 길이 제한 (확장자를 고려)
    ext_length = len(ext)
    max_name_length = max_length - ext_length
    if len(name) > max_name_length:
        name = name[:max_name_length]

    return f"{name}{ext}"


def get_unique_filename(
    directory: Path,
    filename: str,
    strategy: str = "rename",
) -> str:
    """중복되지 않는 파일명을 생성합니다.

    Args:
        directory: 대상 디렉토리
        filename: 원본 파일명
        strategy: 충돌 처리 전략
                 "rename": 이름 변경 (1, 2, 3...)
                 "overwrite": 덮어쓰기 허용 (원본 반환)
                 "skip": 건너뛰기 (None 반환)

    Returns:
        고유한 파일명 (strategy="skip"일 때 중복이면 None)

    Examples:
        >>> get_unique_filename(Path("/tmp"), "test.txt", "rename")
        "test.txt"  # 또는 "test_1.txt", "test_2.txt" 등
    """
    directory = Path(directory)
    target_path = directory / filename

    # 파일이 없으면 원본 파일명 반환
    if not target_path.exists():
        return filename

    # 전략에 따라 처리
    if strategy == "overwrite":
        return filename

    if strategy == "skip":
        return None

    # strategy == "rename"
    path = Path(filename)
    name = path.stem
    ext = path.suffix

    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        new_path = directory / new_filename
        if not new_path.exists():
            debug(f"고유한 파일명 생성: {new_filename} (충돌 회피)")
            return new_filename
        counter += 1

        # 무한루프 방지
        if counter > 10000:
            warning(f"파일명 생성 실패 (무한루프): {filename}")
            return filename


# ============================================================================
# 플레이스홀더 추출 및 처리
# ============================================================================


def extract_placeholders(text: str) -> Set[str]:
    """텍스트에서 모든 플레이스홀더를 추출합니다.

    Args:
        text: 검색 대상 텍스트

    Returns:
        플레이스홀더 이름의 집합 (중복 제거됨)

    Examples:
        >>> extract_placeholders("{{이름}} 님의 주소는 {{주소}} 입니다.")
        {'이름', '주소'}
    """
    matches = re.findall(PLACEHOLDER_PATTERN, text)
    return set(matches)


def extract_placeholders_with_positions(text: str) -> List[Tuple[str, int, int]]:
    """플레이스홀더를 위치 정보와 함께 추출합니다.

    Args:
        text: 검색 대상 텍스트

    Returns:
        (플레이스홀더_이름, 시작위치, 끝위치) 튜플 리스트

    Examples:
        >>> extract_placeholders_with_positions("{{이름}}은 {{직급}}입니다.")
        [('이름', 0, 6), ('직급', 8, 14)]
    """
    result = []
    for match in re.finditer(PLACEHOLDER_PATTERN, text):
        placeholder_name = match.group(1)
        start, end = match.span()
        result.append((placeholder_name, start, end))
    return result


def replace_placeholder(
    text: str,
    placeholder_name: str,
    value: str,
) -> str:
    """특정 플레이스홀더를 값으로 대체합니다.

    Args:
        text: 원본 텍스트
        placeholder_name: 플레이스홀더 이름 (예: "이름")
        value: 대체할 값

    Returns:
        대체된 텍스트

    Examples:
        >>> replace_placeholder("안녕 {{이름}}!", "이름", "철수")
        "안녕 철수!"
    """
    pattern = f"{PLACEHOLDER_START}{placeholder_name}{PLACEHOLDER_END}"
    return text.replace(pattern, str(value))


def replace_all_placeholders(
    text: str,
    replacements: Dict[str, str],
    keep_unmatched: bool = True,
) -> str:
    """모든 플레이스홀더를 일괄 대체합니다.

    Args:
        text: 원본 텍스트
        replacements: {플레이스홀더_이름: 값} 딕셔너리
        keep_unmatched: True면 일치하지 않는 플레이스홀더 유지, False면 제거

    Returns:
        대체된 텍스트

    Examples:
        >>> replace_all_placeholders(
        ...     "{{이름}} {{주소}}",
        ...     {"이름": "김철수", "주소": "서울시"}
        ... )
        "김철수 서울시"
    """
    result = text
    found_placeholders = extract_placeholders(text)

    # 제공된 값으로 대체
    for placeholder in found_placeholders:
        if placeholder in replacements:
            value = replacements[placeholder]
            result = replace_placeholder(result, placeholder, value)
        elif not keep_unmatched:
            # 일치하지 않는 플레이스홀더 제거
            result = replace_placeholder(result, placeholder, "")

    return result


def get_missing_placeholders(
    text: str,
    provided_keys: Set[str],
) -> Set[str]:
    """제공되지 않은 플레이스홀더를 찾습니다.

    Args:
        text: 검색 대상 텍스트
        provided_keys: 제공된 키의 집합

    Returns:
        제공되지 않은 플레이스홀더 이름의 집합

    Examples:
        >>> get_missing_placeholders(
        ...     "{{이름}} {{주소}} {{전화}}",
        ...     {"이름", "주소"}
        ... )
        {"전화"}
    """
    required = extract_placeholders(text)
    missing = required - provided_keys
    return missing


# ============================================================================
# Excel 칼럼 처리
# ============================================================================


def normalize_column_name(column_name: str) -> str:
    """Excel 칼럼명을 정규화합니다.

    - 앞뒤 공백 제거
    - 대소문자 통일 (소문자로 변환 후 원본 유지하되, 비교 시 소문자 사용)

    Args:
        column_name: 원본 칼럼명

    Returns:
        정규화된 칼럼명

    Examples:
        >>> normalize_column_name("  이름  ")
        "이름"
    """
    return column_name.strip()


def match_columns_to_placeholders(
    columns: List[str],
    placeholders: Set[str],
    case_insensitive: bool = False,
) -> Tuple[Dict[str, str], Set[str]]:
    """Excel 칼럼과 플레이스홀더를 매핑합니다.

    Args:
        columns: Excel 칼럼명 리스트
        placeholders: 템플릿 플레이스홀더 집합
        case_insensitive: 대소문자 무시 여부

    Returns:
        ({플레이스홀더: 칼럼명}, {일치하지 않는_플레이스홀더})

    Examples:
        >>> match_columns_to_placeholders(
        ...     ["이름", "주소", "전화"],
        ...     {"이름", "직급"}
        ... )
        ({'이름': '이름'}, {'직급'})
    """
    mapping = {}
    unmatched = set()

    # 칼럼명을 정규화
    normalized_columns = {normalize_column_name(col): col for col in columns}

    # 각 플레이스홀더를 칼럼과 매칭
    for placeholder in placeholders:
        search_key = placeholder.lower() if case_insensitive else placeholder

        for col_normalized, col_original in normalized_columns.items():
            col_search = col_normalized.lower() if case_insensitive else col_normalized

            if search_key == col_search:
                mapping[placeholder] = col_original
                break
        else:
            # 일치하는 칼럼이 없음
            unmatched.add(placeholder)

    return mapping, unmatched


# ============================================================================
# 값 정규화
# ============================================================================


def normalize_value(
    value: any,
    default: str = "",
    strip: bool = True,
) -> str:
    """값을 정규화된 문자열로 변환합니다.

    - None/NaN 처리
    - 날짜/시간 처리 (datetime 객체에서 날짜만 추출)
    - 공백 제거 (선택)
    - 문자열 변환

    Args:
        value: 원본 값 (any)
        default: 빈 값일 때 기본값
        strip: 앞뒤 공백 제거 여부

    Returns:
        정규화된 문자열

    Examples:
        >>> normalize_value(None)
        ""
        >>> normalize_value("  김철수  ")
        "김철수"
        >>> normalize_value(123)
        "123"
        >>> normalize_value(datetime(2026, 3, 1, 0, 0))
        "2026-03-01"
    """
    # None 처리
    if value is None:
        return default

    # NaN 처리 (pandas DataFrame에서)
    try:
        import pandas as pd

        if pd.isna(value):
            return default
    except ImportError:
        pass

    # datetime 객체 처리 (날짜만 추출)
    if isinstance(value, datetime):
        result = value.strftime("%Y-%m-%d")
    else:
        # 문자열 변환
        result = str(value)

    # 공백 처리
    if strip:
        result = result.strip()

    # 빈 문자열 체크
    if not result:
        return default

    return result


# ============================================================================
# 날짜/시간 처리
# ============================================================================


def get_timestamp_string(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """현재 시간을 포맷된 문자열로 반환합니다.

    Args:
        format_str: datetime 포맷 문자열

    Returns:
        포맷된 시간 문자열

    Examples:
        >>> get_timestamp_string()
        "2025-05-16 20:30:45"
    """
    return datetime.now().strftime(format_str)


# ============================================================================
# 경로 처리
# ============================================================================


def ensure_directory_exists(path: Path) -> Path:
    """디렉토리가 없으면 생성합니다.

    Args:
        path: 디렉토리 경로

    Returns:
        생성된 디렉토리 Path 객체
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


# ============================================================================
# 검증 헬퍼
# ============================================================================


def is_valid_excel_file(file_path: Path) -> bool:
    """Excel 파일 유효성 검사.

    Args:
        file_path: 파일 경로

    Returns:
        유효한 Excel 파일이면 True
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    if not file_path.exists():
        warning(f"파일이 없습니다: {file_path}")
        return False

    if not file_path.suffix.lower() in [".xlsx", ".xls"]:
        warning(f"Excel 파일이 아닙니다: {file_path}")
        return False

    return True


def is_valid_hwpx_file(file_path: Path) -> bool:
    """HWPX 파일 유효성 검사.

    Args:
        file_path: 파일 경로

    Returns:
        유효한 HWPX 파일이면 True
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    if not file_path.exists():
        warning(f"파일이 없습니다: {file_path}")
        return False

    if file_path.suffix.lower() != ".hwpx":
        warning(f"HWPX 파일이 아닙니다: {file_path}")
        return False

    return True


if __name__ == "__main__":
    # 간단한 테스트
    print("=== 파일명 정규화 ===")
    print(normalize_filename("김철수 계약서<>.hwpx"))

    print("\n=== 플레이스홀더 추출 ===")
    text = "{{이름}} 님은 {{직급}}입니다. 주소는 {{주소}}입니다."
    print(f"원본: {text}")
    print(f"플레이스홀더: {extract_placeholders(text)}")

    print("\n=== 플레이스홀더 대체 ===")
    result = replace_all_placeholders(
        text, {"이름": "김철수", "직급": "과장", "주소": "서울시"}
    )
    print(f"결과: {result}")

    print("\n=== 칼럼 매칭 ===")
    mapping, unmatched = match_columns_to_placeholders(
        ["이름", "주소", "전화"], {"이름", "직급"}
    )
    print(f"매핑: {mapping}")
    print(f"일치하지 않음: {unmatched}")
