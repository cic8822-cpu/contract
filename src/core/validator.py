"""
계약서 자동화 시스템 - 검증 모듈

배치 처리 전에 데이터와 템플릿의 호환성을 검증합니다.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from .excel_reader import ExcelReader
from .hwpx_processor import HWPXProcessor
from ..utils.helpers import (
    extract_placeholders,
    match_columns_to_placeholders,
    get_missing_placeholders,
)
from ..utils.logger import info, warning, error, debug


@dataclass
class ValidationResult:
    """검증 결과를 담는 데이터 클래스"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: Dict[str, any]

    def __bool__(self):
        """bool(result)로 유효성 확인 가능"""
        return self.is_valid


class Validator:
    """Excel과 HWPX 템플릿의 호환성을 검증하는 클래스

    기능:
    - 파일 존재 여부 및 포맷 검증
    - 칼럼-플레이스홀더 매핑 검증
    - 필수 데이터 존재 여부 검증
    - Dry-run: 실제 생성 없이 검증만 수행
    """

    def __init__(self):
        """Validator 초기화"""
        self.excel_reader = None
        self.hwpx_processor = None
        self.column_placeholder_mapping = {}

    def validate_batch_process(
        self,
        excel_path: Path,
        template_path: Path,
        check_data_samples: bool = True,
    ) -> ValidationResult:
        """배치 처리 가능 여부를 종합적으로 검증

        Args:
            excel_path: Excel 파일 경로
            template_path: HWPX 템플릿 파일 경로
            check_data_samples: 샘플 데이터 검증 여부

        Returns:
            ValidationResult 객체
        """
        errors = []
        warnings = []
        info_dict = {}

        try:
            # 1단계: 파일 존재 및 포맷 검증
            debug("1단계: 파일 검증 시작")
            file_errors = self._validate_files(excel_path, template_path)
            if file_errors:
                errors.extend(file_errors)
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    info=info_dict,
                )

            # 2단계: Excel 읽기
            debug("2단계: Excel 파일 로드")
            try:
                self.excel_reader = ExcelReader(excel_path)
                info_dict["excel_columns"] = self.excel_reader.get_columns()
                info_dict["excel_rows"] = self.excel_reader.get_total_rows()
            except Exception as e:
                errors.append(f"Excel 파일 로드 실패: {e}")
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    info=info_dict,
                )

            # 3단계: HWPX 로드
            debug("3단계: HWPX 템플릿 로드")
            try:
                self.hwpx_processor = HWPXProcessor(template_path)
                info_dict["hwpx_placeholders"] = list(
                    self.hwpx_processor.get_placeholders()
                )
            except Exception as e:
                errors.append(f"HWPX 템플릿 로드 실패: {e}")
                return ValidationResult(
                    is_valid=False,
                    errors=errors,
                    warnings=warnings,
                    info=info_dict,
                )

            # 4단계: 칼럼-플레이스홀더 매핑 검증
            debug("4단계: 칼럼-플레이스홀더 매핑 검증")
            mapping_errors, mapping_warnings = self._validate_mapping(
                self.excel_reader.get_columns(),
                self.hwpx_processor.get_placeholders(),
            )
            if mapping_errors:
                errors.extend(mapping_errors)
            if mapping_warnings:
                warnings.extend(mapping_warnings)

            info_dict["column_placeholder_mapping"] = self.column_placeholder_mapping

            # 5단계: 데이터 샘플 검증 (선택)
            if check_data_samples and info_dict["excel_rows"] > 0:
                debug("5단계: 샘플 데이터 검증")
                sample_warnings = self._validate_data_samples()
                if sample_warnings:
                    warnings.extend(sample_warnings)

            # 최종 판정
            is_valid = len(errors) == 0

            info(f"검증 완료: {'✓ 성공' if is_valid else '✗ 실패'}")
            info(f"  - 에러: {len(errors)}")
            info(f"  - 경고: {len(warnings)}")

            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                info=info_dict,
            )

        except Exception as e:
            error(f"검증 중 예상치 못한 오류: {e}")
            errors.append(f"검증 중 오류 발생: {e}")
            return ValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                info=info_dict,
            )

        finally:
            # 리소스 정리
            if self.excel_reader:
                self.excel_reader.close()

    def _validate_files(
        self,
        excel_path: Path,
        template_path: Path,
    ) -> List[str]:
        """파일 존재 및 포맷 검증

        Returns:
            에러 메시지 리스트
        """
        errors = []

        excel_path = Path(excel_path)
        template_path = Path(template_path)

        # Excel 파일 검증
        if not excel_path.exists():
            errors.append(f"Excel 파일을 찾을 수 없습니다: {excel_path}")
        elif not excel_path.suffix.lower() in [".xlsx", ".xls"]:
            errors.append(f"Excel 파일 형식이 아닙니다: {excel_path}")

        # HWPX 파일 검증
        if not template_path.exists():
            errors.append(f"HWPX 템플릿을 찾을 수 없습니다: {template_path}")
        elif not template_path.suffix.lower() == ".hwpx":
            errors.append(f"HWPX 파일 형식이 아닙니다: {template_path}")

        return errors

    def _validate_mapping(
        self,
        columns: List[str],
        placeholders: set,
    ) -> Tuple[List[str], List[str]]:
        """칼럼-플레이스홀더 매핑 검증

        Returns:
            (에러 메시지 리스트, 경고 메시지 리스트)
        """
        errors = []
        warnings = []

        # 플레이스홀더가 없으면 에러
        if not placeholders:
            errors.append("템플릿에서 플레이스홀더를 찾을 수 없습니다.")
            return errors, warnings

        # 칼럼이 없으면 에러
        if not columns:
            errors.append("Excel 파일에서 칼럼을 찾을 수 없습니다.")
            return errors, warnings

        # 매핑 수행
        self.column_placeholder_mapping, unmatched = match_columns_to_placeholders(
            columns,
            placeholders,
            case_insensitive=True,
        )

        # 일치하지 않는 플레이스홀더는 경고
        if unmatched:
            warning_msg = f"다음 플레이스홀더에 해당하는 칼럼이 없습니다: {', '.join(sorted(unmatched))}"
            warnings.append(warning_msg)
            debug(f"이용 가능한 칼럼: {', '.join(columns)}")

        # 사용되지 않는 칼럼은 정보성 경고
        mapped_columns = set(self.column_placeholder_mapping.values())
        unused_columns = set(columns) - mapped_columns
        if unused_columns:
            info_msg = f"사용되지 않는 칼럼: {', '.join(sorted(unused_columns))}"
            debug(info_msg)

        return errors, warnings

    def _validate_data_samples(self, sample_size: int = 5) -> List[str]:
        """샘플 데이터 검증

        첫 몇 행의 데이터를 읽고 필수 값이 있는지 확인합니다.

        Args:
            sample_size: 샘플 행 수

        Returns:
            경고 메시지 리스트
        """
        warnings = []

        if not self.excel_reader or not self.column_placeholder_mapping:
            return warnings

        # 매핑된 칼럼들
        mapped_columns = self.column_placeholder_mapping.values()

        # 샘플 행 읽기
        try:
            for i, chunk in enumerate(
                self.excel_reader.read_rows_chunked(chunk_size=sample_size)
            ):
                for j, row in enumerate(chunk):
                    # 매핑된 칼럼의 값 확인
                    empty_count = 0
                    for column in mapped_columns:
                        if not row.get(column, "").strip():
                            empty_count += 1

                    # 모든 칼럼이 비어있으면 경고
                    if empty_count == len(list(mapped_columns)):
                        warnings.append(f"행 {j + 1}의 모든 칼럼이 비어있습니다.")

                # 첫 샘플 청크만 확인
                break

        except Exception as e:
            debug(f"샘플 데이터 검증 중 오류: {e}")

        return warnings

    def get_validation_summary(self, result: ValidationResult) -> str:
        """검증 결과를 문자열로 반환

        Args:
            result: ValidationResult 객체

        Returns:
            포맷된 요약 문자열
        """
        lines = []

        lines.append("=" * 60)
        lines.append("검증 결과")
        lines.append("=" * 60)

        # 종합 판정
        status = (
            "✓ 검증 성공 - 배치 처리 가능"
            if result.is_valid
            else "✗ 검증 실패 - 배치 처리 불가"
        )
        lines.append(f"\n상태: {status}")

        # 에러
        if result.errors:
            lines.append("\n[에러]")
            for i, err in enumerate(result.errors, 1):
                lines.append(f"  {i}. {err}")

        # 경고
        if result.warnings:
            lines.append("\n[경고]")
            for i, warn in enumerate(result.warnings, 1):
                lines.append(f"  {i}. {warn}")

        # 정보
        if result.info:
            lines.append("\n[정보]")
            lines.append(
                f"  - Excel 칼럼 수: {result.info.get('excel_columns', 'N/A')}"
            )
            lines.append(f"  - Excel 행 수: {result.info.get('excel_rows', 'N/A')}")
            lines.append(
                f"  - 템플릿 플레이스홀더 수: {len(result.info.get('hwpx_placeholders', []))}"
            )

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)


if __name__ == "__main__":
    # 간단한 테스트
    from pathlib import Path

    excel_file = Path("계약대상자.xlsx")
    template_file = Path("근로계약서.hwpx")

    if excel_file.exists() and template_file.exists():
        validator = Validator()
        result = validator.validate_batch_process(excel_file, template_file)

        print(validator.get_validation_summary(result))
    else:
        print("테스트 파일을 찾을 수 없습니다.")
