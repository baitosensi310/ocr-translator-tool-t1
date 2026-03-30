import tkinter as tk
import pyperclip

from ocr_engine import OCREngine
from select_area import ScreenSelector
from translator import translate
from dictionary_manager import add_word

from dictionary_window import DictionaryWindow
from dictionary_manager import load_dictionary, save_dictionary

class ToolbarWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.dictionary_window = None

        # ===== 視窗設定 =====
        self.root.title("Toolbar")
        self.root.geometry("420x50+300+50")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)  # 半透明
        self.root.configure(bg="#2B2B2B")

        # 可縮放
        self.root.resizable(True, False)

        # ===== 拖曳用變數 =====
        self.offset_x = 0
        self.offset_y = 0

        # ===== OCR =====
        self.ocr_engine = OCREngine()

        # ===== 剪貼簿 =====
        self.last_clipboard = ""

        # ===== UI =====
        self.build_ui()

        # ===== 綁定拖曳 =====
        self.bind_drag()

        # ===== 監聽剪貼簿 =====
        self.monitor_clipboard()

    # =============================
    # UI
    # =============================
    def build_ui(self):
        frame = tk.Frame(self.root, bg="#2B2B2B")
        frame.pack(fill=tk.BOTH, expand=True)

        self.create_button("⚙", self.open_settings)
        self.create_button("OCR", self.run_ocr)
        self.create_button("📖", self.open_dictionary)
        self.create_button("📋", self.read_clipboard)
        self.create_button("➖", self.hide_window)
        self.create_button("✖", self.root.destroy)

    def create_button(self, text, command):
        btn = tk.Button(
            self.root,
            text=text,
            command=command,
            bg="#3C3F41",
            fg="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        btn.pack(side=tk.LEFT, padx=4, pady=5)

    # =============================
    # 拖曳視窗
    # =============================
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

    # =============================
    # 功能
    # =============================
    def run_ocr(self):
        selector = ScreenSelector()
        bbox = selector.get_area()

        if not bbox:
            return

        from PIL import ImageGrab
        img = ImageGrab.grab(bbox=bbox)
        img.save("temp.png")

        text = self.ocr_engine.read("temp.png", "easyocr")
        print("OCR:", text)

    def read_clipboard(self):
        text = pyperclip.paste()
        print("Clipboard:", text)

    def monitor_clipboard(self):
        try:
            text = pyperclip.paste()

            if text != self.last_clipboard and text.strip():
                self.last_clipboard = text

                # 自動翻譯
                result = translate(text, "local")
                print("翻譯:", result)

        except:
            pass

        self.root.after(500, self.monitor_clipboard)

    def open_dictionary(self):
        if self.dictionary_window is not None:
            try:
                self.dictionary_window.window.lift()
                self.dictionary_window.window.focus_force()
                return
            except:
                self.dictionary_window = None

        self.dictionary_window = DictionaryWindow(
            self.root,
            load_dictionary,
            save_dictionary
        )

    def open_settings(self):
        print("打開設定（下一步做）")

    def hide_window(self):
        self.root.withdraw()

    def show(self):
        self.root.mainloop()