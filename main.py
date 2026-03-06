import tkinter as tk
from src.gui import ContractGui
import sys
import os

def main():
    # 실행 시 현재 경로를 기준으로 설정 (EXE 배포 고려)
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    root = tk.Tk()
    app = ContractGui(root)
    
    # 기본 경로 설정 예시 (선택 사항)
    # app.excel_entry.insert(0, os.path.join(os.getcwd(), "명단.xlsx"))
    
    root.mainloop()

if __name__ == "__main__":
    main()
