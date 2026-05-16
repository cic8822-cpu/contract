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

### ⭐ 방법 1: 배치 파일 실행 (가장 간단함 - 권장)

```
1. 프로그램 폴더에서 run_contract_generator.bat 파일 찾기
2. 더블클릭해서 실행
3. 명령 프롬프트에서 Python 환경 자동 확인
4. GUI 창이 자동으로 열림
5. 계약서 생성!
```

**장점**:
- 클릭 한 번으로 실행
- Python 경로 자동 확인
- 패키지 설치 여부 자동 확인
- 친절한 오류 메시지

**자세한 내용**: `배치파일_사용설명서.md` 파일 참고

---

### 방법 2: EXE 파일 실행 (독립 실행 버전)

> **EXE 버전**: Python을 설치하지 않았으면 이 방법을 사용하세요. `dist/contract_generator.exe` 파일 크기는 약 317MB입니다.

**실행 방법**:
1. `dist/contract_generator.exe` 파일을 더블클릭
2. 프로그램이 자동으로 시작 (첫 실행 시 1-2분 로딩 가능)
3. GUI 창이 열림

**장점**:
- Python 설치 불필요
- 배치 파일과 동일한 기능
- 어디서나 바로 실행 가능

**주의**:
- 파일 크기가 크므로 다운로드/복사 시 시간이 걸릴 수 있음
- 첫 실행 시 Windows SmartScreen 경고가 나타날 수 있음 (안전한 파일)

---

### 방법 3: 소스 코드 직접 실행

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

# 또는 배치 파일 실행
run_contract_generator.bat
```

---

## 🎯 프로그램 사용 방법 (GUI 설명)

### Step 1: 파일 선택

**Excel 파일 선택**
- 데이터가 포함된 Excel 파일 (.xlsx 또는 .xls)
- 첫 행: 헤더(칼럼명) - 예: 이름, 주소, 임용일
- 두 번째 행부터: 실제 데이터

**HWPX 템플릿 선택**
- 한글에서 작성한 계약서 템플릿 (.hwpx)
- `{{칼럼명}}` 형식으로 치환 위치 표시
- 예: `{{이름}} 님과 교육청은...`

**출력 폴더 선택**
- 생성된 계약서가 저장될 폴더
- 없으면 자동 생성됨

### Step 2: 옵션 설정

**파일명 생성 방식 선택**
```
① 칼럼 선택
   - 드롭다운에서 "이름" 선택
   - 결과: 01_홍길동.hwpx, 02_이순신.hwpx, ...

② 행번호 사용
   - 자동 번호 생성
   - 결과: 1.hwpx, 2.hwpx, 3.hwpx, ...
```

### Step 3: 검증 실행

**[✓ 검증] 버튼 클릭**
```
자동으로 다음을 확인:
✓ 파일이 존재하는가?
✓ Excel 칼럼을 읽을 수 있는가?
✓ HWPX 템플릿이 유효한가?
✓ 플레이스홀더를 추출할 수 있는가?
✓ 칼럼과 플레이스홀더가 매핑되는가?
✓ 샘플 데이터가 정상인가?

결과:
✓ 검증 완료! 계약서를 생성할 준비가 되었습니다.
```

### Step 4: 계약서 생성

**[▶ 계약서 생성] 버튼 클릭**
```
생성 과정:
[████████░░░░░░░░░░░] 50% (약 2분 남음)

각 파일 생성:
✓ 01_홍길동.hwpx
✓ 02_이순신.hwpx
✓ 03_강감찬.hwpx
  처리 중...

완료 메시지:
생성 완료! 100개의 계약서가 생성되었습니다.
출력 폴더: C:\계약서\출력
```

---

## 📁 폴더 구조

```
계약서 자동작성 프로그램/
├── run_contract_generator.bat      ← 더블클릭으로 실행!
├── main.py                         ← 메인 진입점
├── build.py                        ← EXE 빌드 스크립트 (선택)
├── requirements.txt                ← 필수 패키지 목록
│
├── src/                            ← 소스 코드
│   ├── gui.py                      ← GUI 인터페이스
│   ├── core/
│   │   ├── excel_reader.py         ← Excel 읽기
│   │   ├── hwpx_processor.py       ← HWPX 처리
│   │   ├── validator.py            ← 검증 엔진
│   │   └── batch_processor.py      ← 배치 처리
│   └── utils/
│       ├── constants.py            ← 설정값
│       ├── logger.py               ← 로깅
│       └── helpers.py              ← 유틸리티
│
├── dist/                           ← 빌드 출력 (생성될 폴더)
│   └── contract_generator.exe      ← EXE 파일 (선택)
│
├── README.md                       ← 이 파일
├── 사용설명서.md                   ← 상세 사용설명서
├── 빠른시작가이드.md               ← 5분 빠른 가이드
└── 배치파일_사용설명서.md          ← 배치 파일 상세 설명
```

---

## 📚 문서 안내

| 문서 | 설명 |
|------|------|
| **README.md** | 프로젝트 개요 및 기술 정보 |
| **사용설명서.md** | 상세한 사용 방법 및 FAQ |
| **빠른시작가이드.md** | 5분 안에 시작하기 |
| **배치파일_사용설명서.md** | 배치 파일 사용법 상세 설명 |

**추천 학습 순서**:
1. 빠른시작가이드.md (5분)
2. 배치파일_사용설명서.md (10분)
3. 사용설명서.md (15분)
4. 필요 시 README.md (기술 정보)

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

## 📦 배포 버전 정보

### EXE 버전 빌드 정보

| 항목 | 내용 |
|------|------|
| **파일명** | contract_generator.exe |
| **위치** | dist/contract_generator.exe |
| **파일 크기** | 약 317 MB |
| **빌드 도구** | PyInstaller 6.20.0 |
| **Python 버전** | Python 3.14.0 |
| **포함된 라이브러리** | openpyxl, lxml, loguru, tkinter, 기타 필수 의존성 |

### 배포 옵션 선택 가이드

| 방법 | 상황 | 장점 | 단점 |
|------|------|------|------|
| **배치 파일** | Python 이미 설치됨 | 가볍고 빠름, 쉽게 수정 가능 | Python 필수 설치 |
| **EXE 파일** | Python 미설치 또는 편의성 중시 | 독립 실행, 복잡도 없음 | 파일 크기 큼 (317MB) |
| **소스 코드 직접 실행** | 개발/커스터마이징 필요 | 모든 기능 접근 가능 | 개발 지식 필요 |

---
---

**행운을 빕니다! 계약서 자동화로 업무 효율을 높이세요.** 📈
