import tkinter as tk
from tkinter import scrolledtext


class ResultWindow:
    def __init__(self, text):
        self.text = text

        # 建立主視窗
        self.root = tk.Tk()
        self.root.title("OCR 結果")
        self.root.geometry("800x400")
        self.root.attributes("-topmost", True)

        # 建立文字框（可捲動）
        self.text_area = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 16)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 插入 OCR 文字
        self.text_area.insert(tk.END, self.text)

        # 建立按鈕區
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        # 複製按鈕
        copy_button = tk.Button(button_frame, text="複製文字", command=self.copy_text)
        copy_button.pack(side=tk.LEFT, padx=10)

        # 關閉按鈕
        close_button = tk.Button(button_frame, text="關閉", command=self.root.destroy)
        close_button.pack(side=tk.LEFT, padx=10)

    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text)
        self.root.update()

    def show(self):
        self.root.mainloop()