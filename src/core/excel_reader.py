"""
계약서 자동화 시스템 - Excel 읽기 모듈

openpyxl을 사용하여 Excel 파일을 읽고 데이터를 추출합니다.
"""

from pathlib import Path
from typing import List, Dict, Optional, Generator
import openpyxl
from openpyxl.utils import get_column_letter

from ..utils.logger import info, warning, error, debug
from ..utils.helpers import normalize_value, is_valid_excel_file
from ..utils.constants import (
    EXCEL_HEADER_ROW,
    EXCEL_DATA_START_ROW,
    EXCEL_CHUNK_SIZE,
)


class ExcelReader:
    """Excel 파일을 읽고 데이터를 제공하는 클래스

    특징:
    - 대용량 파일 지원 (청크 처리)
    - 칼럼 자동 감지
    - 에러 처리 및 유효성 검사
    - 메모리 효율적인 스트리밍 방식
    """

    def __init__(self, file_path: Path):
        """ExcelReader 초기화

        Args:
            file_path: Excel 파일 경로

        Raises:
            ValueError: 파일이 없거나 유효하지 않은 경우
        """
        file_path = Path(file_path)

        if not is_valid_excel_file(file_path):
            raise ValueError(f"유효하지 않은 Excel 파일: {file_path}")

        self.file_path = file_path
        self.workbook = None
        self.worksheet = None
        self.columns = []
        self.total_rows = 0
        self.current_row = 0

        self._load_workbook()
        self._extract_columns()

        info(f"Excel 파일 로드됨: {file_path}")
        info(f"칼럼: {', '.join(self.columns)}")
        info(f"데이터 행 수: {self.total_rows}")

    def _load_workbook(self) -> None:
        """Workbook 로드

        첫 번째 활성 시트를 사용합니다.
        """
        try:
            self.workbook = openpyxl.load_workbook(
                self.file_path,
                data_only=True,  # 계산된 값을 읽음
            )
            self.worksheet = self.workbook.active

            if not self.worksheet:
                raise ValueError("활성 워크시트를 찾을 수 없습니다.")

            debug(f"워크시트 로드됨: {self.worksheet.title}")

        except Exception as e:
            error(f"Workbook 로드 실패: {e}")
            raise ValueError(f"Excel 파일을 열 수 없습니다: {e}")

    def _extract_columns(self) -> None:
        """헤더 행에서 칼럼명 추출"""
        if not self.worksheet:
            raise ValueError("워크시트가 초기화되지 않았습니다.")

        try:
            # 헤더 행 읽기
            header_row = self.worksheet[EXCEL_HEADER_ROW + 1]  # openpyxl은 1-indexed

            self.columns = []
            for cell in header_row:
                if cell.value is None:
                    break  # 빈 셀에서 중단
                self.columns.append(str(cell.value).strip())

            if not self.columns:
                raise ValueError("칼럼을 찾을 수 없습니다.")

            debug(f"추출된 칼럼 ({len(self.columns)}개): {self.columns}")

            # 총 행 수 계산
            self.total_rows = self.worksheet.max_row - EXCEL_DATA_START_ROW

            if self.total_rows < 0:
                self.total_rows = 0

        except Exception as e:
            error(f"칼럼 추출 실패: {e}")
            raise ValueError(f"칼럼을 추출할 수 없습니다: {e}")

    def get_columns(self) -> List[str]:
        """칼럼명 리스트 반환

        Returns:
            칼럼명 리스트
        """
        return self.columns.copy()

    def get_total_rows(self) -> int:
        """총 데이터 행 수 반환 (헤더 제외)

        Returns:
            총 행 수
        """
        return self.total_rows

    def read_all_rows(self) -> List[Dict[str, str]]:
        """모든 데이터 행을 딕셔너리 리스트로 반환

        주의: 대용량 파일의 경우 메모리 사용량이 많을 수 있습니다.
        대용량 파일은 read_rows_chunked() 사용을 권장합니다.

        Returns:
            [{칼럼명: 값, ...}, ...]
        """
        rows = []
        for row in self.read_rows_chunked():
            rows.extend(row)
        return rows

    def read_rows_chunked(
        self,
        chunk_size: int = EXCEL_CHUNK_SIZE,
    ) -> Generator[List[Dict[str, str]], None, None]:
        """데이터 행을 청크 단위로 읽어 생성

        메모리 효율적인 스트리밍 방식입니다.

        Args:
            chunk_size: 한 번에 읽을 행의 개수

        Yields:
            청크 단위의 행 리스트 [{칼럼명: 값, ...}, ...]
        """
        if not self.worksheet:
            return

        chunk = []
        row_num = 0

        try:
            # 데이터 시작 행부터 읽기
            for excel_row in self.worksheet.iter_rows(
                min_row=EXCEL_DATA_START_ROW + 1,  # openpyxl은 1-indexed
                max_col=len(self.columns),
                values_only=True,
            ):
                if row_num > 0 and row_num % chunk_size == 0:
                    # 청크가 가득 찼으므로 yield
                    debug(f"청크 생성: {row_num - chunk_size + 1} ~ {row_num} 행")
                    yield chunk
                    chunk = []

                # 행을 딕셔너리로 변환
                row_dict = self._convert_row_to_dict(excel_row)

                # 빈 행 건너뛰기 (모든 셀이 비어있는 경우)
                if not any(row_dict.values()):
                    debug(f"빈 행 건너뛰기: {EXCEL_DATA_START_ROW + row_num + 1}")
                    continue

                chunk.append(row_dict)
                row_num += 1

                self.current_row = row_num

        except Exception as e:
            error(f"행 읽기 중 오류: {e}")
            raise

        # 남은 청크 yield
        if chunk:
            debug(f"남은 청크 생성: {len(chunk)} 행")
            yield chunk

    def read_single_row(self, row_number: int) -> Dict[str, str]:
        """특정 행을 읽음

        Args:
            row_number: 행 번호 (0-indexed, 헤더 제외)

        Returns:
            {칼럼명: 값, ...}

        Raises:
            IndexError: 행 번호가 범위를 벗어난 경우
        """
        if row_number < 0 or row_number >= self.total_rows:
            raise IndexError(f"행 번호 범위 초과: {row_number}")

        try:
            # openpyxl은 1-indexed이고, 헤더가 첫 줄
            excel_row_num = EXCEL_DATA_START_ROW + 1 + row_number
            excel_row = self.worksheet[excel_row_num]

            row_values = tuple(cell.value for cell in excel_row[: len(self.columns)])
            row_dict = self._convert_row_to_dict(row_values)

            return row_dict

        except Exception as e:
            error(f"행 읽기 실패 (행번호: {row_number}): {e}")
            raise

    def _convert_row_to_dict(self, row: tuple) -> Dict[str, str]:
        """튜플 형태의 행을 딕셔너리로 변환

        Args:
            row: 셀 값의 튜플

        Returns:
            {칼럼명: 값, ...}
        """
        row_dict = {}
        for i, column_name in enumerate(self.columns):
            if i < len(row):
                # 값 정규화 (None/NaN 처리)
                row_dict[column_name] = normalize_value(row[i])
            else:
                row_dict[column_name] = ""

        return row_dict

    def get_column_index(self, column_name: str) -> int:
        """칼럼명으로 인덱스 조회

        Args:
            column_name: 칼럼명

        Returns:
            칼럼 인덱스 (0-indexed)

        Raises:
            ValueError: 칼럼이 없는 경우
        """
        try:
            return self.columns.index(column_name)
        except ValueError:
            raise ValueError(f"칼럼을 찾을 수 없습니다: {column_name}")

    def has_column(self, column_name: str) -> bool:
        """특정 칼럼 존재 여부 확인

        Args:
            column_name: 칼럼명

        Returns:
            존재하면 True
        """
        return column_name in self.columns

    def close(self) -> None:
        """리소스 정리

        workbook 종료 및 메모리 해제
        """
        if self.workbook:
            self.workbook.close()
            info(f"Excel 파일 종료: {self.file_path}")

    def __enter__(self):
        """Context manager 지원"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 지원"""
        self.close()

    def __del__(self):
        """소멸자 - 파일 자동 종료"""
        self.close()

    def __repr__(self):
        return (
            f"ExcelReader(file={self.file_path.name}, "
            f"columns={len(self.columns)}, rows={self.total_rows})"
        )


if __name__ == "__main__":
    # 간단한 테스트
    from pathlib import Path

    # 테스트 파일이 있다면 사용
    test_file = Path("계약대상자.xlsx")
    if test_file.exists():
        try:
            reader = ExcelReader(test_file)

            print(f"=== Excel 파일 정보 ===")
            print(f"파일: {reader.file_path.name}")
            print(f"칼럼: {reader.get_columns()}")
            print(f"행 수: {reader.get_total_rows()}")

            print(f"\n=== 처음 5개 행 ===")
            for i, chunk in enumerate(reader.read_rows_chunked(chunk_size=5)):
                if i == 0:  # 첫 번째 청크만 출력
                    for j, row in enumerate(chunk[:5]):
                        print(f"행 {j + 1}: {row}")
                break

            reader.close()
        except Exception as e:
            print(f"오류: {e}")
    else:
        print("테스트 파일을 찾을 수 없습니다.")
