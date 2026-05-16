"""
계약서 자동화 시스템 - GUI 모듈

Tkinter 기반 사용자 인터페이스
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
from pathlib import Path
from typing import Optional, Callable

from .core import BatchProcessor, Validator
from .utils import (
    info as log_info,
    warning as log_warning,
    error as log_error,
    get_log_content,
    clear_logs,
)
from .utils.constants import (
    APP_NAME,
    APP_VERSION,
    GUI_WINDOW_WIDTH,
    GUI_WINDOW_HEIGHT,
    GUI_COLOR_PRIMARY,
    GUI_COLOR_ERROR,
    GUI_COLOR_SUCCESS,
    GUI_FONT_NORMAL,
    GUI_FONT_BUTTON,
    GUI_FONT_TITLE,
    MESSAGES,
)


class ContractGui:
    """계약서 자동화 GUI 메인 클래스"""

    def __init__(self, root):
        """GUI 초기화

        Args:
            root: Tkinter 루트 윈도우
        """
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{GUI_WINDOW_WIDTH}x{GUI_WINDOW_HEIGHT}")

        # 상태
        self.is_processing = False
        self.processor = None

        # 파일 선택 UI 생성
        self._create_file_selection_ui()

        # 옵션 UI 생성
        self._create_options_ui()

        # 실행 버튼
        self._create_button_ui()

        # 로그 창
        self._create_log_ui()

        # 진행률 표시
        self._create_progress_ui()

        # 초기 로그
        log_info("프로그램이 시작되었습니다.")

    def _create_file_selection_ui(self):
        """파일 선택 UI 생성"""
        frame = tk.Frame(self.root)
        frame.pack(pady=15, padx=15, fill="x")

        # 제목
        title = tk.Label(
            frame,
            text="📋 파일 선택",
            font=GUI_FONT_TITLE,
            fg=GUI_COLOR_PRIMARY,
        )
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # Excel 파일
        tk.Label(frame, text="Excel 파일:", font=GUI_FONT_NORMAL).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.excel_entry = tk.Entry(frame, font=GUI_FONT_NORMAL)
        self.excel_entry.grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(
            frame,
            text="찾기",
            command=self.select_excel,
            width=8,
        ).grid(row=1, column=2)

        # HWPX 템플릿
        tk.Label(frame, text="계약서 양식:", font=GUI_FONT_NORMAL).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.template_entry = tk.Entry(frame, font=GUI_FONT_NORMAL)
        self.template_entry.grid(row=2, column=1, sticky="ew", padx=5)
        tk.Button(
            frame,
            text="찾기",
            command=self.select_template,
            width=8,
        ).grid(row=2, column=2)

        # 출력 폴더
        tk.Label(frame, text="출력 폴더:", font=GUI_FONT_NORMAL).grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.output_entry = tk.Entry(frame, font=GUI_FONT_NORMAL)
        self.output_entry.grid(row=3, column=1, sticky="ew", padx=5)
        tk.Button(
            frame,
            text="찾기",
            command=self.select_output,
            width=8,
        ).grid(row=3, column=2)

        frame.columnconfigure(1, weight=1)

    def _create_options_ui(self):
        """옵션 UI 생성"""
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=15, fill="x")

        # 제목
        title = tk.Label(
            frame,
            text="⚙️ 옵션",
            font=GUI_FONT_TITLE,
            fg=GUI_COLOR_PRIMARY,
        )
        title.pack(anchor="w", pady=(0, 5))

        # 파일명 옵션
        option_frame = tk.Frame(frame)
        option_frame.pack(fill="x")

        tk.Label(option_frame, text="파일명 생성:", font=GUI_FONT_NORMAL).pack(
            side="left"
        )

        self.filename_var = tk.StringVar(value="row_number")
        tk.Radiobutton(
            option_frame,
            text="행번호 사용",
            variable=self.filename_var,
            value="row_number",
            font=GUI_FONT_NORMAL,
        ).pack(side="left", padx=20)

        tk.Radiobutton(
            option_frame,
            text="칼럼 사용",
            variable=self.filename_var,
            value="column",
            font=GUI_FONT_NORMAL,
        ).pack(side="left")

        # 칼럼명 입력 (선택)
        tk.Label(option_frame, text="칼럼명:", font=GUI_FONT_NORMAL).pack(
            side="left", padx=(10, 0)
        )
        self.filename_column_entry = tk.Entry(
            option_frame, font=GUI_FONT_NORMAL, width=15
        )
        self.filename_column_entry.pack(side="left", padx=5)
        self.filename_column_entry.insert(0, "이름")

    def _create_button_ui(self):
        """버튼 UI 생성"""
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill="x", padx=15)

        button_frame = tk.Frame(frame)
        button_frame.pack()

        # 검증 버튼
        self.validate_btn = tk.Button(
            button_frame,
            text="✓ 검증",
            command=self.validate_files,
            bg="#2196F3",
            fg="white",
            font=GUI_FONT_BUTTON,
            width=12,
        )
        self.validate_btn.pack(side="left", padx=5)

        # 시작 버튼
        self.start_btn = tk.Button(
            button_frame,
            text="▶ 계약서 생성",
            command=self.start_process,
            bg=GUI_COLOR_PRIMARY,
            fg="white",
            font=GUI_FONT_BUTTON,
            width=12,
        )
        self.start_btn.pack(side="left", padx=5)

        # 취소 버튼
        self.cancel_btn = tk.Button(
            button_frame,
            text="✕ 취소",
            command=self.cancel_process,
            bg=GUI_COLOR_ERROR,
            fg="white",
            font=GUI_FONT_BUTTON,
            width=12,
            state="disabled",
        )
        self.cancel_btn.pack(side="left", padx=5)

    def _create_progress_ui(self):
        """진행률 UI 생성"""
        frame = tk.Frame(self.root)
        frame.pack(pady=5, padx=15, fill="x")

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            length=400,
        )
        self.progress_bar.pack(fill="x")

        self.progress_label = tk.Label(frame, text="준비됨", font=GUI_FONT_NORMAL)
        self.progress_label.pack(anchor="w", pady=(3, 0))

    def _create_log_ui(self):
        """로그 UI 생성"""
        frame = tk.Frame(self.root)
        frame.pack(pady=5, padx=15, fill="both", expand=True)

        # 제목
        title = tk.Label(
            frame,
            text="📝 로그",
            font=GUI_FONT_TITLE,
            fg=GUI_COLOR_PRIMARY,
        )
        title.pack(anchor="w")

        # 로그 영역
        self.log_area = scrolledtext.ScrolledText(
            frame,
            height=10,
            font=("Courier New", 9),
            bg="#f5f5f5",
            wrap="word",
        )
        self.log_area.pack(fill="both", expand=True, pady=(5, 0))

        # 초기 로그
        self._update_log()

    def _update_log(self):
        """로그 영역 업데이트"""
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.insert(tk.END, get_log_content())
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def select_excel(self):
        """Excel 파일 선택"""
        path = filedialog.askopenfilename(
            title="Excel 파일 선택",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")],
        )
        if path:
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(0, path)
            log_info(f"Excel 파일 선택: {path}")

    def select_template(self):
        """HWPX 템플릿 선택"""
        path = filedialog.askopenfilename(
            title="계약서 양식 선택",
            filetypes=[("HWPX files", "*.hwpx"), ("All files", "*.*")],
        )
        if path:
            self.template_entry.delete(0, tk.END)
            self.template_entry.insert(0, path)
            log_info(f"템플릿 선택: {path}")

    def select_output(self):
        """출력 폴더 선택"""
        path = filedialog.askdirectory(title="출력 폴더 선택")
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)
            log_info(f"출력 폴더 선택: {path}")

    def validate_files(self):
        """파일 검증"""
        excel = self.excel_entry.get().strip()
        template = self.template_entry.get().strip()
        output = self.output_entry.get().strip()

        # 입력 확인
        if not all([excel, template, output]):
            messagebox.showwarning("입력 누락", "모든 경로를 지정해주세요.")
            return

        # 검증 실행
        clear_logs()
        log_info("=" * 60)
        log_info("파일 검증 시작...")
        log_info("=" * 60)

        validator = Validator()
        result = validator.validate_batch_process(
            Path(excel),
            Path(template),
            check_data_samples=True,
        )

        log_info(validator.get_validation_summary(result))

        if result.is_valid:
            messagebox.showinfo(
                "검증 성공",
                f"검증이 완료되었습니다.\n\n"
                f"- Excel 칼럼: {len(result.info.get('excel_columns', []))}개\n"
                f"- 데이터 행: {result.info.get('excel_rows', 0)}개\n"
                f"- 템플릿 플레이스홀더: {len(result.info.get('hwpx_placeholders', []))}개",
            )
        else:
            messagebox.showerror(
                "검증 실패",
                f"검증에 실패했습니다.\n\n에러:\n" + "\n".join(result.errors),
            )

        self._update_log()

    def start_process(self):
        """배치 처리 시작"""
        excel = self.excel_entry.get().strip()
        template = self.template_entry.get().strip()
        output = self.output_entry.get().strip()

        # 입력 확인
        if not all([excel, template, output]):
            messagebox.showwarning("입력 누락", "모든 경로를 지정해주세요.")
            return

        # 파일 존재 확인
        if not Path(excel).exists():
            messagebox.showerror("오류", f"Excel 파일을 찾을 수 없습니다:\n{excel}")
            return

        if not Path(template).exists():
            messagebox.showerror("오류", f"템플릿 파일을 찾을 수 없습니다:\n{template}")
            return

        # UI 상태 변경
        self.is_processing = True
        self.start_btn.config(state="disabled")
        self.validate_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")

        # 로그 초기화
        clear_logs()

        # 별도 스레드에서 실행
        thread = threading.Thread(
            target=self._process_thread,
            args=(excel, template, output),
            daemon=True,
        )
        thread.start()

    def _process_thread(self, excel: str, template: str, output: str):
        """배치 처리 스레드"""
        try:
            # 배치 처리 실행
            processor = BatchProcessor(Path(excel), Path(template), Path(output))

            # 파일명 옵션
            use_row_number = self.filename_var.get() == "row_number"
            filename_column = (
                None if use_row_number else self.filename_column_entry.get()
            )

            # 진행률 콜백
            def progress_callback(current: int, total: int):
                percent = (current / total) * 100 if total > 0 else 0
                self.root.after(
                    0,
                    lambda: self._update_progress(current, total, percent),
                )

            # 배치 처리
            result = processor.process(
                filename_column=filename_column,
                use_row_number=use_row_number,
                progress_callback=progress_callback,
            )

            # 결과 표시
            self.root.after(0, lambda: self._show_result(result))

        except Exception as e:
            log_error(f"처리 중 오류: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "오류", f"처리 중 오류가 발생했습니다:\n{e}"
                ),
            )

        finally:
            # UI 상태 복원
            self.root.after(0, self._finish_process)

    def _update_progress(self, current: int, total: int, percent: float):
        """진행률 업데이트"""
        self.progress_var.set(percent)
        self.progress_label.config(text=f"진행: {current}/{total} ({percent:.1f}%)")
        self._update_log()

    def _show_result(self, result):
        """결과 표시"""
        self._update_log()

        if result.is_success:
            messagebox.showinfo(
                "완료",
                f"계약서 생성이 완료되었습니다.\n\n"
                f"- 생성된 파일: {result.generated_files}개\n"
                f"- 소요 시간: {result.execution_time_seconds:.2f}초\n\n"
                f"출력 폴더를 확인해주세요.",
            )
        else:
            messagebox.showerror(
                "실패",
                f"계약서 생성에 실패했습니다.\n\n"
                f"- 실패 행: {result.failed_at_row or '알 수 없음'}\n"
                f"- 오류: {result.error_message}\n"
                f"- 생성된 파일: {result.generated_files}개 (롤백됨)",
            )

    def _finish_process(self):
        """처리 완료"""
        self.is_processing = False
        self.start_btn.config(state="normal")
        self.validate_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    def cancel_process(self):
        """처리 취소 (구현 예정)"""
        messagebox.showinfo("알림", "현재 처리를 중단하는 기능은 준비 중입니다.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ContractGui(root)
    root.mainloop()
