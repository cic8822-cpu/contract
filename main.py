"""
계약서 자동화 시스템 - 메인 진입점

GUI 애플리케이션 시작

**중요**: Python 캐시 무시하고 실행하려면:
  python -B main.py
"""

import tkinter as tk
import sys
import os
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
