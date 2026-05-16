"""
계약서 자동화 시스템 - HWPX 처리 모듈

HWPX 파일(ZIP 기반)을 읽고, XML을 파싱하며, 플레이스홀더를 치환합니다.
"""

import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Optional, Set
from io import BytesIO
import xml.etree.ElementTree as ET

from ..utils.logger import info, warning, error, debug
from ..utils.helpers import (
    extract_placeholders,
    is_valid_hwpx_file,
    get_unique_filename,
)
from ..utils.constants import (
    HWPX_CONTENT_XML,
    HWPX_STYLES_XML,
    HWPX_MIME_TYPE,
    XML_ENCODING,
    TEMP_DIR,
)


class HWPXProcessor:
    """HWPX 파일을 처리하는 클래스

    특징:
    - ZIP 기반 HWPX 파일 읽기/쓰기
    - XML 안전 파싱 (ElementTree 사용)
    - 플레이스홀더 추출 및 치환
    - 원본 포맷 유지
    """

    def __init__(self, template_path: Path):
        """HWPXProcessor 초기화

        Args:
            template_path: HWPX 템플릿 파일 경로

        Raises:
            ValueError: 파일이 없거나 유효하지 않은 경우
        """
        template_path = Path(template_path)

        if not is_valid_hwpx_file(template_path):
            raise ValueError(f"유효하지 않은 HWPX 파일: {template_path}")

        self.template_path = template_path
        self.temp_dir = None
        self.placeholders = set()

        # 템플릿에서 플레이스홀더 추출
        self._extract_placeholders()

        info(f"HWPX 템플릿 로드됨: {template_path}")
        info(f"플레이스홀더: {', '.join(sorted(self.placeholders))}")

    def _extract_placeholders(self) -> None:
        """템플릿에서 모든 플레이스홀더 추출

        content.xml 파일을 읽고 플레이스홀더를 찾습니다.
        """
        try:
            with zipfile.ZipFile(self.template_path, "r") as zip_file:
                # content.xml 읽기
                if HWPX_CONTENT_XML not in zip_file.namelist():
                    warning(f"content.xml을 찾을 수 없습니다: {self.template_path}")
                    return

                content_xml = zip_file.read(HWPX_CONTENT_XML).decode(XML_ENCODING)

                # 플레이스홀더 추출
                self.placeholders = extract_placeholders(content_xml)

                debug(f"추출된 플레이스홀더: {self.placeholders}")

        except Exception as e:
            error(f"플레이스홀더 추출 실패: {e}")
            raise ValueError(f"템플릿 파일을 읽을 수 없습니다: {e}")

    def get_placeholders(self) -> Set[str]:
        """템플릿의 플레이스홀더 반환

        Returns:
            플레이스홀더 이름의 집합
        """
        return self.placeholders.copy()

    def generate_document(
        self,
        output_path: Path,
        replacements: Dict[str, str],
        overwrite: bool = False,
    ) -> Path:
        """플레이스홀더를 치환하여 새 문서 생성

        Args:
            output_path: 출력 파일 경로
            replacements: {플레이스홀더: 값} 딕셔너리
            overwrite: 기존 파일 덮어쓰기 여부

        Returns:
            생성된 파일의 Path 객체

        Raises:
            ValueError: 처리 중 오류 발생 시
        """
        output_path = Path(output_path)

        # 출력 디렉토리 생성
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 중복 처리
        if not overwrite and output_path.exists():
            original_stem = output_path.stem
            original_suffix = output_path.suffix
            counter = 1
            while output_path.exists():
                output_path = (
                    output_path.parent / f"{original_stem}_{counter}{original_suffix}"
                )
                counter += 1
            debug(f"파일명 변경: {output_path.name}")

        try:
            # 임시 디렉토리에서 HWPX 처리
            with tempfile.TemporaryDirectory() as temp_dir:
                # 1. HWPX 압축 해제
                with zipfile.ZipFile(self.template_path, "r") as zip_file:
                    zip_file.extractall(temp_dir)

                # 2. content.xml 수정
                content_xml_path = Path(temp_dir) / HWPX_CONTENT_XML
                self._replace_placeholders_in_file(content_xml_path, replacements)

                # 3. 필요시 styles.xml도 수정
                styles_xml_path = Path(temp_dir) / HWPX_STYLES_XML
                if styles_xml_path.exists():
                    self._replace_placeholders_in_file(styles_xml_path, replacements)

                # 4. 수정된 파일들을 다시 ZIP으로 압축
                self._create_hwpx_file(temp_dir, output_path)

            info(f"문서 생성 완료: {output_path}")
            return output_path

        except Exception as e:
            error(f"문서 생성 실패: {e}")
            raise ValueError(f"문서 생성 중 오류 발생: {e}")

    def _replace_placeholders_in_file(
        self,
        xml_file_path: Path,
        replacements: Dict[str, str],
    ) -> None:
        """XML 파일의 플레이스홀더 치환

        XML을 파싱하고 텍스트 노드의 플레이스홀더를 치환합니다.

        Args:
            xml_file_path: XML 파일 경로
            replacements: {플레이스홀더: 값} 딕셔너리
        """
        try:
            # XML 파싱
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # 모든 텍스트 노드를 순회하며 플레이스홀더 치환
            self._replace_in_element(root, replacements)

            # 수정된 XML 저장
            tree.write(
                xml_file_path,
                encoding=XML_ENCODING,
                xml_declaration=True,
            )

            debug(f"XML 파일 수정 완료: {xml_file_path.name}")

        except Exception as e:
            error(f"XML 파일 수정 실패 ({xml_file_path}): {e}")
            raise

    def _replace_in_element(
        self,
        element: ET.Element,
        replacements: Dict[str, str],
    ) -> None:
        """XML 요소와 그 자식 요소의 텍스트에서 플레이스홀더를 치환

        재귀적으로 모든 텍스트 노드를 탐색합니다.

        Args:
            element: XML 요소
            replacements: {플레이스홀더: 값} 딕셔너리
        """
        # 텍스트 노드 치환
        if element.text:
            element.text = self._replace_text(element.text, replacements)

        if element.tail:
            element.tail = self._replace_text(element.tail, replacements)

        # 자식 요소 재귀 처리
        for child in element:
            self._replace_in_element(child, replacements)

    def _replace_text(self, text: str, replacements: Dict[str, str]) -> str:
        """텍스트의 플레이스홀더를 치환

        Args:
            text: 원본 텍스트
            replacements: {플레이스홀더: 값} 딕셔너리

        Returns:
            치환된 텍스트
        """
        result = text
        for placeholder, value in replacements.items():
            placeholder_str = f"{{{{{placeholder}}}}}"
            result = result.replace(placeholder_str, str(value or ""))

        return result

    def _create_hwpx_file(
        self,
        source_dir: str,
        output_path: Path,
    ) -> None:
        """수정된 디렉토리를 HWPX 파일로 압축

        Args:
            source_dir: 소스 디렉토리 (HWPX 압축 해제된 디렉토리)
            output_path: 출력 파일 경로
        """
        try:
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # 모든 파일을 ZIP에 추가
                for root, dirs, files in Path(source_dir).walk(top_down=True):
                    for file in files:
                        file_path = Path(root) / file
                        # ZIP 내에서의 상대 경로
                        arcname = file_path.relative_to(source_dir)
                        zip_file.write(file_path, arcname=arcname)

            debug(f"HWPX 파일 생성 완료: {output_path}")

        except Exception as e:
            error(f"HWPX 파일 생성 실패: {e}")
            raise

    def validate_replacements(
        self,
        replacements: Dict[str, str],
    ) -> tuple[bool, Optional[str]]:
        """치환 데이터의 유효성 검사

        Args:
            replacements: {플레이스홀더: 값} 딕셔너리

        Returns:
            (유효성, 오류메시지)
        """
        # 모든 플레이스홀더에 값이 제공되었는지 확인
        for placeholder in self.placeholders:
            if placeholder not in replacements:
                return False, f"플레이스홀더 값이 누락되었습니다: {placeholder}"

        return True, None

    def __repr__(self):
        return (
            f"HWPXProcessor(template={self.template_path.name}, "
            f"placeholders={len(self.placeholders)})"
        )


if __name__ == "__main__":
    # 간단한 테스트
    test_template = Path("근로계약서.hwpx")
    if test_template.exists():
        try:
            processor = HWPXProcessor(test_template)

            print(f"=== HWPX 템플릿 정보 ===")
            print(f"파일: {processor.template_path.name}")
            print(f"플레이스홀더: {processor.get_placeholders()}")

            # 테스트 문서 생성
            test_replacements = {
                placeholder: f"테스트_{placeholder}"
                for placeholder in processor.get_placeholders()
            }

            output_file = Path("outputs") / "테스트_계약서.hwpx"
            result = processor.generate_document(output_file, test_replacements)
            print(f"\n생성된 파일: {result}")

        except Exception as e:
            print(f"오류: {e}")
    else:
        print("테스트 파일을 찾을 수 없습니다.")
