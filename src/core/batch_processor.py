"""
계약서 자동화 시스템 - 배치 처리 모듈

Excel 데이터를 읽고 HWPX 계약서를 일괄 생성합니다.
All-or-Nothing 전략: 첫 오류에서 전체 배치 중단.
"""

from pathlib import Path
from typing import Dict, Callable, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from .excel_reader import ExcelReader
from .hwpx_processor import HWPXProcessor
from .validator import Validator, ValidationResult
from ..utils.logger import info, warning, error, debug
from ..utils.helpers import normalize_filename, get_unique_filename
from ..utils.constants import (
    ERROR_HANDLING_STRATEGY,
    FILENAME_CONFLICT_STRATEGY,
    BATCH_SIZE,
)


@dataclass
class BatchResult:
    """배치 처리 결과를 담는 데이터 클래스"""

    is_success: bool
    total_rows: int
    generated_files: int
    failed_at_row: Optional[int] = None
    error_message: Optional[str] = None
    generated_file_paths: List[Path] = field(default_factory=list)
    execution_time_seconds: float = 0.0

    def __bool__(self):
        """bool(result)로 성공 여부 확인 가능"""
        return self.is_success


class BatchProcessor:
    """Excel 데이터를 읽고 HWPX 계약서를 일괄 생성하는 클래스

    특징:
    - All-or-Nothing 처리: 첫 오류에서 전체 배치 중단
    - 진행률 콜백 지원
    - 대용량 파일 지원 (청크 처리)
    """

    def __init__(
        self,
        excel_path: Path,
        template_path: Path,
        output_dir: Path,
    ):
        """BatchProcessor 초기화

        Args:
            excel_path: Excel 파일 경로
            template_path: HWPX 템플릿 파일 경로
            output_dir: 출력 디렉토리

        Raises:
            ValueError: 파일이 없거나 유효하지 않은 경우
        """
        self.excel_path = Path(excel_path)
        self.template_path = Path(template_path)
        self.output_dir = Path(output_dir)

        # 컴포넌트 초기화
        self.excel_reader = None
        self.hwpx_processor = None
        self.validator = Validator()

        # 상태
        self.column_placeholder_mapping = {}
        self.is_validated = False

        info(f"BatchProcessor 초기화됨")
        info(f"  Excel: {self.excel_path}")
        info(f"  Template: {self.template_path}")
        info(f"  Output: {self.output_dir}")

    def process(
        self,
        filename_column: Optional[str] = None,
        use_row_number: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> BatchResult:
        """배치 처리 실행

        Args:
            filename_column: 파일명 생성에 사용할 칼럼명 (None이면 use_row_number 사용)
            use_row_number: True면 행번호를 파일명으로 사용
            progress_callback: 진행 상황 콜백 함수 (현재_행, 총_행)

        Returns:
            BatchResult 객체
        """
        start_time = datetime.now()

        try:
            info("=" * 60)
            info("배치 처리 시작")
            info("=" * 60)

            # 1단계: 검증
            info("\n[1단계] 사전 검증 실행...")
            validation_result = self.validator.validate_batch_process(
                self.excel_path,
                self.template_path,
            )

            if not validation_result.is_valid:
                error("검증 실패")
                error(self.validator.get_validation_summary(validation_result))

                return BatchResult(
                    is_success=False,
                    total_rows=0,
                    generated_files=0,
                    error_message="사전 검증 실패",
                )

            info("✓ 검증 성공")
            self.is_validated = True

            # 검증된 컴포넌트 설정
            self.excel_reader = ExcelReader(self.excel_path)
            self.hwpx_processor = HWPXProcessor(self.template_path)
            self.column_placeholder_mapping = validation_result.info.get(
                "column_placeholder_mapping", {}
            )

            # 2단계: 배치 처리
            info(
                f"\n[2단계] 배치 처리 시작 ({self.excel_reader.get_total_rows()}개 행)..."
            )

            result = self._process_batch(
                filename_column=filename_column,
                use_row_number=use_row_number,
                progress_callback=progress_callback,
            )

            # 실행 시간 계산
            result.execution_time_seconds = (
                datetime.now() - start_time
            ).total_seconds()

            # 최종 보고
            if result.is_success:
                info("\n" + "=" * 60)
                info("✓ 배치 처리 완료")
                info(f"  - 생성된 계약서: {result.generated_files}개")
                info(f"  - 소요 시간: {result.execution_time_seconds:.2f}초")
                info("=" * 60)
            else:
                error("\n" + "=" * 60)
                error("✗ 배치 처리 실패")
                error(f"  - 실패 행: {result.failed_at_row}")
                error(f"  - 오류: {result.error_message}")
                error(f"  - 생성된 계약서: {result.generated_files}개 (롤백됨)")
                error("=" * 60)

            return result

        except Exception as e:
            error(f"배치 처리 중 예상치 못한 오류: {e}")
            return BatchResult(
                is_success=False,
                total_rows=0,
                generated_files=0,
                error_message=str(e),
            )

        finally:
            # 리소스 정리
            if self.excel_reader:
                self.excel_reader.close()

    def _process_batch(
        self,
        filename_column: Optional[str],
        use_row_number: bool,
        progress_callback: Optional[Callable],
    ) -> BatchResult:
        """실제 배치 처리 로직

        All-or-Nothing 전략: 첫 오류에서 전체 배치 중단
        """
        generated_files = []
        total_rows = self.excel_reader.get_total_rows()
        current_row = 0

        try:
            # 출력 디렉토리 생성
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # 청크 단위로 처리
            for chunk in self.excel_reader.read_rows_chunked(chunk_size=BATCH_SIZE):
                for row_data in chunk:
                    current_row += 1

                    # 진행률 콜백
                    if progress_callback:
                        progress_callback(current_row, total_rows)

                    try:
                        # 파일명 결정
                        if use_row_number:
                            output_filename = f"row_{current_row}.hwpx"
                        elif filename_column and filename_column in row_data:
                            base_filename = normalize_filename(
                                row_data[filename_column]
                            )
                            output_filename = f"{base_filename}.hwpx"
                        else:
                            output_filename = f"row_{current_row}.hwpx"

                        # 중복 처리
                        unique_filename = get_unique_filename(
                            self.output_dir,
                            output_filename,
                            strategy=FILENAME_CONFLICT_STRATEGY,
                        )

                        if unique_filename is None:
                            # skip 전략에서 파일이 이미 존재
                            warning(
                                f"행 {current_row}: 파일이 이미 존재하여 건너뜀 ({output_filename})"
                            )
                            continue

                        output_path = self.output_dir / unique_filename

                        # 플레이스홀더 치환을 위한 데이터 준비
                        replacements = {}
                        for (
                            placeholder,
                            column,
                        ) in self.column_placeholder_mapping.items():
                            value = row_data.get(column, "")
                            replacements[placeholder] = value

                        # 문서 생성
                        self.hwpx_processor.generate_document(
                            output_path,
                            replacements,
                            overwrite=True,
                        )

                        generated_files.append(output_path)
                        debug(f"행 {current_row}: 생성 완료 ({unique_filename})")

                    except Exception as row_error:
                        # All-or-Nothing: 첫 오류에서 중단
                        error(f"행 {current_row} 처리 중 오류: {row_error}")

                        return BatchResult(
                            is_success=False,
                            total_rows=total_rows,
                            generated_files=len(generated_files),
                            failed_at_row=current_row,
                            error_message=str(row_error),
                            generated_file_paths=generated_files,
                        )

            # 성공
            return BatchResult(
                is_success=True,
                total_rows=total_rows,
                generated_files=len(generated_files),
                generated_file_paths=generated_files,
            )

        except Exception as e:
            error(f"배치 처리 중 오류: {e}")
            return BatchResult(
                is_success=False,
                total_rows=total_rows,
                generated_files=len(generated_files),
                failed_at_row=current_row,
                error_message=str(e),
                generated_file_paths=generated_files,
            )


if __name__ == "__main__":
    # 간단한 테스트
    from pathlib import Path

    excel_file = Path("계약대상자.xlsx")
    template_file = Path("근로계약서.hwpx")
    output_dir = Path("outputs")

    if excel_file.exists() and template_file.exists():
        processor = BatchProcessor(excel_file, template_file, output_dir)

        def progress_callback(current, total):
            percent = (current / total) * 100
            print(f"진행: {current}/{total} ({percent:.1f}%)")

        result = processor.process(
            filename_column="이름",
            progress_callback=progress_callback,
        )

        print(f"\n결과: {'성공' if result.is_success else '실패'}")
        print(f"생성된 파일: {result.generated_files}")
        if result.generated_file_paths:
            for path in result.generated_file_paths[:5]:
                print(f"  - {path}")
    else:
        print("테스트 파일을 찾을 수 없습니다.")
