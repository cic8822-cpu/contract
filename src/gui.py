import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from src.contract_pipeline import run_contract_automation
import threading
import os

class ContractGui:
    def __init__(self, root):
        self.root = root
        self.root.title("신규채용자 계약서 작성 자동화 v1.0")
        self.root.geometry("600x500")
        
        # 1. 파일 선택 프레임
        self.create_file_selection_ui()
        
        # 2. 실행 버튼
        self.start_btn = tk.Button(root, text="계약서 생성 시작", command=self.start_process, 
                                   height=2, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.start_btn.pack(pady=20, fill="x", padx=20)
        
        # 3. 로그 창
        self.log_area = scrolledtext.ScrolledText(root, height=15)
        self.log_area.pack(padx=20, pady=10, fill="both", expand=True)
        self.log_area.insert(tk.END, "프로그램이 준비되었습니다.\n")

    def create_file_selection_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=20, padx=20, fill="x")
        
        # 엑셀 파일
        tk.Label(frame, text="엑셀 파일 명단:").grid(row=0, column=0, sticky="w")
        self.excel_entry = tk.Entry(frame)
        self.excel_entry.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(frame, text="찾기", command=self.select_excel).grid(row=0, column=2)
        
        # 한글 양식
        tk.Label(frame, text="계약서 양식(HWP):").grid(row=1, column=0, sticky="w", pady=10)
        self.template_entry = tk.Entry(frame)
        self.template_entry.grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(frame, text="찾기", command=self.select_template).grid(row=1, column=2)
        
        # 저장 폴더
        tk.Label(frame, text="저장될 폴더:").grid(row=2, column=0, sticky="w")
        self.output_entry = tk.Entry(frame)
        self.output_entry.grid(row=2, column=1, sticky="ew", padx=5)
        tk.Button(frame, text="찾기", command=self.select_output).grid(row=2, column=2)
        
        frame.columnconfigure(1, weight=1)

    def select_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if path:
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(0, path)

    def select_template(self):
        path = filedialog.askopenfilename(filetypes=[("HWP files", "*.hwp *.hwpx")])
        if path:
            self.template_entry.delete(0, tk.END)
            self.template_entry.insert(0, path)

    def select_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_process(self):
        excel = self.excel_entry.get()
        template = self.template_entry.get()
        output = self.output_entry.get()
        
        if not all([excel, template, output]):
            messagebox.showwarning("입력 누락", "모든 경로를 지정해주세요.")
            return
        
        self.start_btn.config(state="disabled")
        self.log("작업을 시작합니다...")
        
        # 별도 스레드에서 실행하여 GUI 얼지 않게 함
        threading.Thread(target=self.run_process_thread, args=(excel, template, output), daemon=True).start()

    def run_process_thread(self, excel, template, output):
        def progress(current, total, msg):
            self.root.after(0, lambda: self.log(f"[{current}/{total}] {msg}"))
            
        success, msg = run_contract_automation(excel, template, output, progress)
        
        if success:
            self.root.after(0, lambda: messagebox.showinfo("완료", msg))
        else:
            self.root.after(0, lambda: messagebox.showerror("에러", msg))
            
        self.root.after(0, lambda: self.start_btn.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ContractGui(root)
    root.mainloop()
