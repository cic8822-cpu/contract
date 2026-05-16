"""
계약서 자동화 시스템 - PyInstaller 빌드 스크립트

Python 애플리케이션을 Windows EXE로 패키징합니다.
"""

import os
import sys
import subprocess
from pathlib import Path


def build_exe():
    """PyInstaller를 사용하여 EXE 빌드"""

    print("=" * 70)
    print("계약서 자동화 시스템 - PyInstaller 빌드")
    print("=" * 70)

    # 프로젝트 디렉토리
    project_dir = Path(__file__).parent.parent
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"

    print(f"\n📁 프로젝트 디렉토리: {project_dir}")
    print(f"📁 출력 디렉토리: {dist_dir}")

    # PyInstaller 명령어
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        # 메인 파일
        str(project_dir / "main.py"),
        # 옵션
        "--onefile",  # 단일 EXE 파일
        "--windowed",  # 콘솔 창 없음
        "--name",
        "contract_generator",  # EXE 이름
        "--distpath",
        str(dist_dir),  # 출력 경로
        "--buildpath",
        str(build_dir),  # 빌드 경로
        "--specpath",
        str(build_dir),  # spec 파일 경로
        "--clean",  # 이전 빌드 정리
        # 숨겨진 import (필요한 경우)
        "--hidden-import=openpyxl",
        "--hidden-import=loguru",
        # 아이콘 (선택)
        # "--icon", str(project_dir / "resources" / "icon.ico"),
    ]

    print(f"\n🔨 PyInstaller 명령어 실행...")
    print(f"   {' '.join(pyinstaller_cmd[:5])} ...")

    try:
        # PyInstaller 실행
        result = subprocess.run(
            pyinstaller_cmd,
            cwd=str(project_dir),
            check=True,
            capture_output=False,
        )

        print("\n" + "=" * 70)
        print("✓ 빌드 성공!")
        print("=" * 70)

        # 생성된 EXE 정보
        exe_path = dist_dir / "contract_generator.exe"
        if exe_path.exists():
            file_size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📦 생성된 파일:")
            print(f"   경로: {exe_path}")
            print(f"   크기: {file_size_mb:.2f} MB")
            print(f"\n💡 사용 방법:")
            print(f"   1. {exe_path}를 실행하세요")
            print(f"   2. Excel 파일과 HWPX 템플릿을 선택하세요")
            print(f"   3. 출력 폴더를 지정하고 '계약서 생성' 버튼을 클릭하세요")

        return True

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print("✗ 빌드 실패")
        print("=" * 70)
        print(f"\n오류: {e}")
        print("\n📝 해결 방법:")
        print("   1. PyInstaller 설치 확인: pip install PyInstaller")
        print("   2. 필수 모듈 설치 확인: pip install -r requirements.txt")
        print("   3. Python 버전 확인: Python 3.9 이상 필요")

        return False

    except Exception as e:
        print(f"\n예상치 못한 오류: {e}")
        return False


def clean_build():
    """이전 빌드 파일 정리"""
    project_dir = Path(__file__).parent.parent

    print("🧹 이전 빌드 파일 정리 중...")

    for directory in ["build", "dist", "__pycache__"]:
        dir_path = project_dir / directory
        if dir_path.exists():
            import shutil

            shutil.rmtree(dir_path)
            print(f"   삭제됨: {dir_path}")

    # spec 파일 정리
    for spec_file in project_dir.glob("*.spec"):
        spec_file.unlink()
        print(f"   삭제됨: {spec_file}")

    print("✓ 정리 완료\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PyInstaller 빌드 스크립트")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="이전 빌드 파일 정리",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="정리 없이 빌드 (기본값: 정리 후 빌드)",
    )

    args = parser.parse_args()

    # 정리
    if args.clean:
        clean_build()
    elif not args.no_clean:
        clean_build()

    # 빌드
    success = build_exe()

    sys.exit(0 if success else 1)
