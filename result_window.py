import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyperclip
from PIL import ImageGrab

from translator import translate
from dictionary_manager import add_word
from select_area import ScreenSelector
from ocr_engine import OCREngine


class ResultWindow:
    def __init__(self, text):
        self.original_text = text
        self.translated_text = ""

        # 記錄上一次剪貼簿內容，避免重複翻譯
        self.last_clipboard_text = ""

        # OCR 引擎
        self.ocr_engine = OCREngine()

        # ===== 建立主視窗 =====
        self.root = tk.Tk()
        self.root.title("OCR / 剪貼簿 翻譯工具")
        self.root.geometry("1050x720")
        self.root.attributes("-topmost", True)

        # ===== Tkinter 變數 =====
        self.mode_var = tk.StringVar(value="local")
        self.ocr_mode_var = tk.StringVar(value="easyocr")
        self.clipboard_monitor_var = tk.BooleanVar(value=True)

        # ===== 原文標題 =====
        original_label = tk.Label(
            self.root,
            text="OCR / 剪貼簿原文",
            font=("Microsoft JhengHei", 14, "bold")
        )
        original_label.pack(pady=(10, 0))

        # ===== 原文文字框 =====
        self.original_text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 14),
            height=10
        )
        self.original_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.original_text_area.insert(tk.END, self.original_text)

        # ===== 原文區右鍵選單 =====
        self.original_menu = tk.Menu(self.root, tearoff=0)
        self.original_menu.add_command(label="複製選取", command=self.copy_selected_original_text)
        self.original_menu.add_command(label="加入字典", command=self.add_to_dict)

        # 右鍵綁定（Windows 常用）
        self.original_text_area.bind("<Button-3>", self.show_original_menu)

        # Ctrl+C 綁定
        self.original_text_area.bind("<Control-c>", self.handle_ctrl_c_original)

        # ===== 設定列 =====
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=5)

        mode_label = tk.Label(mode_frame, text="翻譯模式：")
        mode_label.pack(side=tk.LEFT)

        local_radio = tk.Radiobutton(
            mode_frame,
            text="本地翻譯",
            variable=self.mode_var,
            value="local"
        )
        local_radio.pack(side=tk.LEFT, padx=5)

        gpt_radio = tk.Radiobutton(
            mode_frame,
            text="GPT翻譯",
            variable=self.mode_var,
            value="gpt"
        )
        gpt_radio.pack(side=tk.LEFT, padx=5)

        ocr_mode_label = tk.Label(mode_frame, text=" OCR模式：")
        ocr_mode_label.pack(side=tk.LEFT)

        easyocr_radio = tk.Radiobutton(
            mode_frame,
            text="EasyOCR",
            variable=self.ocr_mode_var,
            value="easyocr"
        )
        easyocr_radio.pack(side=tk.LEFT, padx=5)

        mangaocr_radio = tk.Radiobutton(
            mode_frame,
            text="Manga-OCR",
            variable=self.ocr_mode_var,
            value="mangaocr"
        )
        mangaocr_radio.pack(side=tk.LEFT, padx=5)

        clipboard_check = tk.Checkbutton(
            mode_frame,
            text="自動監聽剪貼簿",
            variable=self.clipboard_monitor_var
        )
        clipboard_check.pack(side=tk.LEFT, padx=15)

        # ===== 按鈕區 =====
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=8)

        translate_button = tk.Button(
            button_frame,
            text="翻譯成中文",
            command=self.do_translate
        )
        translate_button.pack(side=tk.LEFT, padx=8)

        add_dict_button = tk.Button(
            button_frame,
            text="加入字典",
            command=self.add_to_dict
        )
        add_dict_button.pack(side=tk.LEFT, padx=8)

        clipboard_button = tk.Button(
            button_frame,
            text="手動讀取剪貼簿",
            command=self.load_clipboard_text
        )
        clipboard_button.pack(side=tk.LEFT, padx=8)

        ocr_button = tk.Button(
            button_frame,
            text="OCR選區",
            command=self.run_ocr
        )
        ocr_button.pack(side=tk.LEFT, padx=8)

        copy_original_button = tk.Button(
            button_frame,
            text="複製原文",
            command=self.copy_original_text
        )
        copy_original_button.pack(side=tk.LEFT, padx=8)

        copy_translated_button = tk.Button(
            button_frame,
            text="複製翻譯",
            command=self.copy_translated_text
        )
        copy_translated_button.pack(side=tk.LEFT, padx=8)

        close_button = tk.Button(
            button_frame,
            text="關閉",
            command=self.root.destroy
        )
        close_button.pack(side=tk.LEFT, padx=8)

        # ===== 狀態列 =====
        self.status_label = tk.Label(
            self.root,
            text="狀態：等待剪貼簿或 OCR 輸入",
            anchor="w",
            fg="blue"
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=(0, 5))

        # ===== 翻譯標題 =====
        translated_label = tk.Label(
            self.root,
            text="中文翻譯",
            font=("Microsoft JhengHei", 14, "bold")
        )
        translated_label.pack(pady=(10, 0))

        # ===== 翻譯文字框 =====
        self.translated_text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 14),
            height=10
        )
        self.translated_text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== 翻譯區右鍵選單 =====
        self.translated_menu = tk.Menu(self.root, tearoff=0)
        self.translated_menu.add_command(label="複製選取", command=self.copy_selected_translated_text)

        # 右鍵綁定
        self.translated_text_area.bind("<Button-3>", self.show_translated_menu)

        # Ctrl+C 綁定
        self.translated_text_area.bind("<Control-c>", self.handle_ctrl_c_translated)

        # 啟動剪貼簿監聽
        self.start_clipboard_monitor()

    def set_status(self, text):
        self.status_label.config(text=f"狀態：{text}")

    def do_translate(self):
        current_text = self.original_text_area.get("1.0", tk.END).strip()

        if not current_text:
            messagebox.showwarning("提示", "目前沒有可翻譯的文字")
            return

        mode = self.mode_var.get()
        self.set_status(f"正在翻譯（{mode}）...")
        self.root.update()

        self.translated_text = translate(current_text, mode)

        self.translated_text_area.delete("1.0", tk.END)
        self.translated_text_area.insert(tk.END, self.translated_text)

        self.set_status("翻譯完成")

    def add_to_dict(self):
        try:
            selected_text = self.original_text_area.selection_get()
        except:
            selected_text = ""

        if not selected_text.strip():
            messagebox.showwarning("提示", "請先在原文區選取文字")
            return

        result = add_word(selected_text)
        messagebox.showinfo("字典", result)

    def load_clipboard_text(self):
        try:
            clipboard_text = pyperclip.paste()
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取剪貼簿失敗：{e}")
            return

        if not clipboard_text.strip():
            messagebox.showwarning("提示", "剪貼簿目前沒有文字")
            return

        self.last_clipboard_text = clipboard_text
        self.update_original_text(clipboard_text)
        self.set_status("已手動讀取剪貼簿")
        self.do_translate()

    def run_ocr(self):
        selector = ScreenSelector()
        bbox = selector.get_area()

        if bbox is None:
            self.set_status("取消 OCR 選區")
            return

        try:
            img = ImageGrab.grab(bbox=bbox)
            img.save("test.png")

            ocr_mode = self.ocr_mode_var.get()
            final_text = self.ocr_engine.read("test.png", ocr_mode)

            self.update_original_text(final_text)
            self.set_status(f"OCR 完成（{ocr_mode}）")
            self.do_translate()

        except Exception as e:
            messagebox.showerror("錯誤", f"OCR 失敗：{e}")

    def update_original_text(self, text):
        self.original_text_area.delete("1.0", tk.END)
        self.original_text_area.insert(tk.END, text)

    def check_clipboard(self):
        if self.clipboard_monitor_var.get():
            try:
                clipboard_text = pyperclip.paste()
            except:
                clipboard_text = ""

            if clipboard_text.strip() and clipboard_text != self.last_clipboard_text:
                self.last_clipboard_text = clipboard_text
                self.update_original_text(clipboard_text)
                self.set_status("偵測到新的剪貼簿文字")
                self.do_translate()

        self.root.after(800, self.check_clipboard)

    def start_clipboard_monitor(self):
        self.root.after(800, self.check_clipboard)

    def copy_original_text(self):
        current_text = self.original_text_area.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(current_text)
        self.root.update()
        self.set_status("已複製原文")

    def copy_translated_text(self):
        current_text = self.translated_text_area.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(current_text)
        self.root.update()
        self.set_status("已複製翻譯")

    def show_original_menu(self, event):
        try:
            self.original_text_area.focus_set()
            self.original_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.original_menu.grab_release()

    def show_translated_menu(self, event):
        try:
            self.translated_text_area.focus_set()
            self.translated_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.translated_menu.grab_release()

    def copy_selected_original_text(self):
        try:
            selected_text = self.original_text_area.selection_get()

            if selected_text.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.root.update()
                self.set_status("已複製原文選取內容")
        except:
            messagebox.showwarning("提示", "請先在原文區選取文字")

    def copy_selected_translated_text(self):
        try:
            selected_text = self.translated_text_area.selection_get()

            if selected_text.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.root.update()
                self.set_status("已複製翻譯選取內容")
        except:
            messagebox.showwarning("提示", "請先在翻譯區選取文字")

    def handle_ctrl_c_original(self, event=None):
        try:
            self.copy_selected_original_text()
        except:
            pass
        return "break"

    def handle_ctrl_c_translated(self, event=None):
        try:
            self.copy_selected_translated_text()
        except:
            pass
        return "break"

    def show(self):
        self.root.mainloop()