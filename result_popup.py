import tkinter as tk
from tkinter import messagebox, ttk
import threading

from translator import translate
from dictionary_manager import add_word, add_word_fast, enrich_word_data_async


class ResultPopup:
    def __init__(self, parent, source_text):
        self.parent = parent
        self.source_text = source_text.strip()
        self.translated_text = ""
        self.translate_job_id = 0

        self.window = tk.Toplevel(self.parent)
        self.window.title("翻譯結果")
        self.window.geometry("980x520+360+140")
        self.window.minsize(720, 360)
        self.window.configure(bg="#F5EAD9")
        self.window.attributes("-topmost", True)

        self.build_ui()
        self.update_content(self.source_text)

    def build_ui(self):
        self.main_frame = tk.Frame(self.window, bg="#F5EAD9")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.top_bar = tk.Frame(self.main_frame, bg="#E7D6BE")
        self.top_bar.pack(fill=tk.X, pady=(0, 10))

        self.add_dict_button = tk.Button(
            self.top_bar,
            text="加入字典",
            command=self.add_current_to_dict,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2"
        )
        self.add_dict_button.pack(side=tk.LEFT, padx=8, pady=8)

        self.copy_source_button = tk.Button(
            self.top_bar,
            text="複製原文",
            command=self.copy_source,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2"
        )
        self.copy_source_button.pack(side=tk.LEFT, padx=8, pady=8)

        self.copy_translated_button = tk.Button(
            self.top_bar,
            text="複製翻譯",
            command=self.copy_translated,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2"
        )
        self.copy_translated_button.pack(side=tk.LEFT, padx=8, pady=8)

        self.hide_toolbar_button = tk.Button(
            self.top_bar,
            text="隱藏工具列",
            command=self.hide_toolbar,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2"
        )
        self.hide_toolbar_button.pack(side=tk.LEFT, padx=8, pady=8)

        spacer = tk.Frame(self.top_bar, bg="#E7D6BE")
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.close_button = tk.Button(
            self.top_bar,
            text="關閉",
            command=self.window.destroy,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=7,
            cursor="hand2"
        )
        self.close_button.pack(side=tk.RIGHT, padx=8, pady=8)

        self.content_paned = ttk.Panedwindow(self.main_frame, orient=tk.HORIZONTAL)
        self.content_paned.pack(fill=tk.BOTH, expand=True)

        self.left_panel = tk.Frame(self.content_paned, bg="#E7D6BE", bd=0)
        self.content_paned.add(self.left_panel, weight=3)

        self.source_title = tk.Label(
            self.left_panel,
            text="原文",
            font=("Microsoft JhengHei", 13, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            anchor="w",
            padx=12,
            pady=10
        )
        self.source_title.pack(fill=tk.X)

        self.source_textbox = tk.Text(
            self.left_panel,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 12),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            padx=12,
            pady=12
        )
        self.source_textbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.right_panel = tk.Frame(self.content_paned, bg="#E7D6BE", bd=0)
        self.content_paned.add(self.right_panel, weight=2)

        self.translated_title = tk.Label(
            self.right_panel,
            text="翻譯",
            font=("Microsoft JhengHei", 13, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            anchor="w",
            padx=12,
            pady=10
        )
        self.translated_title.pack(fill=tk.X)

        self.translated_textbox = tk.Text(
            self.right_panel,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 12),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            padx=12,
            pady=12
        )
        self.translated_textbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.status_label = tk.Label(
            self.main_frame,
            text="狀態：準備完成",
            font=("Microsoft JhengHei", 10),
            bg="#E7D6BE",
            fg="#6A4A35",
            anchor="w",
            padx=10,
            pady=8
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))

    def update_content(self, new_source_text):
        self.source_text = new_source_text.strip()
        self.translated_text = ""

        self.source_textbox.delete("1.0", tk.END)
        self.translated_textbox.delete("1.0", tk.END)

        self.source_textbox.insert("1.0", self.source_text)

        if not self.source_text:
            self.translated_textbox.insert("1.0", "沒有可翻譯文字")
            self.set_status("沒有可翻譯文字")
            return

        self.translated_textbox.insert("1.0", "翻譯中，請稍候...")
        self.start_translate_async()

    def start_translate_async(self):
        self.translate_job_id += 1
        current_job_id = self.translate_job_id

        self.set_status("正在翻譯...")

        thread = threading.Thread(
            target=self._translate_worker,
            args=(self.source_text, current_job_id),
            daemon=True
        )
        thread.start()

    def _translate_worker(self, text, job_id):
        try:
            result = translate(text, "local")
        except Exception as e:
            result = f"翻譯失敗：{e}"

        self.window.after(0, lambda: self._apply_translation_result(job_id, result))

    def _apply_translation_result(self, job_id, result):
        if not self.window.winfo_exists():
            return

        if job_id != self.translate_job_id:
            return

        self.translated_text = result if result else "翻譯結果為空"

        self.translated_textbox.delete("1.0", tk.END)
        self.translated_textbox.insert("1.0", self.translated_text)
        self.set_status("翻譯完成")

    def add_current_to_dict(self):
        try:
            result = add_word_fast(self.source_text)

            if result.startswith("已加入字典"):
                enrich_word_data_async(self.source_text)
                messagebox.showinfo(
                    "字典",
                    f"{result}\n背景正在補完讀音 / 中文 / 英文 / 詞性",
                    parent=self.window
                )
                self.set_status("已加入字典，背景補資料中")
            else:
                messagebox.showinfo("字典", result, parent=self.window)
                self.set_status(f"字典：{result}")

        except Exception as e:
            messagebox.showerror("錯誤", f"加入字典失敗：{e}", parent=self.window)
            self.set_status("加入字典失敗")

    def copy_source(self):
        text = self.source_textbox.get("1.0", tk.END).strip()
        if not text:
            return

        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        self.window.update()
        self.set_status("已複製原文")

    def copy_translated(self):
        text = self.translated_textbox.get("1.0", tk.END).strip()
        if not text:
            return

        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        self.window.update()
        self.set_status("已複製翻譯")

    def hide_toolbar(self):
        try:
            self.parent.withdraw()
            self.set_status("已隱藏工具列")
        except Exception:
            self.set_status("隱藏工具列失敗")

    def set_status(self, text):
        self.status_label.config(text=f"狀態：{text}")

    def show(self):
        self.window.lift()
        self.window.focus_force()

    def ask_dictionary_language(self, selected_text):
        dialog = tk.Toplevel(self.window)
        dialog.title("選擇字典")
        dialog.geometry("320x160")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.configure(bg="#F5EAD9")

        label = tk.Label(
            dialog,
            text=f"「{selected_text}」只有漢字\n請選擇要加入哪個字典：",
            font=("Microsoft JhengHei", 11),
            bg="#F5EAD9",
            fg="#4A2F21",
            justify="center"
        )
        label.pack(pady=(20, 16))

        button_frame = tk.Frame(dialog, bg="#F5EAD9")
        button_frame.pack()

        ja_btn = tk.Button(
            button_frame,
            text="日文字典",
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            command=lambda: self.add_word_with_language(selected_text, "ja", dialog)
        )
        ja_btn.pack(side=tk.LEFT, padx=8)

        zh_btn = tk.Button(
            button_frame,
            text="中文字典",
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            command=lambda: self.add_word_with_language(selected_text, "zh", dialog)
        )
        zh_btn.pack(side=tk.LEFT, padx=8)

def add_word_with_language(self, selected_text, language, dialog):
    result = add_word_fast(selected_text, forced_language=language)
    dialog.destroy()
    messagebox.showinfo("字典", result, parent=self.window)
    self.set_status(f"字典：{result}")

    enrich_word_data_async(selected_text)