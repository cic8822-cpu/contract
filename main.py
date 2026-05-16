"""
계약서 자동화 시스템 - 메인 진입점

GUI 애플리케이션 시작

**중요**: Python 캐시를 완전히 비활성화합니다.
  - sys.dont_write_bytecode = True
  - 이것으로 .pyc 파일이 생성되지 않습니다.
"""

import sys
import os

# Python 바이트코드 캐시 완전 비활성화 (가장 중요!)
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

import tkinter as tk
from pathlib import Path

# 실행 경로 설정 (EXE 배포 고려)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

# 경로 추가
sys.path.insert(0, str(BASE_DIR))

from src.gui import ContractGui
from src.utils import ensure_directories


def main():
    """메인 함수"""
    # 필요한 디렉토리 생성
    ensure_directories()

    # GUI 시작
    root = tk.Tk()
    app = ContractGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
