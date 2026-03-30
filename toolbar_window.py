import tkinter as tk
import pyperclip
from PIL import ImageGrab

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
        self.dictionary_home = None
        self.result_popup = None

        try:
            self.last_clipboard_text = pyperclip.paste()
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

            text = self.ocr_engine.read("temp_ocr.png", "easyocr")

            if text.strip():
                self.open_result_popup(text)
        except Exception as e:
            print("OCR失敗：", e)

    def open_result_popup(self, source_text):
        if self.result_popup is not None:
            try:
                if self.result_popup.window.winfo_exists():
                    self.result_popup.update_content(source_text)
                    self.result_popup.window.lift()
                    self.result_popup.window.focus_force()
                    return
            except Exception:
                self.result_popup = None

        self.result_popup = ResultPopup(self.root, source_text)
        self.result_popup.show()

    def monitor_clipboard(self):
        try:
            text = pyperclip.paste()

            if text.strip() and text != self.last_clipboard_text:
                self.last_clipboard_text = text
                self.open_result_popup(text)
        except Exception:
            pass

        self.root.after(400, self.monitor_clipboard)

    def open_dictionary(self):
        if self.dictionary_home is not None:
            try:
                if self.dictionary_home.window.winfo_exists():
                    self.dictionary_home.window.lift()
                    self.dictionary_home.window.focus_force()
                    return
            except Exception:
                self.dictionary_home = None

        self.dictionary_home = DictionaryHome(self.root)

    def open_settings(self):
        print("設定視窗下一步接")

    def show(self):
        self.root.mainloop()