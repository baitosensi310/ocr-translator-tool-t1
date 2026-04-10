import tkinter as tk
import ctypes
import pyperclip
from PIL import ImageGrab

from app_settings import load_openai_api_key, save_openai_api_key, load_settings, save_settings
from ocr_engine import OCREngine
from select_area import ScreenSelector
from result_popup import ResultPopup
from dictionary_home import DictionaryHome


class ToolbarWindow:
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("Toolbar")
        self.root.geometry("320x58+260+80")
        self.root.minsize(260, 58)
        self.root.resizable(True, False)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.90)
        self.root.configure(bg="#3A2A1F")

        self.offset_x = 0
        self.offset_y = 0

        self.ocr_engine = OCREngine()
        self.settings = load_settings()
        self.dictionary_home = None
        self.result_popup = None
        self.clipboard_monitor_enabled = True
        self.clipboard_error_count = 0
        self.last_clipboard_sequence = self.get_clipboard_sequence()

        try:
            self.last_clipboard_text = self.read_clipboard_text()
        except Exception:
            self.last_clipboard_text = ""

        self.build_ui()
        self.bind_drag()
        self.monitor_clipboard()

    def build_ui(self):
        container = tk.Frame(self.root, bg="#3A2A1F")
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.create_button(container, "OCR", self.run_ocr).pack(side=tk.LEFT, padx=4)
        self.create_button(container, "字典", self.open_dictionary).pack(side=tk.LEFT, padx=4)

        self.clipboard_toggle_button = self.create_button(
            container,
            "剪貼簿監聽：開",
            self.toggle_clipboard_monitor
        )
        self.clipboard_toggle_button.pack(side=tk.LEFT, padx=4)

        self.create_button(container, "設定", self.open_settings).pack(side=tk.LEFT, padx=4)

        spacer = tk.Frame(container, bg="#3A2A1F")
        spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.create_button(container, "X", self.root.destroy).pack(side=tk.RIGHT, padx=4)

    def create_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2"
        )

    def bind_drag(self):
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.offset_x
        y = self.root.winfo_y() + event.y - self.offset_y
        self.root.geometry(f"+{x}+{y}")

    def run_ocr(self):
        selector = ScreenSelector()
        bbox = selector.get_area()

        if not bbox:
            return

        try:
            img = ImageGrab.grab(bbox=bbox)
            img.save("temp_ocr.png")

            if self.settings.get("gpt_ocr_enabled", False):
                result = self.ocr_engine.read_gpt_ocr("temp_ocr.png")
                source_text = result.get("source_text", "").strip()
                translated_text = result.get("translated_text", "").strip()

                if source_text or translated_text:
                    self.open_result_popup(source_text or "GPT OCR 沒有辨識到原文", translated_text)
                return

            text = self.ocr_engine.read("temp_ocr.png", "easyocr")

            if text.strip():
                self.open_result_popup(text)
        except Exception as e:
            print("OCR失敗：", e)

    def open_result_popup(self, source_text, initial_translation=None):
        if self.result_popup is not None:
            try:
                if self.result_popup.window.winfo_exists():
                    self.result_popup.translation_mode = self.settings.get("translation_mode", "local")
                    self.result_popup.update_content(source_text, initial_translation)
                    self.result_popup.window.lift()
                    self.result_popup.window.focus_force()
                    return
            except Exception:
                self.result_popup = None

        self.result_popup = ResultPopup(
            self.root,
            source_text,
            initial_translation=initial_translation,
            translation_mode=self.settings.get("translation_mode", "local")
        )
        self.result_popup.show()

    def read_clipboard_text(self):
        try:
            return pyperclip.paste()
        except Exception:
            pass

        try:
            return self.root.clipboard_get()
        except Exception:
            return ""

    def get_clipboard_sequence(self):
        try:
            return ctypes.windll.user32.GetClipboardSequenceNumber()
        except Exception:
            return 0

    def monitor_clipboard(self):
        if self.clipboard_monitor_enabled:
            text = self.read_clipboard_text()
            sequence = self.get_clipboard_sequence()

            if text:
                self.clipboard_error_count = 0
                clipboard_changed = (
                    text != self.last_clipboard_text
                    or (sequence and sequence != self.last_clipboard_sequence)
                )

                if text.strip() and clipboard_changed:
                    self.last_clipboard_text = text
                    self.last_clipboard_sequence = sequence
                    self.open_result_popup(text)
            else:
                self.clipboard_error_count += 1

        self.root.after(400, self.monitor_clipboard)

    def open_dictionary(self):
        self.sync_clipboard_before_dictionary()

        if self.dictionary_home is not None:
            try:
                if self.dictionary_home.window.winfo_exists():
                    self.dictionary_home.refresh_external_context()
                    self.dictionary_home.window.lift()
                    self.dictionary_home.window.focus_force()
                    return
            except Exception:
                self.dictionary_home = None

        self.dictionary_home = DictionaryHome(self)

    def sync_clipboard_before_dictionary(self):
        text = self.read_clipboard_text()
        if text.strip():
            self.last_clipboard_text = text
            self.last_clipboard_sequence = self.get_clipboard_sequence()

    def get_current_translation_context(self):
        source_text = ""
        translated_text = ""

        if self.result_popup is not None:
            try:
                if self.result_popup.window.winfo_exists():
                    if hasattr(self.result_popup, "source_textbox"):
                        source_text = self.result_popup.source_textbox.get("1.0", tk.END).strip()
                    else:
                        source_text = str(getattr(self.result_popup, "source_text", "")).strip()

                    if hasattr(self.result_popup, "translated_textbox"):
                        translated_text = self.result_popup.translated_textbox.get("1.0", tk.END).strip()
                    else:
                        translated_text = str(getattr(self.result_popup, "translated_text", "")).strip()
            except Exception:
                pass

        return {
            "source_text": source_text,
            "translated_text": translated_text
        }

    def open_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("設定")
        dialog.geometry("560x500+320+120")
        dialog.minsize(520, 470)
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.configure(bg="#F5EAD9")
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)

        content = tk.Frame(dialog, bg="#F5EAD9")
        content.grid(row=0, column=0, sticky="nsew", padx=18, pady=(18, 8))
        content.grid_columnconfigure(0, weight=1)

        translation_mode_var = tk.StringVar(value=self.settings.get("translation_mode", "local"))
        gpt_ocr_var = tk.BooleanVar(value=self.settings.get("gpt_ocr_enabled", False))
        api_key_var = tk.StringVar(value=load_openai_api_key())

        title = tk.Label(
            content,
            text="設定",
            font=("Microsoft JhengHei", 16, "bold"),
            bg="#F5EAD9",
            fg="#4A2F21"
        )
        title.pack(fill=tk.X, pady=(0, 12))

        translation_frame = tk.LabelFrame(
            content,
            text="翻譯 API",
            font=("Microsoft JhengHei", 11, "bold"),
            bg="#F5EAD9",
            fg="#4A2F21",
            padx=12,
            pady=10
        )
        translation_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Radiobutton(
            translation_frame,
            text="Google 翻譯",
            variable=translation_mode_var,
            value="local",
            bg="#F5EAD9",
            fg="#4A2F21",
            selectcolor="#FBF6EE",
            font=("Microsoft JhengHei", 10)
        ).pack(anchor="w")

        tk.Radiobutton(
            translation_frame,
            text="GPT 翻譯（需要 OPENAI_API_KEY）",
            variable=translation_mode_var,
            value="gpt",
            bg="#F5EAD9",
            fg="#4A2F21",
            selectcolor="#FBF6EE",
            font=("Microsoft JhengHei", 10)
        ).pack(anchor="w")

        ocr_frame = tk.LabelFrame(
            content,
            text="OCR",
            font=("Microsoft JhengHei", 11, "bold"),
            bg="#F5EAD9",
            fg="#4A2F21",
            padx=12,
            pady=10
        )
        ocr_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Checkbutton(
            ocr_frame,
            text="同意使用 GPT OCR：截圖會送到 OpenAI 做原文辨識與翻譯",
            variable=gpt_ocr_var,
            bg="#F5EAD9",
            fg="#4A2F21",
            selectcolor="#FBF6EE",
            font=("Microsoft JhengHei", 10),
            anchor="w",
            justify="left"
        ).pack(anchor="w")

        account_frame = tk.LabelFrame(
            content,
            text="OpenAI 登入",
            font=("Microsoft JhengHei", 11, "bold"),
            bg="#F5EAD9",
            fg="#4A2F21",
            padx=12,
            pady=10
        )
        account_frame.pack(fill=tk.X, pady=(0, 0))

        key_entry = tk.Entry(
            account_frame,
            textvariable=api_key_var,
            show="*",
            font=("Microsoft JhengHei", 10),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="flat",
            bd=0
        )
        key_entry.pack(fill=tk.X, ipady=6)

        key_hint = tk.Label(
            account_frame,
            text="可貼上 OpenAI API Key；若系統已有 OPENAI_API_KEY，會優先使用環境變數。",
            font=("Microsoft JhengHei", 9),
            bg="#F5EAD9",
            fg="#6A4A35",
            anchor="w",
            justify="left"
        )
        key_hint.pack(fill=tk.X, pady=(6, 0))

        button_row = tk.Frame(dialog, bg="#F5EAD9")
        button_row.grid(row=1, column=0, sticky="ew")

        button_inner = tk.Frame(button_row, bg="#F5EAD9")
        button_inner.pack(fill=tk.X, padx=18, pady=(4, 18))

        def apply_settings():
            self.settings["translation_mode"] = translation_mode_var.get()
            self.settings["gpt_ocr_enabled"] = bool(gpt_ocr_var.get())
            self.settings = save_settings(self.settings)
            save_openai_api_key(api_key_var.get())
            dialog.destroy()

        def clear_api_key():
            api_key_var.set("")
            save_openai_api_key("")

        self.create_button(button_inner, "儲存", apply_settings).pack(side=tk.RIGHT, padx=(8, 0))
        self.create_button(button_inner, "取消", dialog.destroy).pack(side=tk.RIGHT)
        self.create_button(button_inner, "清除 Key", clear_api_key).pack(side=tk.LEFT)

    def show(self):
        self.root.mainloop()

    def toggle_clipboard_monitor(self):
        self.clipboard_monitor_enabled = not self.clipboard_monitor_enabled

        if self.clipboard_monitor_enabled:
            self.clipboard_toggle_button.config(text="剪貼簿監聽：開")
            print("剪貼簿監聽已開啟")
        else:
            self.clipboard_toggle_button.config(text="剪貼簿監聽：關")
            print("剪貼簿監聽已關閉")
