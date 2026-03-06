# 제품 상세 설계서 (Design) - 신규채용자 계약서 작성 자동화

## 1. 시스템 아키텍처
본 시스템은 데이터 처리 레이어, 한글 문서 자동화 레이어, 사용자 인터페이스 레이어로 구성됩니다.

### 1.1 데이터 흐름 (Data Flow)
1.  **GUI (main.py)**: 사용자가 파일 경로 선택 및 실행 버튼 클릭
2.  **Excel Parser (excel_reader.py)**: pandas를 사용하여 엑셀 데이터를 JSON/Dict 리스트로 변환
3.  **Process Orchestrator (contract_pipeline.py)**: 추출된 명단을 순회하며 HWP Writer 호출
4.  **HWP Writer (hwpx_writer.py)**: pyhwpx를 통해 한글 양식 파일을 열고 데이터를 채운 후 개별 저장

## 2. 모듈별 상세 설계

### 2.1 `excel_reader.py`
*   **Input**: 엑셀 파일 경로
*   **Logic**: `pd.read_excel()` 후 필요한 컬럼(이름, 생일 등)만 필터링하여 리스트 반환
*   **Output**: `[{'이름': '홍길동', '생일': '1990-01-01', ...}, ...]`

### 2.2 `hwpx_writer.py`
*   **Library**: `pyhwpx` 사용
*   **Function**: `fill_contract(template_path, data, output_path)`
    *   `hwp.open(template_path)`
    *   `hwp.put_field_text()` 를 사용하여 데이터 입력 (누름틀 기반)
    *   `hwp.save_as(output_path)`
    *   `hwp.FileClose()`

### 2.3 `gui.py`
*   **Library**: `tkinter`, `filedialog`
*   **Layout**: 
    *   Label/Entry/Button 세트 3개 (엑셀, 양식, 출력폴더)
    *   실행 버튼 (Start)
    *   텍스트 로그 창 (작업 진행 상황 출력)

## 3. 파일명 생성 규칙
`{임용일}_{직종}_{성명}_계약서.hwp`

## 4. 에러 처리 및 예외 상황
*   엑셀 컬럼명이 일치하지 않을 경우 경고 메시지 출력
*   한글 프로그램이 설치되어 있지 않거나 파일이 열려 있는 경우 예외 처리
*   데이터 누락 시 해당 행 건너뛰고 로그 남김
