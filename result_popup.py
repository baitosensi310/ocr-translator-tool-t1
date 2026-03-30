import tkinter as tk
from tkinter import messagebox

from translator import translate
from dictionary_manager import add_word


class ResultPopup:
    def __init__(self, parent, source_text, translate_mode="local"):
        self.parent = parent
        self.source_text = source_text.strip()
        self.translate_mode = translate_mode
        self.translated_text = ""

        self.window = tk.Toplevel(self.parent)
        self.window.title("翻譯結果")
        self.window.geometry("520x320+420+180")
        self.window.minsize(420, 260)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#F5EAD9")

        self.COLOR_BG_MAIN = "#F5EAD9"
        self.COLOR_BG_PANEL = "#E7D6BE"
        self.COLOR_BG_TEXT = "#FBF6EE"
        self.COLOR_TITLE = "#4A2F21"
        self.COLOR_TEXT = "#3A2A1F"
        self.COLOR_BORDER = "#8B6A4E"
        self.COLOR_BUTTON = "#8B5E3C"
        self.COLOR_BUTTON_HOVER = "#A06A43"
        self.COLOR_BUTTON_TEXT = "#FFF8EE"

        self.build_ui()
        self.do_translate()

    def build_ui(self):
        main = tk.Frame(self.window, bg=self.COLOR_BG_MAIN)
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        container = tk.Frame(
            main,
            bg=self.COLOR_BG_PANEL,
            bd=1,
            relief="solid",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        container.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            container,
            text="翻譯結果",
            font=("Microsoft JhengHei", 16, "bold"),
            bg=self.COLOR_BG_PANEL,
            fg=self.COLOR_TITLE,
            pady=10
        )
        title.pack()

        source_label = tk.Label(
            container,
            text="原文",
            font=("Microsoft JhengHei", 11, "bold"),
            bg=self.COLOR_BG_PANEL,
            fg=self.COLOR_TITLE,
            anchor="w"
        )
        source_label.pack(fill=tk.X, padx=14, pady=(0, 4))

        self.source_textbox = tk.Text(
            container,
            height=5,
            font=("Microsoft JhengHei", 11),
            bg=self.COLOR_BG_TEXT,
            fg=self.COLOR_TEXT,
            relief="flat",
            wrap=tk.WORD
        )
        self.source_textbox.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))
        self.source_textbox.insert("1.0", self.source_text)

        translated_label = tk.Label(
            container,
            text="翻譯",
            font=("Microsoft JhengHei", 11, "bold"),
            bg=self.COLOR_BG_PANEL,
            fg=self.COLOR_TITLE,
            anchor="w"
        )
        translated_label.pack(fill=tk.X, padx=14, pady=(0, 4))

        self.translated_textbox = tk.Text(
            container,
            height=5,
            font=("Microsoft JhengHei", 11),
            bg=self.COLOR_BG_TEXT,
            fg=self.COLOR_TEXT,
            relief="flat",
            wrap=tk.WORD
        )
        self.translated_textbox.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))

        button_bar = tk.Frame(container, bg=self.COLOR_BG_PANEL)
        button_bar.pack(fill=tk.X, padx=14, pady=(0, 12))

        self.create_button(button_bar, "加入字典", self.add_current_to_dictionary).pack(side=tk.LEFT, padx=(0, 8))
        self.create_button(button_bar, "複製原文", self.copy_source).pack(side=tk.LEFT, padx=8)
        self.create_button(button_bar, "複製翻譯", self.copy_translated).pack(side=tk.LEFT, padx=8)
        self.create_button(button_bar, "關閉", self.window.destroy).pack(side=tk.RIGHT)

    def create_button(self, parent, text, command):
        btn = tk.Button(
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
            padx=12,
            pady=7,
            cursor="hand2"
        )
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.COLOR_BUTTON_HOVER))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.COLOR_BUTTON))
        return btn

    def do_translate(self):
        if not self.source_text:
            self.translated_text = "沒有可翻譯的文字"
        else:
            self.translated_text = translate(self.source_text, self.translate_mode)

        self.translated_textbox.delete("1.0", tk.END)
        self.translated_textbox.insert("1.0", self.translated_text)

    def add_current_to_dictionary(self):
        word = self.source_textbox.get("1.0", tk.END).strip()
        if not word:
            messagebox.showwarning("提示", "沒有可加入字典的文字")
            return

        result = add_word(word)
        messagebox.showinfo("字典", result)

    def copy_source(self):
        text = self.source_textbox.get("1.0", tk.END).strip()
        if text:
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            self.window.update()

    def copy_translated(self):
        text = self.translated_textbox.get("1.0", tk.END).strip()
        if text:
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            self.window.update()