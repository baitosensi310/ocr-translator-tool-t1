import tkinter as tk
import pyperclip
from PIL import ImageGrab

from result_window import ResultWindow
from select_area import ScreenSelector
from ocr_engine import OCREngine


class ToolbarWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Toolbar")
        self.root.geometry("300x55+300+80")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)
        self.root.configure(bg="#3A2A1F")

        self.last_clipboard = ""

        try:
            self.last_clipboard = pyperclip.paste()
        except:
            self.last_clipboard = ""

        self.offset_x = 0
        self.offset_y = 0

        self.ocr_engine = OCREngine()

        self.build_ui()
        self.bind_drag()
        self.monitor_clipboard()

    def build_ui(self):
        frame = tk.Frame(self.root, bg="#3A2A1F")
        frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.create_button(frame, "OCR", self.run_ocr)
        self.create_button(frame, "字典", self.open_dictionary)
        self.create_button(frame, "設定", self.open_settings)
        self.create_button(frame, "X", self.root.destroy)

    def create_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg="#8B5E3C",
            fg="#FFF8EE",
            relief="flat",
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        btn.pack(side=tk.LEFT, padx=4)

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

        img = ImageGrab.grab(bbox=bbox)
        img.save("temp.png")

        text = self.ocr_engine.read("temp.png", "easyocr")

        if text.strip():
            self.open_result(text)

    def open_result(self, text):
        win = ResultWindow(text)
        win.show()

    def monitor_clipboard(self):
        try:
            text = pyperclip.paste()

            if text != self.last_clipboard and text.strip():
                self.last_clipboard = text
                self.open_result(text)

        except:
            pass

        self.root.after(400, self.monitor_clipboard)

    def open_dictionary(self):
        print("下一步接字典主頁")

    def open_settings(self):
        print("下一步接設定")

    def show(self):
        self.root.mainloop()