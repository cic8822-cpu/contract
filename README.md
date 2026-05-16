# 신규채용자 계약서 작성 자동화 시스템

**Excel 데이터를 기반으로 한글(HWPX) 계약서를 자동 생성하는 Windows 데스크톱 애플리케이션**

## 🎯 주요 기능

- **Excel → HWPX 자동 변환**: Excel 데이터를 읽고 HWPX 계약서 템플릿에 자동 삽입
- **배치 처리**: 100명, 1000명 등 대량의 계약서를 한 번에 생성
- **플레이스홀더 매핑**: `{{이름}}`, `{{주소}}` 등의 템플릿 변수를 자동으로 칼럼과 매칭
- **사전 검증**: 배치 처리 전에 Dry-run으로 문제를 미리 감지
- **진행률 표시**: 실시간 진행 상황을 GUI에서 확인
- **안전한 처리**: All-or-Nothing 전략으로 첫 오류 시 전체 중단 (부분 실패 방지)
- **메모리 효율**: 대용량 파일도 청크 처리로 메모리 낭비 없음

## 📋 요구사항

### 시스템 사양
- **OS**: Windows 10 이상
- **Python**: Python 3.9 이상 (소스 코드 실행 시)

### 입력 파일
- **Excel 파일** (.xlsx, .xls)
  - 첫 행: 헤더 (칼럼명)
  - 두 번째 행부터: 데이터
  
- **HWPX 템플릿** (.hwpx)
  - 한글에서 생성한 .hwpx 파일
  - `{{플레이스홀더}}` 형식으로 변수 표시
  - 예: `{{이름}}`, `{{주소}}`, `{{생일}}`

## 🚀 사용 방법

### 방법 1: EXE 파일 실행 (권장)

1. `dist/contract_generator.exe` 파일을 실행
2. GUI 창이 열림
3. 다음 단계 수행:
   - **Excel 파일 선택**: 데이터가 있는 Excel 파일
   - **계약서 양식 선택**: HWPX 템플릿 파일
   - **출력 폴더 선택**: 생성된 계약서가 저장될 폴더
4. **✓ 검증** 버튼 클릭: 사전 검증 실행
5. **▶ 계약서 생성** 버튼 클릭: 배치 처리 시작
6. 진행률을 보며 대기
7. 완료 메시지 확인 후 출력 폴더에서 생성된 계약서 확인

### 방법 2: 소스 코드 실행

#### 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd contract_generator

# 가상 환경 생성 (선택)
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

#### 프로그램 실행
```bash
# GUI 시작
python main.py
```

#### EXE 빌드
```bash
# PyInstaller로 EXE 생성
python build.py

# 또는 옵션과 함께
python build.py --clean  # 이전 빌드 정리 후 재빌드
```

생성된 EXE는 `dist/contract_generator.exe`에 위치합니다.

## 📝 Excel 파일 형식 예시

| 순번 | 이름   | 주소         | 생일       | 전화         | 임용일     |
|------|--------|--------------|-----------|--------------|-----------|
| 1    | 김철수 | 서울시 강남구 | 1990-01-15 | 010-1234-5678 | 2025-03-01 |
| 2    | 이영희 | 서울시 서초구 | 1992-05-20 | 010-2345-6789 | 2025-03-01 |
| 3    | 박민준 | 부산시 해운대구 | 1995-08-10 | 010-3456-7890 | 2025-03-01 |

## 🔧 HWPX 템플릿 작성

1. 한글에서 계약서 문서 작성
2. 변수가 들어갈 위치에 `{{칼럼명}}` 입력
   ```
   예시:
   {{이름}} 님과 교육청은 다음과 같이 계약합니다.
   - 근무지: {{주소}}
   - 임용일: {{임용일}}
   ```
3. 파일을 `.hwpx` 형식으로 저장
4. GUI에서 이 파일을 템플릿으로 선택

## 📊 GUI 설명

### 파일 선택 섹션
- **Excel 파일**: 직원 정보 데이터 파일
- **계약서 양식**: HWPX 템플릿 파일
- **출력 폴더**: 생성된 계약서 저장 폴더

### 옵션 섹션
- **행번호 사용**: `row_1.hwpx`, `row_2.hwpx` 형식으로 파일명 생성
- **칼럼 사용**: 특정 칼럼 값을 파일명으로 사용 (예: `김철수.hwpx`)

### 진행률 표시
- 프로그래스 바: 전체 진행률 시각화
- 텍스트 표시: `진행: 10/100 (10.0%)`

### 로그 창
- 실시간 처리 상황 표시
- 에러 메시지 및 경고 표시

## ⚙️ 기술 스택

| 항목 | 기술 |
|------|------|
| **언어** | Python 3.9+ |
| **GUI** | Tkinter (표준 라이브러리) |
| **Excel 읽기** | openpyxl |
| **HWPX 처리** | zipfile + xml.etree.ElementTree |
| **로깅** | loguru |
| **EXE 패키징** | PyInstaller |

## 📁 프로젝트 구조

```
contract_generator/
├── src/                          # 소스 코드
│   ├── __init__.py              # 패키지 초기화
│   ├── gui.py                   # GUI 메인 모듈
│   ├── core/                    # 핵심 기능
│   │   ├── excel_reader.py      # Excel 읽기
│   │   ├── hwpx_processor.py    # HWPX 처리
│   │   ├── validator.py         # 검증 엔진
│   │   └── batch_processor.py   # 배치 처리
│   └── utils/                   # 유틸리티
│       ├── constants.py         # 상수 정의
│       ├── logger.py            # 로깅 시스템
│       └── helpers.py           # 헬퍼 함수
├── main.py                      # 진입점
├── build.py                     # PyInstaller 빌드 스크립트
├── requirements.txt             # 의존성 목록
└── README.md                    # 이 파일
```

## 🔍 주요 클래스 및 함수

### ExcelReader
```python
reader = ExcelReader("계약대상자.xlsx")
columns = reader.get_columns()  # ['이름', '주소', ...]
total_rows = reader.get_total_rows()  # 100

# 청크 단위로 읽기 (메모리 효율)
for chunk in reader.read_rows_chunked(chunk_size=100):
    for row in chunk:
        print(row)  # {'이름': '김철수', '주소': '서울시', ...}
```

### HWPXProcessor
```python
processor = HWPXProcessor("계약서_템플릿.hwpx")
placeholders = processor.get_placeholders()  # {'이름', '주소', ...}

# 문서 생성
output_path = processor.generate_document(
    "출력/김철수.hwpx",
    {"이름": "김철수", "주소": "서울시", ...}
)
```

### Validator
```python
validator = Validator()
result = validator.validate_batch_process(
    "계약대상자.xlsx",
    "계약서_템플릿.hwpx"
)

if result.is_valid:
    print(f"✓ 검증 성공: {result.info}")
else:
    print(f"✗ 에러: {result.errors}")
    print(f"⚠ 경고: {result.warnings}")
```

### BatchProcessor
```python
processor = BatchProcessor(
    "계약대상자.xlsx",
    "계약서_템플릿.hwpx",
    "출력/"
)

result = processor.process(
    filename_column="이름",
    progress_callback=lambda curr, total: print(f"{curr}/{total}")
)

print(f"생성된 파일: {result.generated_files}개")
print(f"소요 시간: {result.execution_time_seconds:.2f}초")
```

## 🛡️ 에러 처리

### All-or-Nothing 전략
- 배치 처리 중 첫 번째 오류 발생 시 **전체 배치 중단**
- 부분적으로 생성된 파일은 **자동 롤백**
- 데이터 일관성 보장

### 검증 단계
1. 파일 존재 여부 확인
2. 파일 포맷 검증 (Excel/HWPX)
3. 칼럼-플레이스홀더 매핑 검증
4. 샘플 데이터 유효성 검사

## 📊 로그 시스템

메모리 기반 로깅:
- 최대 10,000줄 버퍼 유지
- 초과 시 오래된 내용 자동 제거
- GUI에서 실시간 표시
- 파일로 내보내기 가능

## 🔐 보안

- 템플릿 XML은 **ElementTree로 안전하게 파싱**
- 정규식 사용하지 않음 (XML 파싱으로 정확성 보장)
- 플레이스홀더는 `{{placeholder}}` 형식으로 엄격하게 검증
- 파일명은 금지된 문자 제거 후 사용

## 🐛 문제 해결

### Q: "openpyxl 모듈을 찾을 수 없습니다" 오류
```bash
pip install openpyxl
```

### Q: HWPX 파일을 열 수 없습니다
- 파일이 손상되지 않았는지 확인
- 한글에서 다시 .hwpx로 저장해보기
- 파일명에 특수문자가 없는지 확인

### Q: 생성된 계약서가 너무 큽니다
- 이미지가 많이 포함되면 파일 크기 증가
- 템플릿 파일 크기 확인

### Q: 진행이 느립니다
- 대용량 Excel 파일인 경우 시간이 걸릴 수 있음
- 컴퓨터 사양 확인 (특히 CPU, RAM)

## 📞 지원

문제가 발생했을 경우:
1. 로그 내용 확인
2. README의 문제 해결 섹션 참고
3. 관리자에게 보고

## 📄 라이선스

(조직 내부 사용)

## 🎓 개발 정보

- **개발 환경**: Python 3.9+
- **작성 일자**: 2025년 5월
- **버전**: 1.0.0

---

**행운을 빕니다! 계약서 자동화로 업무 효율을 높이세요.** 📈
