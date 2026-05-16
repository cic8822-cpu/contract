# Contract Generator (한글 계약서 자동작성) 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**목표:** 비개발자가 Excel 데이터와 HWPX 템플릿을 입력하면 자동으로 다중 계약서 HWPX 파일을 생성하는 Windows GUI 앱 완성

**아키텍처:** 모듈식 설계 (core: 비즈니스 로직, ui: 사용자 인터페이스, utils: 공통 유틸)로 각 모듈은 독립적으로 테스트 가능. All-or-nothing 에러 처리, XML 파서 기반 안전한 HWPX 처리.

**기술 스택:** Python 3.11+, PySide6, openpyxl, ElementTree, loguru, PyInstaller

---

## 📁 파일 구조 정의

### 생성할 파일들

```
contract_generator/
├── core/
│   ├── __init__.py
│   ├── excel_reader.py              # Excel 읽기, 칼럼 추출
│   ├── hwpx_processor.py            # HWPX ZIP 처리, XML 파싱
│   └── validator.py                 # Dry-run 검증
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # PySide6 메인 창
│   ├── progress_dialog.py           # 진행률 표시
│   └── styles.qss                   # Qt 스타일시트
├── utils/
│   ├── __init__.py
│   ├── logger.py                    # 로깅 설정
│   ├── constants.py                 # 상수, 에러 메시지
│   └── helpers.py                   # 공통 함수
├── resources/
│   ├── icon.ico                     # 아이콘
│   ├── sample_template.hwpx         # 샘플 템플릿
│   └── sample_data.xlsx             # 샘플 데이터
├── build/
│   └── build.py                     # PyInstaller 빌드
├── tests/
│   ├── __init__.py
│   ├── test_excel_reader.py
│   ├── test_hwpx_processor.py
│   └── test_validator.py
├── main.py                          # GUI 진입점
├── requirements.txt
└── README.md
```

---

## 📝 작업 분해 (19개 Task)

### Phase 1: 기초 설정 (Task 1-3)

### Task 1: Python 환경 설정 및 requirements.txt 작성

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: requirements.txt 작성**

```
openpyxl==3.10.10
PySide6==6.7.0
loguru==0.7.2
```

- [ ] **Step 2: 패키지 설치 테스트**

```bash
pip install -r requirements.txt
```

Expected: 모든 패키지 설치 성공

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: add Python dependencies"
```

---

### Task 2: 상수 및 에러 메시지 정의 (utils/constants.py)

**Files:**
- Create: `utils/constants.py`

- [ ] **Step 1: constants.py 작성**

```python
"""
프로젝트 전역 상수 및 에러 메시지
"""

# 에러 메시지 (사용자용)
ERROR_EXCEL_INVALID = "Excel 파일을 읽을 수 없습니다. 파일이 손상되었거나 이미 열려 있을 수 있습니다."
ERROR_EXCEL_EMPTY = "Excel 파일이 비어있습니다. 최소 1개 행이 필요합니다."
ERROR_HWPX_INVALID = "HWPX 템플릿 파일이 유효하지 않습니다. 올바른 계약서 파일을 선택해 주세요."
ERROR_OUTPUT_PERMISSION = "출력 폴더에 쓰기 권한이 없습니다. 다른 폴더를 선택해 주세요."
ERROR_DISK_FULL = "디스크 용량이 부족합니다."
ERROR_BATCH_STOPPED = "배치 처리 중 오류가 발생하여 중단되었습니다."

# 성공 메시지
SUCCESS_BATCH_COMPLETE = "{count}개 파일이 생성되었습니다."

# 플레이스홀더 정규식
PLACEHOLDER_PATTERN = r'\{\{([A-Za-z0-9_가-힣]+)\}\}'

# 임시 폴더 프리픽스
TEMP_DIR_PREFIX = "contract_gen_"

# 설정 파일
CONFIG_DIR_NAME = ".contract_generator"
CONFIG_FILE_NAME = "settings.json"

# 최대 청크 크기 (행)
EXCEL_CHUNK_SIZE = 500
```

- [ ] **Step 2: import 테스트**

```python
from utils.constants import ERROR_EXCEL_INVALID, PLACEHOLDER_PATTERN
print(ERROR_EXCEL_INVALID)
print(PLACEHOLDER_PATTERN)
```

Expected: 메시지와 패턴이 정상 출력됨

- [ ] **Step 3: Commit**

```bash
git add utils/__init__.py utils/constants.py
git commit -m "feat: add project constants and error messages"
```

---

### Task 3: 로거 설정 (utils/logger.py)

**Files:**
- Create: `utils/logger.py`

- [ ] **Step 1: logger.py 작성 (메모리 기반)**

```python
"""
Loguru 기반 로깅 설정 (메모리 기반)
"""
import io
from loguru import logger as loguru_logger

# 메모리 버퍼
log_buffer = io.StringIO()

# 로거 설정
loguru_logger.remove()  # 기본 핸들러 제거
loguru_logger.add(
    log_buffer,
    format="[{time:HH:mm:ss}] {level: <8} | {message}",
    level="DEBUG"
)
loguru_logger.add(
    lambda msg: print(msg, end=""),  # 콘솔에도 출력
    format="[{time:HH:mm:ss}] {level: <8} | {message}",
    level="INFO"
)

# 외부 인터페이스
logger = loguru_logger

def get_logs() -> str:
    """메모리 버퍼의 모든 로그 반환"""
    return log_buffer.getvalue()

def clear_logs():
    """메모리 버퍼 초기화"""
    global log_buffer
    log_buffer = io.StringIO()
```

- [ ] **Step 2: 로거 테스트**

```python
from utils.logger import logger, get_logs, clear_logs

logger.info("테스트 메시지")
logs = get_logs()
assert "테스트 메시지" in logs
print(f"Logs:\n{logs}")
```

Expected: 로그가 정상적으로 버퍼에 저장됨

- [ ] **Step 3: Commit**

```bash
git add utils/logger.py
git commit -m "feat: add loguru-based logger with memory buffer"
```

---

### Phase 2: Core 모듈 (Task 4-8)

### Task 4: 헬퍼 함수 작성 (utils/helpers.py)

**Files:**
- Create: `utils/helpers.py`

- [ ] **Step 1: helpers.py 작성**

```python
"""
공통 헬퍼 함수 (경로, 인코딩, 파일명 정규화)
"""
import re
from pathlib import Path
from utils.constants import PLACEHOLDER_PATTERN

def normalize_filename(name: str, max_length: int = 200) -> str:
    """
    파일명 정규화 (Windows 예약어 제외, 특수문자 제거)
    
    Args:
        name: 원본 파일명
        max_length: 최대 길이
    
    Returns:
        정규화된 파일명
    """
    if not name or not str(name).strip():
        return None
    
    # 특수문자 제거 (한글, 영문, 숫자, 기본 기호만 허용)
    name = re.sub(r'[<>:"/\\|?*]', '', str(name))
    
    # 공백 정리
    name = name.strip()
    
    # 길이 제한
    if len(name) > max_length:
        name = name[:max_length]
    
    # Windows 예약어 확인
    reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1'}
    if name.upper() in reserved:
        name = f"_{name}"
    
    return name

def extract_placeholders(text: str) -> set:
    """
    텍스트에서 {{PLACEHOLDER}} 형식의 플레이스홀더 추출
    
    Args:
        text: 검색 대상 텍스트
    
    Returns:
        플레이스홀더 이름 집합
    """
    if not text:
        return set()
    matches = re.findall(PLACEHOLDER_PATTERN, text)
    return set(matches)

def get_config_dir() -> Path:
    """사용자 홈 디렉토리의 설정 폴더 경로 반환"""
    from utils.constants import CONFIG_DIR_NAME
    config_dir = Path.home() / CONFIG_DIR_NAME
    config_dir.mkdir(exist_ok=True)
    return config_dir

def get_config_file() -> Path:
    """설정 파일 경로 반환"""
    from utils.constants import CONFIG_FILE_NAME
    return get_config_dir() / CONFIG_FILE_NAME
```

- [ ] **Step 2: 테스트 코드 작성**

```python
from utils.helpers import normalize_filename, extract_placeholders, get_config_dir

# 파일명 정규화 테스트
assert normalize_filename("김철수") == "김철수"
assert normalize_filename("김철수<>") == "김철수"
assert normalize_filename("CON") == "_CON"

# 플레이스홀더 추출 테스트
placeholders = extract_placeholders("{{이름}}과 {{주소}}")
assert placeholders == {"이름", "주소"}

# 설정 디렉토리 테스트
config_dir = get_config_dir()
assert config_dir.exists()

print("모든 헬퍼 함수 테스트 통과")
```

Expected: 모든 테스트 통과

- [ ] **Step 3: Commit**

```bash
git add utils/helpers.py
git commit -m "feat: add helper functions (filename normalization, placeholder extraction)"
```

---

### Task 5: Excel Reader 구현 (core/excel_reader.py) - Part 1

**Files:**
- Create: `core/excel_reader.py`
- Create: `tests/test_excel_reader.py`

- [ ] **Step 1: 실패하는 테스트 작성 (정상 파일 읽기)**

```python
# tests/test_excel_reader.py
import pytest
from pathlib import Path
from core.excel_reader import ExcelReader

def test_read_valid_excel():
    """정상 Excel 파일 읽기"""
    reader = ExcelReader()
    # sample_data.xlsx가 테스트 데이터로 존재한다고 가정
    data = reader.read("sample_data.xlsx")
    
    assert data is not None
    assert len(data) > 0
    assert "이름" in data  # 칼럼명 확인
```

- [ ] **Step 2: 테스트 실행 (실패 확인)**

```bash
pytest tests/test_excel_reader.py::test_read_valid_excel -v
```

Expected: FAIL (ExcelReader 클래스 없음)

- [ ] **Step 3: ExcelReader 클래스 구현**

```python
# core/excel_reader.py
"""
Excel 파일 읽기 및 검증
"""
from pathlib import Path
from typing import Dict, List, Any
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException
from utils.logger import logger
from utils.constants import ERROR_EXCEL_INVALID, ERROR_EXCEL_EMPTY, EXCEL_CHUNK_SIZE


class ExcelReader:
    """Excel 파일 읽기 및 칼럼 추출"""
    
    def __init__(self):
        self.columns = []
        self.data = {}
    
    def read(self, excel_path: str) -> Dict[str, List[Any]]:
        """
        Excel 파일 읽기 (청크 처리)
        
        Args:
            excel_path: Excel 파일 경로
        
        Returns:
            {칼럼명: [값들]} 형태의 딕셔너리
        
        Raises:
            Exception: 파일 읽기 실패시
        """
        try:
            path = Path(excel_path)
            if not path.exists():
                raise FileNotFoundError(f"파일 없음: {excel_path}")
            
            workbook = load_workbook(path, data_only=True)
            worksheet = workbook.active
            
            # 첫 행에서 칼럼명 추출
            rows = list(worksheet.iter_rows(values_only=True))
            if not rows:
                raise ValueError(ERROR_EXCEL_EMPTY)
            
            self.columns = [str(col) if col else f"Column_{i}" 
                           for i, col in enumerate(rows[0])]
            
            # 데이터 행 읽기 (2번째 행부터)
            self.data = {col: [] for col in self.columns}
            for row_idx, row_values in enumerate(rows[1:], start=2):
                for col_idx, col_name in enumerate(self.columns):
                    value = row_values[col_idx] if col_idx < len(row_values) else ""
                    self.data[col_name].append(value)
            
            logger.info(f"Excel 로드 완료: {len(self.columns)}개 칼럼, {len(self.data[self.columns[0]])}개 행")
            return self.data
            
        except InvalidFileException as e:
            logger.error(f"Excel 파일 손상: {e}")
            raise Exception(ERROR_EXCEL_INVALID)
        except Exception as e:
            logger.error(f"Excel 읽기 실패: {e}")
            raise
    
    def get_columns(self) -> List[str]:
        """칼럼명 목록 반환"""
        return self.columns
    
    def get_row_count(self) -> int:
        """데이터 행 개수 반환"""
        if not self.data or not self.columns:
            return 0
        return len(self.data[self.columns[0]])
    
    def get_row(self, index: int) -> Dict[str, Any]:
        """특정 행의 데이터 반환 (0-based index)"""
        row = {}
        for col in self.columns:
            row[col] = self.data[col][index] if index < len(self.data[col]) else ""
        return row
```

- [ ] **Step 4: 테스트 실행 (통과 확인)**

```bash
pytest tests/test_excel_reader.py::test_read_valid_excel -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add core/__init__.py core/excel_reader.py tests/test_excel_reader.py
git commit -m "feat: implement ExcelReader class with column extraction"
```

---

### Task 6: Excel Reader 테스트 추가 (error cases)

**Files:**
- Modify: `tests/test_excel_reader.py`

- [ ] **Step 1: 추가 테스트 작성 (손상 파일, 빈 파일)**

```python
# tests/test_excel_reader.py에 추가

def test_read_nonexistent_file():
    """존재하지 않는 파일 읽기"""
    reader = ExcelReader()
    with pytest.raises(FileNotFoundError):
        reader.read("nonexistent.xlsx")

def test_read_empty_excel():
    """빈 Excel 파일 읽기"""
    # 임시 빈 Excel 파일 생성
    from openpyxl import Workbook
    from tempfile import NamedTemporaryFile
    
    wb = Workbook()
    ws = wb.active
    # 아무 데이터도 추가하지 않음
    
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        wb.save(tmp.name)
        reader = ExcelReader()
        with pytest.raises(Exception):
            reader.read(tmp.name)
```

- [ ] **Step 2: 테스트 실행**

```bash
pytest tests/test_excel_reader.py -v
```

Expected: 모든 테스트 통과

- [ ] **Step 3: Commit**

```bash
git add tests/test_excel_reader.py
git commit -m "test: add error case tests for ExcelReader"
```

---

### Task 7: HWPX Processor 구현 - Part 1 (ZIP 처리)

**Files:**
- Create: `core/hwpx_processor.py`
- Create: `tests/test_hwpx_processor.py`

- [ ] **Step 1: 기본 테스트 작성**

```python
# tests/test_hwpx_processor.py
import pytest
from core.hwpx_processor import HWPXProcessor

def test_extract_hwpx():
    """HWPX ZIP 추출"""
    processor = HWPXProcessor()
    # sample_template.hwpx가 존재한다고 가정
    xml_files = processor.extract_hwpx("sample_template.hwpx")
    
    assert xml_files is not None
    assert "content.xml" in xml_files or len(xml_files) > 0
```

- [ ] **Step 2: HWPXProcessor 클래스 구현 - ZIP 처리**

```python
# core/hwpx_processor.py
"""
HWPX 파일 처리 (ZIP 기반 컨테이너)
"""
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple
from utils.logger import logger
from utils.constants import ERROR_HWPX_INVALID, TEMP_DIR_PREFIX


class HWPXProcessor:
    """HWPX 파일 처리 (XML 파싱, 플레이스홀더 치환)"""
    
    def __init__(self):
        self.temp_dir = None
        self.xml_files = {}
    
    def extract_hwpx(self, hwpx_path: str) -> Dict[str, str]:
        """
        HWPX ZIP에서 XML 파일 추출
        
        Args:
            hwpx_path: HWPX 파일 경로
        
        Returns:
            {파일명: 내용} 딕셔너리
        
        Raises:
            Exception: HWPX 파일 유효하지 않음
        """
        try:
            self.temp_dir = tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX)
            path = Path(hwpx_path)
            
            if not path.exists():
                raise FileNotFoundError(f"HWPX 파일 없음: {hwpx_path}")
            
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # XML 파일 읽기
            temp_path = Path(self.temp_dir)
            for xml_file in temp_path.glob("**/*.xml"):
                rel_path = xml_file.relative_to(temp_path)
                with open(xml_file, 'r', encoding='utf-8') as f:
                    self.xml_files[str(rel_path)] = f.read()
            
            logger.info(f"HWPX 추출 완료: {len(self.xml_files)}개 XML 파일")
            return self.xml_files
            
        except zipfile.BadZipFile:
            logger.error(f"HWPX ZIP 손상: {hwpx_path}")
            raise Exception(ERROR_HWPX_INVALID)
        except Exception as e:
            logger.error(f"HWPX 추출 실패: {e}")
            raise
    
    def cleanup(self):
        """임시 디렉토리 정리"""
        if self.temp_dir and Path(self.temp_dir).exists():
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.debug(f"임시 디렉토리 정리: {self.temp_dir}")
```

- [ ] **Step 3: 테스트 실행**

```bash
pytest tests/test_hwpx_processor.py::test_extract_hwpx -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add core/hwpx_processor.py tests/test_hwpx_processor.py
git commit -m "feat: implement HWPXProcessor with ZIP extraction"
```

---

### Task 8: HWPX Processor - 플레이스홀더 추출 및 치환

**Files:**
- Modify: `core/hwpx_processor.py`
- Modify: `tests/test_hwpx_processor.py`

- [ ] **Step 1: 플레이스홀더 추출 테스트 작성**

```python
# tests/test_hwpx_processor.py에 추가

def test_extract_placeholders():
    """HWPX에서 플레이스홀더 추출"""
    processor = HWPXProcessor()
    processor.extract_hwpx("sample_template.hwpx")
    placeholders = processor.extract_placeholders()
    
    assert placeholders is not None
    assert isinstance(placeholders, set)
    # sample_template.hwpx에 {{이름}}, {{주소}} 등이 있다고 가정
    assert len(placeholders) > 0
```

- [ ] **Step 2: HWPXProcessor에 플레이스홀더 메서드 추가**

```python
# core/hwpx_processor.py에 추가

import re
from utils.helpers import extract_placeholders as helper_extract_placeholders

    def extract_placeholders(self) -> set:
        """
        HWPX 내 모든 플레이스홀더 추출
        
        Returns:
            플레이스홀더 이름 집합
        """
        placeholders = set()
        for content in self.xml_files.values():
            placeholders.update(helper_extract_placeholders(content))
        logger.info(f"플레이스홀더 추출 완료: {placeholders}")
        return placeholders
    
    def replace_placeholders(self, data: Dict[str, str]) -> bool:
        """
        XML 파일의 플레이스홀더 치환 (XML 파서 사용)
        
        Args:
            data: {칼럼명: 값} 딕셔너리
        
        Returns:
            성공 여부
        """
        try:
            for file_name, content in self.xml_files.items():
                # XML 파싱
                root = ET.fromstring(content)
                
                # 모든 텍스트 노드에서 플레이스홀더 치환
                self._replace_in_element(root, data)
                
                # 수정된 XML 저장
                modified_xml = ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
                self.xml_files[file_name] = modified_xml
            
            logger.info("플레이스홀더 치환 완료")
            return True
        except Exception as e:
            logger.error(f"플레이스홀더 치환 실패: {e}")
            raise
    
    def _replace_in_element(self, element, data: Dict[str, str]):
        """재귀적으로 요소의 텍스트에서 플레이스홀더 치환"""
        if element.text:
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                element.text = element.text.replace(placeholder, str(value or ""))
        
        if element.tail:
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                element.tail = element.tail.replace(placeholder, str(value or ""))
        
        for child in element:
            self._replace_in_element(child, data)
    
    def save_hwpx(self, output_path: str) -> bool:
        """
        수정된 HWPX를 새 파일로 저장
        
        Args:
            output_path: 출력 HWPX 파일 경로
        
        Returns:
            성공 여부
        """
        try:
            # 임시 XML 파일들을 원본 구조로 복원
            temp_path = Path(self.temp_dir)
            for file_name, content in self.xml_files.items():
                file_path = temp_path / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # ZIP으로 다시 압축
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_path)
                        zip_ref.write(file_path, arcname)
            
            logger.info(f"HWPX 저장 완료: {output_path}")
            return True
        except Exception as e:
            logger.error(f"HWPX 저장 실패: {e}")
            raise
```

- [ ] **Step 3: 플레이스홀더 치환 테스트 추가**

```python
# tests/test_hwpx_processor.py에 추가

def test_replace_placeholders():
    """플레이스홀더 치환"""
    processor = HWPXProcessor()
    processor.extract_hwpx("sample_template.hwpx")
    
    data = {"이름": "김철수", "주소": "서울시", "계약금액": "1,000,000"}
    result = processor.replace_placeholders(data)
    
    assert result == True
    
    # 임시 파일로 저장 후 확인
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".hwpx", delete=False) as tmp:
        processor.save_hwpx(tmp.name)
        assert Path(tmp.name).exists()
        processor.cleanup()
```

- [ ] **Step 4: 테스트 실행**

```bash
pytest tests/test_hwpx_processor.py -v
```

Expected: 모든 테스트 통과

- [ ] **Step 5: Commit**

```bash
git add core/hwpx_processor.py tests/test_hwpx_processor.py
git commit -m "feat: add placeholder extraction and replacement (XML parser)"
```

---

### Phase 3: Validator 모듈 (Task 9-10)

### Task 9: Validator 구현 (Dry-run 검증)

**Files:**
- Create: `core/validator.py`
- Create: `tests/test_validator.py`

- [ ] **Step 1: 테스트 작성**

```python
# tests/test_validator.py
import pytest
from core.excel_reader import ExcelReader
from core.hwpx_processor import HWPXProcessor
from core.validator import Validator


def test_validate_mapping():
    """칼럼/플레이스홀더 매핑 검증"""
    # Excel과 HWPX 로드
    excel_reader = ExcelReader()
    excel_reader.read("sample_data.xlsx")
    
    hwpx_processor = HWPXProcessor()
    hwpx_processor.extract_hwpx("sample_template.hwpx")
    
    # 검증
    validator = Validator(excel_reader, hwpx_processor)
    result = validator.validate()
    
    assert result is not None
    assert "matched" in result
    assert "missing" in result
    assert "unused" in result
```

- [ ] **Step 2: Validator 클래스 구현**

```python
# core/validator.py
"""
Dry-run 검증 엔진
"""
from typing import Dict, List, Set
from utils.logger import logger


class ValidationResult:
    """검증 결과"""
    def __init__(self):
        self.excel_columns: Set[str] = set()
        self.hwpx_placeholders: Set[str] = set()
        self.matched: Set[str] = set()  # 매칭된 필드
        self.missing: Set[str] = set()  # HWPX에 있지만 Excel에 없는 필드
        self.unused: Set[str] = set()   # Excel에는 있지만 HWPX에 없는 필드
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "excel_columns": list(self.excel_columns),
            "hwpx_placeholders": list(self.hwpx_placeholders),
            "matched": list(self.matched),
            "missing": list(self.missing),
            "unused": list(self.unused)
        }


class Validator:
    """Excel과 HWPX 매핑 검증"""
    
    def __init__(self, excel_reader, hwpx_processor):
        """
        Args:
            excel_reader: ExcelReader 인스턴스
            hwpx_processor: HWPXProcessor 인스턴스
        """
        self.excel_reader = excel_reader
        self.hwpx_processor = hwpx_processor
    
    def validate(self) -> ValidationResult:
        """
        Excel 칼럼과 HWPX 플레이스홀더 매핑 검증
        
        Returns:
            ValidationResult 객체
        """
        result = ValidationResult()
        
        # Excel 칼럼 추출
        result.excel_columns = set(self.excel_reader.get_columns())
        
        # HWPX 플레이스홀더 추출
        result.hwpx_placeholders = self.hwpx_processor.extract_placeholders()
        
        # 매핑 분석
        result.matched = result.excel_columns & result.hwpx_placeholders
        result.missing = result.hwpx_placeholders - result.excel_columns
        result.unused = result.excel_columns - result.hwpx_placeholders
        
        # 로그 기록
        logger.info(f"검증 결과:")
        logger.info(f"  - Excel 칼럼: {result.excel_columns}")
        logger.info(f"  - HWPX 플레이스홀더: {result.hwpx_placeholders}")
        logger.info(f"  - 매칭됨: {result.matched}")
        logger.info(f"  - 누락: {result.missing}")
        logger.info(f"  - 미사용: {result.unused}")
        
        return result
    
    def is_valid(self) -> bool:
        """
        검증 통과 여부 (누락된 필드 없음)
        
        Returns:
            모든 플레이스홀더가 매칭되었으면 True
        """
        result = self.validate()
        return len(result.missing) == 0
```

- [ ] **Step 3: 테스트 실행**

```bash
pytest tests/test_validator.py -v
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add core/validator.py tests/test_validator.py
git commit -m "feat: implement Validator for dry-run check"
```

---

### Phase 4: UI 모듈 (Task 11-14)

### Task 10: Main Window 기본 구조 (PySide6)

**Files:**
- Create: `ui/main_window.py`
- Create: `ui/styles.qss`

- [ ] **Step 1: styles.qss 작성 (스타일시트)**

```css
/* ui/styles.qss */
QMainWindow {
    background-color: #f0f0f0;
}

QLabel {
    color: #333333;
    font-family: "Segoe UI", "맑은 고딕";
    font-size: 10pt;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
    font-family: "Segoe UI", "맑은 고딕";
}

QPushButton:hover {
    background-color: #005a9e;
}

QPushButton:pressed {
    background-color: #003f73;
}

QLineEdit {
    padding: 6px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: white;
}

QTextEdit {
    border: 1px solid #cccccc;
    background-color: white;
    font-family: "Consolas", "Courier New";
    font-size: 9pt;
}
```

- [ ] **Step 2: Main Window 기본 구조**

```python
# ui/main_window.py
"""
PySide6 기반 메인 GUI 창
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog,
    QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from pathlib import Path
from utils.logger import logger, get_logs


class MainWindow(QMainWindow):
    """메인 창"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("계약서 자동작성 도구")
        self.setGeometry(100, 100, 900, 700)
        
        # 선택된 파일 경로
        self.excel_path = ""
        self.hwpx_path = ""
        self.output_dir = ""
        self.filename_column = None
        
        self.init_ui()
        self.load_styles()
    
    def init_ui(self):
        """UI 초기화"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 1. Excel 파일 선택
        excel_layout = QHBoxLayout()
        excel_layout.addWidget(QLabel("Excel 파일:"))
        self.excel_input = QLineEdit()
        self.excel_input.setReadOnly(True)
        excel_layout.addWidget(self.excel_input)
        excel_btn = QPushButton("선택")
        excel_btn.clicked.connect(self.select_excel)
        excel_layout.addWidget(excel_btn)
        main_layout.addLayout(excel_layout)
        
        # 2. HWPX 템플릿 선택
        hwpx_layout = QHBoxLayout()
        hwpx_layout.addWidget(QLabel("HWPX 템플릿:"))
        self.hwpx_input = QLineEdit()
        self.hwpx_input.setReadOnly(True)
        hwpx_layout.addWidget(self.hwpx_input)
        hwpx_btn = QPushButton("선택")
        hwpx_btn.clicked.connect(self.select_hwpx)
        hwpx_layout.addWidget(hwpx_btn)
        main_layout.addLayout(hwpx_layout)
        
        # 3. 출력 폴더 선택
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("출력 폴더:"))
        self.output_input = QLineEdit()
        self.output_input.setReadOnly(True)
        output_layout.addWidget(self.output_input)
        output_btn = QPushButton("선택")
        output_btn.clicked.connect(self.select_output)
        output_layout.addWidget(output_btn)
        main_layout.addLayout(output_layout)
        
        # 4. 파일명 칼럼 선택
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("파일명 기준:"))
        self.filename_combo = QComboBox()
        self.filename_combo.addItem("행번호 (row_1, row_2, ...)")
        filename_layout.addWidget(self.filename_combo)
        main_layout.addLayout(filename_layout)
        
        # 5. 버튼 영역
        button_layout = QHBoxLayout()
        diagnose_btn = QPushButton("문제 진단 (Dry-run)")
        diagnose_btn.clicked.connect(self.diagnose)
        button_layout.addWidget(diagnose_btn)
        
        generate_btn = QPushButton("생성 시작")
        generate_btn.setStyleSheet("background-color: #28a745;")
        generate_btn.clicked.connect(self.generate)
        button_layout.addWidget(generate_btn)
        main_layout.addLayout(button_layout)
        
        # 6. 로그 영역
        main_layout.addWidget(QLabel("진행 상황:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        main_layout.addWidget(self.log_text)
        
        central_widget.setLayout(main_layout)
    
    def load_styles(self):
        """스타일시트 로드"""
        style_path = Path(__file__).parent / "styles.qss"
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
    
    def select_excel(self):
        """Excel 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel 파일 선택", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            self.excel_path = file_path
            self.excel_input.setText(file_path)
            logger.info(f"Excel 파일 선택: {file_path}")
            self.update_log()
    
    def select_hwpx(self):
        """HWPX 템플릿 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "HWPX 템플릿 선택", "", "HWPX Files (*.hwpx)"
        )
        if file_path:
            self.hwpx_path = file_path
            self.hwpx_input.setText(file_path)
            logger.info(f"HWPX 템플릿 선택: {file_path}")
            self.update_log()
    
    def select_output(self):
        """출력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "출력 폴더 선택"
        )
        if folder_path:
            self.output_dir = folder_path
            self.output_input.setText(folder_path)
            logger.info(f"출력 폴더 선택: {folder_path}")
            self.update_log()
    
    def diagnose(self):
        """Dry-run 검증"""
        QMessageBox.information(self, "알림", "아직 구현되지 않음")
    
    def generate(self):
        """배치 생성 시작"""
        QMessageBox.information(self, "알림", "아직 구현되지 않음")
    
    def update_log(self):
        """로그 텍스트 업데이트"""
        self.log_text.setText(get_logs())
```

- [ ] **Step 3: Commit**

```bash
git add ui/__init__.py ui/main_window.py ui/styles.qss
git commit -m "feat: create main window UI with PySide6"
```

---

### Task 11: Progress Dialog 구현

**Files:**
- Create: `ui/progress_dialog.py`

- [ ] **Step 1: Progress Dialog 작성**

```python
# ui/progress_dialog.py
"""
배치 처리 진행률 표시 다이얼로그
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
)
from PySide6.QtCore import Qt


class ProgressDialog(QDialog):
    """진행률 표시"""
    
    def __init__(self, parent=None, total_count=0):
        super().__init__(parent)
        self.setWindowTitle("배치 처리 중...")
        self.setGeometry(200, 200, 500, 150)
        self.setModal(True)
        self.total_count = total_count
        self.current_count = 0
        
        self.init_ui()
    
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        
        self.status_label = QLabel(f"0/{self.total_count} 처리 중...")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.total_count)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn)
        
        self.setLayout(layout)
    
    def update_progress(self, current_count: int, message: str = ""):
        """진행률 업데이트"""
        self.current_count = current_count
        self.progress_bar.setValue(current_count)
        
        if message:
            self.status_label.setText(f"{current_count}/{self.total_count} - {message}")
        else:
            self.status_label.setText(f"{current_count}/{self.total_count} 처리 중...")
    
    def set_complete(self):
        """완료 상태로 설정"""
        self.progress_bar.setValue(self.total_count)
        self.status_label.setText(f"{self.total_count}/{self.total_count} 완료!")
        self.cancel_btn.setText("닫기")
```

- [ ] **Step 2: Commit**

```bash
git add ui/progress_dialog.py
git commit -m "feat: add progress dialog for batch processing"
```

---

### Task 12: Main 진입점 작성

**Files:**
- Create: `main.py`

- [ ] **Step 1: main.py 작성**

```python
# main.py
"""
계약서 자동작성 도구 - 메인 진입점
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import logger


def main():
    """메인 함수"""
    logger.info("="*50)
    logger.info("계약서 자동작성 도구 시작")
    logger.info("="*50)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    logger.info("GUI 창 표시")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 실행 테스트**

```bash
python main.py
```

Expected: GUI 창이 표시됨

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point for GUI application"
```

---

### Phase 5: 배치 처리 로직 (Task 13-15)

### Task 13: 배치 처리 컨트롤러 구현

**Files:**
- Create: `core/batch_processor.py`

- [ ] **Step 1: Batch Processor 작성**

```python
# core/batch_processor.py
"""
배치 처리 엔진 (All-or-Nothing)
"""
from pathlib import Path
from typing import Callable, Optional, Tuple
from core.excel_reader import ExcelReader
from core.hwpx_processor import HWPXProcessor
from core.validator import Validator
from utils.logger import logger
from utils.helpers import normalize_filename


class BatchProcessor:
    """배치 처리"""
    
    def __init__(self, excel_path: str, hwpx_path: str, output_dir: str):
        self.excel_path = excel_path
        self.hwpx_path = hwpx_path
        self.output_dir = output_dir
        self.progress_callback: Optional[Callable] = None
        self.total_rows = 0
    
    def set_progress_callback(self, callback: Callable):
        """진행 상황 콜백 설정"""
        self.progress_callback = callback
    
    def process(self, filename_column: Optional[str] = None) -> Tuple[bool, str]:
        """
        배치 처리 (All-or-Nothing)
        
        Args:
            filename_column: 파일명으로 사용할 칼럼명 (없으면 행번호)
        
        Returns:
            (성공 여부, 메시지)
        """
        try:
            logger.info("배치 처리 시작")
            
            # 1. Excel 읽기
            logger.info(f"Excel 파일 읽기: {self.excel_path}")
            excel_reader = ExcelReader()
            excel_reader.read(self.excel_path)
            
            self.total_rows = excel_reader.get_row_count()
            logger.info(f"총 {self.total_rows}개 행 발견")
            
            # 2. HWPX 검증
            logger.info(f"HWPX 템플릿 검증: {self.hwpx_path}")
            hwpx_processor = HWPXProcessor()
            hwpx_processor.extract_hwpx(self.hwpx_path)
            
            # 3. 매핑 검증
            logger.info("매핑 검증")
            validator = Validator(excel_reader, hwpx_processor)
            result = validator.validate()
            
            if result.missing:
                msg = f"누락된 필드: {', '.join(result.missing)}"
                logger.error(msg)
                return False, msg
            
            # 4. 배치 처리 루프 (All-or-Nothing)
            for row_idx in range(self.total_rows):
                try:
                    # 행 데이터 추출
                    row_data = excel_reader.get_row(row_idx)
                    
                    # 파일명 생성
                    if filename_column and filename_column in row_data:
                        base_name = normalize_filename(row_data[filename_column])
                        if not base_name:
                            base_name = f"row_{row_idx+1}"
                    else:
                        base_name = f"row_{row_idx+1}"
                    
                    filename = f"{base_name}.hwpx"
                    output_path = Path(self.output_dir) / filename
                    
                    # 중복 처리
                    counter = 1
                    original_output_path = output_path
                    while output_path.exists():
                        base_name_new = f"{base_name}_{counter}"
                        filename = f"{base_name_new}.hwpx"
                        output_path = Path(self.output_dir) / filename
                        counter += 1
                    
                    # HWPX 생성
                    logger.info(f"[{row_idx+1}/{self.total_rows}] {filename} 생성 중...")
                    
                    # 새로운 processor 인스턴스 (각 행마다)
                    processor = HWPXProcessor()
                    processor.extract_hwpx(self.hwpx_path)
                    processor.replace_placeholders(row_data)
                    processor.save_hwpx(str(output_path))
                    processor.cleanup()
                    
                    logger.info(f"[{row_idx+1}/{self.total_rows}] ✓ {filename} 완료")
                    
                    # 진행 콜백
                    if self.progress_callback:
                        self.progress_callback(row_idx + 1, filename)
                
                except Exception as e:
                    logger.error(f"[{row_idx+1}/{self.total_rows}] ✗ 처리 실패: {e}", exc_info=True)
                    return False, f"행 {row_idx+1}에서 오류 발생: {str(e)}"
            
            logger.info("="*50)
            logger.info(f"배치 처리 완료: {self.total_rows}개 파일 생성")
            logger.info("="*50)
            
            return True, f"{self.total_rows}개 파일이 생성되었습니다."
        
        except Exception as e:
            logger.error(f"배치 처리 실패: {e}", exc_info=True)
            return False, f"배치 처리 중 오류 발생: {str(e)}"
```

- [ ] **Step 2: Commit**

```bash
git add core/batch_processor.py
git commit -m "feat: implement batch processor with all-or-nothing error handling"
```

---

### Task 14: Main Window에 배치 처리 로직 연결

**Files:**
- Modify: `ui/main_window.py`

- [ ] **Step 1: diagnose와 generate 메서드 구현**

```python
# ui/main_window.py의 diagnose와 generate 메서드 수정

def diagnose(self):
    """Dry-run 검증"""
    if not self.excel_path or not self.hwpx_path:
        QMessageBox.warning(self, "경고", "Excel과 HWPX 파일을 선택해주세요.")
        return
    
    try:
        from core.excel_reader import ExcelReader
        from core.hwpx_processor import HWPXProcessor
        from core.validator import Validator
        
        logger.info("Dry-run 검증 시작...")
        
        excel_reader = ExcelReader()
        excel_reader.read(self.excel_path)
        
        hwpx_processor = HWPXProcessor()
        hwpx_processor.extract_hwpx(self.hwpx_path)
        
        validator = Validator(excel_reader, hwpx_processor)
        result = validator.validate()
        
        # 파일명 칼럼 업데이트
        self.filename_combo.clear()
        self.filename_combo.addItem("행번호 (row_1, row_2, ...)", None)
        for col in result.excel_columns:
            self.filename_combo.addItem(col, col)
        
        # 결과 메시지
        msg = f"""
✓ Excel 칼럼 ({len(result.excel_columns)}개): {', '.join(sorted(result.excel_columns))}

✓ HWPX 플레이스홀더 ({len(result.hwpx_placeholders)}개): {', '.join(sorted(result.hwpx_placeholders))}

✓ 매칭된 필드 ({len(result.matched)}개): {', '.join(sorted(result.matched))}
"""
        
        if result.missing:
            msg += f"\n⚠ 누락된 필드 ({len(result.missing)}개): {', '.join(sorted(result.missing))}"
        
        if result.unused:
            msg += f"\n⚠ 미사용 칼럼 ({len(result.unused)}개): {', '.join(sorted(result.unused))}"
        
        self.update_log()
        QMessageBox.information(self, "검증 결과", msg)
        
    except Exception as e:
        logger.error(f"검증 실패: {e}", exc_info=True)
        self.update_log()
        QMessageBox.critical(self, "오류", f"검증 실패: {str(e)}")


def generate(self):
    """배치 생성 시작"""
    if not self.excel_path or not self.hwpx_path or not self.output_dir:
        QMessageBox.warning(self, "경고", "모든 파일과 폴더를 선택해주세요.")
        return
    
    try:
        from core.batch_processor import BatchProcessor
        from ui.progress_dialog import ProgressDialog
        from pathlib import Path
        import os
        
        # 파일명 칼럼 가져오기
        filename_column = self.filename_combo.currentData()
        
        logger.info(f"배치 처리 시작 (파일명 칼럼: {filename_column})")
        
        # 배치 처리
        processor = BatchProcessor(
            self.excel_path,
            self.hwpx_path,
            self.output_dir
        )
        
        # 진행 다이얼로그 표시
        progress = ProgressDialog(self, processor.total_rows)
        processor.set_progress_callback(
            lambda current, filename: progress.update_progress(current, filename)
        )
        
        # 배치 처리 실행
        success, message = processor.process(filename_column)
        
        self.update_log()
        
        if success:
            progress.set_complete()
            reply = QMessageBox.information(
                self, "완료", message + "\n\n출력 폴더를 열까요?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                os.startfile(self.output_dir)  # Windows에서 폴더 열기
        else:
            QMessageBox.critical(self, "오류", f"생성 실패: {message}")
    
    except Exception as e:
        logger.error(f"배치 처리 실패: {e}", exc_info=True)
        self.update_log()
        QMessageBox.critical(self, "오류", f"배치 처리 실패: {str(e)}")
```

- [ ] **Step 2: Commit**

```bash
git add ui/main_window.py
git commit -m "feat: integrate batch processing logic with GUI"
```

---

### Phase 6: 빌드 및 최종 테스트 (Task 15-19)

### Task 15: PyInstaller 빌드 스크립트 작성

**Files:**
- Create: `build/build.py`

- [ ] **Step 1: build.py 작성**

```python
# build/build.py
"""
PyInstaller 빌드 스크립트
"""
import subprocess
import sys
from pathlib import Path


def build():
    """EXE 빌드"""
    project_root = Path(__file__).parent.parent
    icon_path = project_root / "resources" / "icon.ico"
    main_py = project_root / "main.py"
    
    print("계약서 자동작성 도구 빌드 시작...")
    
    # PyInstaller 명령
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # 단일 파일로 패킹
        "--windowed",  # 콘솔 창 숨김
        f"--icon={icon_path}",  # 아이콘
        "--name=contract_generator",  # 실행 파일명
        "--distpath=dist",  # 출력 디렉토리
        "--buildpath=build_temp",
        str(main_py)
    ]
    
    print(f"명령: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=str(project_root))
    
    if result.returncode == 0:
        print("✓ 빌드 완료!")
        print(f"출력: {project_root / 'dist' / 'contract_generator.exe'}")
    else:
        print("✗ 빌드 실패!")
        sys.exit(1)


if __name__ == "__main__":
    build()
```

- [ ] **Step 2: 샘플 아이콘 생성 (간단한 ICO)**

샘플 icon.ico는 수동으로 생성하거나 온라인 도구 사용

- [ ] **Step 3: Commit**

```bash
git add build/build.py
git commit -m "feat: add PyInstaller build script"
```

---

### Task 16: README.md 작성

**Files:**
- Create: `README.md`

- [ ] **Step 1: README.md 작성**

```markdown
# 계약서 자동작성 도구 (Contract Generator)

한국어 계약서를 대량으로 자동 생성하는 Windows 데스크톱 애플리케이션입니다.

## 기능

- **배치 처리**: Excel 파일의 각 행마다 개별 계약서 HWPX 파일 자동 생성
- **플레이스홀더 치환**: {{이름}}, {{주소}} 등의 동적 값 자동 치환
- **검증**: 생성 전 Dry-run을 통한 사전 점검
- **사용자 친화적 GUI**: 비개발자도 쉽게 사용

## 설치 및 실행

### 방법 1: EXE 실행 (권장)

1. `contract_generator.exe` 다운로드
2. 더블클릭하여 실행

### 방법 2: 소스 코드에서 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
python main.py
```

## 사용 방법

1. **Excel 파일 선택**: 계약 대상자 정보가 담긴 .xlsx 파일 선택
2. **HWPX 템플릿 선택**: 계약서 템플릿 (.hwpx) 파일 선택
3. **출력 폴더 선택**: 생성된 파일을 저장할 폴더 선택
4. **파일명 기준 선택**: 칼럼 선택 또는 행번호 사용
5. **검증**: "문제 진단" 클릭으로 Dry-run 수행
6. **생성**: "생성 시작" 클릭하여 배치 처리

## 시스템 요구사항

- **OS**: Windows 10 이상
- **메모리**: 최소 4GB
- **디스크**: 최소 500MB

## 제약사항

- 플레이스홀더는 반드시 `{{필드명}}` 형식 (중괄호 두 개)
- HWPX 파일만 지원 (한글 전용)
- 복잡한 표 또는 특수 서식은 일부 손상될 수 있음

## 오류 해결

### "Excel 파일을 읽을 수 없습니다"
- Excel 파일이 손상되지 않았는지 확인
- 파일이 이미 열려있지는 않은지 확인

### "HWPX 템플릿이 유효하지 않습니다"
- 한글 프로그램에서 .hwpx 파일이 정상적으로 저장되었는지 확인

### "출력 폴더에 쓰기 권한이 없습니다"
- 출력 폴더의 접근 권한 확인
- 다른 폴더 선택

## 개발자 가이드

### 빌드

```bash
pip install -r requirements.txt
python build/build.py
```

### 테스트

```bash
pytest tests/ -v
```

### 프로젝트 구조

```
contract_generator/
├── core/              # 비즈니스 로직
├── ui/                # GUI
├── utils/             # 공통 유틸
├── resources/         # 리소스 (아이콘, 샘플)
├── build/             # 빌드 스크립트
├── tests/             # 테스트
└── main.py            # 진입점
```

## 라이선스

MIT License

## 기술 스택

- Python 3.11+
- PySide6 (Qt for Python)
- openpyxl (Excel 처리)
- loguru (로깅)
- PyInstaller (EXE 패킹)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README"
```

---

### Task 17: .gitignore 업데이트

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: .gitignore 업데이트**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec
build_temp/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
.contract_generator/
logs/
*.hwpx~
```

- [ ] **Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: update gitignore for Python and build artifacts"
```

---

### Task 18: 샘플 데이터 및 템플릿 준비

**Files:**
- Create: `resources/sample_data.xlsx` (수동)
- Create: `resources/sample_template.hwpx` (수동)

- [ ] **Step 1: 샘플 데이터 생성**

existing 파일 `계약대상자.xlsx`를 `resources/sample_data.xlsx`로 복사

```bash
cp 계약대상자.xlsx resources/sample_data.xlsx
```

- [ ] **Step 2: 샘플 템플릿 생성**

existing 파일 `근로계약서.hwpx`를 `resources/sample_template.hwpx`로 복사

```bash
cp 근로계약서.hwpx resources/sample_template.hwpx
```

- [ ] **Step 3: Commit**

```bash
git add resources/
git commit -m "feat: add sample data and template for testing"
```

---

### Task 19: 최종 통합 테스트 및 문서화

**Files:**
- Modify: `tests/test_excel_reader.py`
- Modify: `tests/test_hwpx_processor.py`
- Modify: `tests/test_validator.py`
- Create: `tests/integration_test.py`

- [ ] **Step 1: 통합 테스트 작성**

```python
# tests/integration_test.py
"""
End-to-end 통합 테스트
"""
import pytest
from pathlib import Path
import tempfile
from core.excel_reader import ExcelReader
from core.hwpx_processor import HWPXProcessor
from core.validator import Validator
from core.batch_processor import BatchProcessor


def test_end_to_end_batch_processing():
    """전체 배치 처리 흐름 테스트"""
    # 테스트 파일
    excel_file = "resources/sample_data.xlsx"
    hwpx_file = "resources/sample_template.hwpx"
    
    # 임시 출력 디렉토리
    with tempfile.TemporaryDirectory() as temp_dir:
        # 배치 처리 실행
        processor = BatchProcessor(excel_file, hwpx_file, temp_dir)
        success, message = processor.process(filename_column=None)  # 행번호 사용
        
        # 검증
        assert success == True
        assert "완료" in message
        
        # 생성된 파일 확인
        output_dir = Path(temp_dir)
        hwpx_files = list(output_dir.glob("*.hwpx"))
        
        # sample_data.xlsx에 데이터가 있으면 파일이 생성되었을 것
        if hwpx_files:
            assert len(hwpx_files) > 0
```

- [ ] **Step 2: 테스트 실행 (70% 커버리지 검증)**

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=core --cov=ui --cov=utils --cov-report=term-missing
```

Expected: 70% 이상의 커버리지

- [ ] **Step 3: 최종 Commit**

```bash
git add tests/
git commit -m "test: add integration tests and coverage validation"
```

---

## 📋 요약

### 작업 완료 체크리스트

- [ ] Task 1-3: 기초 설정 (requirements, constants, logger)
- [ ] Task 4-8: Core 모듈 (ExcelReader, HWPXProcessor)
- [ ] Task 9-10: Validator (Dry-run 검증)
- [ ] Task 11-14: UI 모듈 (MainWindow, ProgressDialog, 배치 처리 연결)
- [ ] Task 15-19: 빌드 및 최종 테스트 (PyInstaller, README, 통합 테스트)

### 예상 개발 완료 후

1. **EXE 빌드**: `python build/build.py` → `dist/contract_generator.exe`
2. **배포**: 단일 EXE 파일로 배포 가능
3. **테스트**: `pytest tests/ -v` 로 검증

---

## 🚀 실행 방식 선택

**이 계획을 어떻게 실행할까요?**

1. **Subagent-Driven (권장)**: 각 Task마다 독립 서브에이전트 파견 → 빠르고 병렬 처리
2. **Inline Execution**: 현재 세션에서 체크포인트식 실행 → 직렬 처리

어떤 방식을 원하시나요?

