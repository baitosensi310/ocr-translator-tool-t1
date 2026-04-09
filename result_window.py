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

        try:
            self.last_clipboard_text = pyperclip.paste()
        except:
            self.last_clipboard_text = ""

        self.ocr_engine = OCREngine()

        # ========= 配色：古書店 / 舊書頁風 =========
        self.COLOR_BG_MAIN = "#F5EAD9"       # 主背景
        self.COLOR_BG_PANEL = "#E7D6BE"      # 區塊背景
        self.COLOR_BG_TEXT = "#FBF6EE"       # 文字框背景
        self.COLOR_TITLE = "#4A2F21"         # 深棕標題
        self.COLOR_TEXT = "#3A2A1F"          # 內文字色
        self.COLOR_BORDER = "#8B6A4E"        # 邊框色
        self.COLOR_BUTTON = "#8B5E3C"        # 按鈕色
        self.COLOR_BUTTON_HOVER = "#A06A43"  # 按鈕 hover
        self.COLOR_BUTTON_TEXT = "#FFF8EE"   # 按鈕文字
        self.COLOR_ACCENT = "#C89B3C"        # 金棕強調色
        self.COLOR_STATUS = "#6A4A35"        # 狀態列文字

        # ========= 主視窗 =========
        self.root = tk.Tk()
        self.root.title("古書翻譯室")
        self.root.geometry("1280x760")
        self.root.minsize(1100, 650)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.COLOR_BG_MAIN)

        # ========= 變數 =========
        self.mode_var = tk.StringVar(value="local")
        self.ocr_mode_var = tk.StringVar(value="easyocr")
        self.clipboard_monitor_var = tk.BooleanVar(value=True)
        self.auto_translate_var = tk.BooleanVar(value=True)

        # ========= 最外層 =========
        self.main_container = tk.Frame(self.root, bg=self.COLOR_BG_MAIN)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        # ========= 標題區 =========
        self.build_header()

        # ========= 工具列 =========
        self.build_toolbar()

        # ========= 內容區 =========
        self.build_content_area()

        # ========= 設定列 =========
        self.build_setting_bar()

        # ========= 狀態列 =========
        self.build_status_bar()

        # ========= 初始化文字 =========
        if self.original_text.strip():
            self.original_text_area.insert(tk.END, self.original_text)

        # ========= 右鍵選單 =========
        self.build_menus()

        # ========= 事件綁定 =========
        self.bind_events()

        # ========= 開始監聽剪貼簿 =========
        self.start_clipboard_monitor()

    # =========================================================
    # UI 建立區
    # =========================================================
    def build_header(self):
        header_frame = tk.Frame(
            self.main_container,
            bg=self.COLOR_BG_PANEL,
            bd=2,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        header_frame.pack(fill=tk.X, pady=(0, 12))

        title_label = tk.Label(
            header_frame,
            text="古書翻譯室",
            font=("Microsoft JhengHei", 22, "bold"),
            fg=self.COLOR_TITLE,
            bg=self.COLOR_BG_PANEL,
            pady=10
        )
        title_label.pack()

        subtitle_label = tk.Label(
            header_frame,
            text="OCR・剪貼簿翻譯・單字收藏",
            font=("Microsoft JhengHei", 10),
            fg=self.COLOR_STATUS,
            bg=self.COLOR_BG_PANEL,
            pady=2
        )
        subtitle_label.pack()

    def build_toolbar(self):
        self.toolbar_frame = tk.Frame(
            self.main_container,
            bg=self.COLOR_BG_PANEL,
            bd=2,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 12), ipady=8)

        self.ocr_button = self.create_action_button(
            self.toolbar_frame, "OCR選區", self.run_ocr
        )
        self.ocr_button.pack(side=tk.LEFT, padx=(12, 8), pady=6)

        self.clipboard_button = self.create_action_button(
            self.toolbar_frame, "讀取剪貼簿", self.load_clipboard_text
        )
        self.clipboard_button.pack(side=tk.LEFT, padx=8, pady=6)

        self.translate_button = self.create_action_button(
            self.toolbar_frame, "翻譯成中文", self.do_translate
        )
        self.translate_button.pack(side=tk.LEFT, padx=8, pady=6)

        self.add_dict_button = self.create_action_button(
            self.toolbar_frame, "加入字典", self.add_to_dict
        )
        self.add_dict_button.pack(side=tk.LEFT, padx=8, pady=6)

        self.copy_original_button = self.create_action_button(
            self.toolbar_frame, "複製原文", self.copy_original_text
        )
        self.copy_original_button.pack(side=tk.LEFT, padx=8, pady=6)

        self.copy_translated_button = self.create_action_button(
            self.toolbar_frame, "複製翻譯", self.copy_translated_text
        )
        self.copy_translated_button.pack(side=tk.LEFT, padx=8, pady=6)

        spacer = tk.Frame(self.toolbar_frame, bg=self.COLOR_BG_PANEL)
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.close_button = self.create_action_button(
            self.toolbar_frame, "關閉", self.root.destroy
        )
        self.close_button.pack(side=tk.RIGHT, padx=(8, 12), pady=6)

    def build_content_area(self):
        self.content_frame = tk.Frame(self.main_container, bg=self.COLOR_BG_MAIN)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.left_panel = tk.Frame(
            self.content_frame,
            bg=self.COLOR_BG_PANEL,
            bd=2,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.right_panel = tk.Frame(
            self.content_frame,
            bg=self.COLOR_BG_PANEL,
            bd=2,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        # 左：原文
        left_title = tk.Label(
            self.left_panel,
            text="原文",
            font=("Microsoft JhengHei", 15, "bold"),
            fg=self.COLOR_TITLE,
            bg=self.COLOR_BG_PANEL,
            anchor="w",
            padx=14,
            pady=10
        )
        left_title.pack(fill=tk.X)

        self.original_text_area = scrolledtext.ScrolledText(
            self.left_panel,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 14),
            bg=self.COLOR_BG_TEXT,
            fg=self.COLOR_TEXT,
            insertbackground=self.COLOR_TITLE,
            relief="flat",
            bd=0,
            padx=14,
            pady=12
        )
        self.original_text_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # 右：翻譯
        right_title = tk.Label(
            self.right_panel,
            text="中文翻譯",
            font=("Microsoft JhengHei", 15, "bold"),
            fg=self.COLOR_TITLE,
            bg=self.COLOR_BG_PANEL,
            anchor="w",
            padx=14,
            pady=10
        )
        right_title.pack(fill=tk.X)

        self.translated_text_area = scrolledtext.ScrolledText(
            self.right_panel,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 14),
            bg=self.COLOR_BG_TEXT,
            fg=self.COLOR_TEXT,
            insertbackground=self.COLOR_TITLE,
            relief="flat",
            bd=0,
            padx=14,
            pady=12
        )
        self.translated_text_area.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    def build_setting_bar(self):
        self.setting_frame = tk.Frame(
            self.main_container,
            bg=self.COLOR_BG_PANEL,
            bd=2,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        self.setting_frame.pack(fill=tk.X, pady=(0, 12), ipady=6)

        # 左側：翻譯模式
        mode_title = tk.Label(
            self.setting_frame,
            text="翻譯模式",
            font=("Microsoft JhengHei", 10, "bold"),
            fg=self.COLOR_TITLE,
            bg=self.COLOR_BG_PANEL
        )
        mode_title.pack(side=tk.LEFT, padx=(14, 6))

        local_radio = self.create_radio(
            self.setting_frame, "本地翻譯", self.mode_var, "local"
        )
        local_radio.pack(side=tk.LEFT, padx=4)

        gpt_radio = self.create_radio(
            self.setting_frame, "GPT翻譯", self.mode_var, "gpt"
        )
        gpt_radio.pack(side=tk.LEFT, padx=4)

        # 中間：OCR 模式
        ocr_title = tk.Label(
            self.setting_frame,
            text="OCR模式",
            font=("Microsoft JhengHei", 10, "bold"),
            fg=self.COLOR_TITLE,
            bg=self.COLOR_BG_PANEL
        )
        ocr_title.pack(side=tk.LEFT, padx=(20, 6))

        easyocr_radio = self.create_radio(
            self.setting_frame, "EasyOCR", self.ocr_mode_var, "easyocr"
        )
        easyocr_radio.pack(side=tk.LEFT, padx=4)

        mangaocr_radio = self.create_radio(
            self.setting_frame, "Manga-OCR", self.ocr_mode_var, "mangaocr"
        )
        mangaocr_radio.pack(side=tk.LEFT, padx=4)

        # 右側：監聽與自動翻譯
        spacer = tk.Frame(self.setting_frame, bg=self.COLOR_BG_PANEL)
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        clipboard_check = self.create_checkbutton(
            self.setting_frame, "監聽 Ctrl+C", self.clipboard_monitor_var
        )
        clipboard_check.pack(side=tk.LEFT, padx=8)

        auto_translate_check = self.create_checkbutton(
            self.setting_frame, "自動翻譯", self.auto_translate_var
        )
        auto_translate_check.pack(side=tk.LEFT, padx=(4, 14))

    def build_status_bar(self):
        self.status_frame = tk.Frame(
            self.main_container,
            bg=self.COLOR_BG_PANEL,
            bd=2,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        self.status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            self.status_frame,
            text="狀態：等待 OCR 或 Ctrl+C 文字輸入",
            font=("Microsoft JhengHei", 10),
            fg=self.COLOR_STATUS,
            bg=self.COLOR_BG_PANEL,
            anchor="w",
            padx=12,
            pady=8
        )
        self.status_label.pack(fill=tk.X)

    def build_menus(self):
        self.original_menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=self.COLOR_BG_TEXT,
            fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BUTTON_HOVER,
            activeforeground=self.COLOR_BUTTON_TEXT
        )
        self.original_menu.add_command(label="複製選取", command=self.copy_selected_original_text)
        self.original_menu.add_command(label="加入字典", command=self.add_to_dict)

        self.translated_menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=self.COLOR_BG_TEXT,
            fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BUTTON_HOVER,
            activeforeground=self.COLOR_BUTTON_TEXT
        )
        self.translated_menu.add_command(label="複製選取", command=self.copy_selected_translated_text)

    def bind_events(self):
        self.original_text_area.bind("<Button-3>", self.show_original_menu)
        self.translated_text_area.bind("<Button-3>", self.show_translated_menu)

        self.original_text_area.bind("<Control-c>", self.handle_ctrl_c_original)
        self.translated_text_area.bind("<Control-c>", self.handle_ctrl_c_translated)

    # =========================================================
    # 小元件樣式
    # =========================================================
    def create_action_button(self, parent, text, command):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Microsoft JhengHei", 10, "bold"),
            bg=self.COLOR_BUTTON,
            fg=self.COLOR_BUTTON_TEXT,
            activebackground=self.COLOR_BUTTON_HOVER,
            activeforeground=self.COLOR_BUTTON_TEXT,
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2"
        )
        button.bind("<Enter>", lambda e, b=button: b.config(bg=self.COLOR_BUTTON_HOVER))
        button.bind("<Leave>", lambda e, b=button: b.config(bg=self.COLOR_BUTTON))
        return button

    def create_radio(self, parent, text, variable, value):
        return tk.Radiobutton(
            parent,
            text=text,
            variable=variable,
            value=value,
            font=("Microsoft JhengHei", 10),
            bg=self.COLOR_BG_PANEL,
            fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BG_PANEL,
            activeforeground=self.COLOR_TITLE,
            selectcolor=self.COLOR_BG_TEXT
        )

    def create_checkbutton(self, parent, text, variable):
        return tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            font=("Microsoft JhengHei", 10),
            bg=self.COLOR_BG_PANEL,
            fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BG_PANEL,
            activeforeground=self.COLOR_TITLE,
            selectcolor=self.COLOR_BG_TEXT
        )

    # =========================================================
    # 功能區
    # =========================================================
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

        try:
            self.translated_text = translate(current_text, mode)
            self.translated_text_area.delete("1.0", tk.END)
            self.translated_text_area.insert(tk.END, self.translated_text)
            self.set_status("翻譯完成")
        except Exception as e:
            messagebox.showerror("錯誤", f"翻譯失敗：{e}")
            self.set_status("翻譯失敗")

    def add_to_dict(self):
        try:
            selected_text = self.original_text_area.selection_get()
        except:
            selected_text = ""

        if not selected_text.strip():
            messagebox.showwarning("提示", "請先在原文區選取文字")
            return

        try:
            result = add_word(selected_text)
            messagebox.showinfo("字典", result)
            self.set_status(f"字典：{result}")
        except Exception as e:
            messagebox.showerror("錯誤", f"加入字典失敗：{e}")
            self.set_status("加入字典失敗")

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

        if self.auto_translate_var.get():
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

            if self.auto_translate_var.get():
                self.do_translate()

        except Exception as e:
            messagebox.showerror("錯誤", f"OCR 失敗：{e}")
            self.set_status("OCR 失敗")

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
                self.set_status("已抓到新的 Ctrl+C 文字")

                if self.auto_translate_var.get():
                    self.do_translate()

        self.root.after(300, self.check_clipboard)

    def start_clipboard_monitor(self):
        self.root.after(300, self.check_clipboard)

    # =========================================================
    # 複製 / 右鍵
    # =========================================================
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

                result = None
                try:
                    result = add_word(selected_text)
                except Exception:
                    result = None

                if result and result.startswith("已加入字典"):
                    self.set_status("已複製原文選取內容，已加入字典")
                elif result == "已存在":
                    self.set_status("已複製原文選取內容，字典中已存在")
                elif result == "這段內容看起來像句子，請先反白單字再加入":
                    self.set_status("已複製原文選取內容（句子未加入字典）")
                else:
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