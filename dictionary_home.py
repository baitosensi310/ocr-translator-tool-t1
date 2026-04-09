import random
import re
import tkinter as tk
import pyperclip
from tkinter import filedialog
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from dictionary_manager import (
    add_word_fast,
    delete_word,
    enrich_word_data_async,
    load_dictionary,
    save_dictionary,
)


class DictionaryHome:
    def __init__(self, parent):
        self.parent = parent
        self.parent_window = getattr(parent, "root", parent)
        self.selected_language = None

        self.dictionary_data = []
        self.filtered_dictionary_data = []
        self.collection_flat_items = []
        self.current_entry = None
        self.tree_item_to_entry = {}
        self.collection_image_preview = None
        self.collection_current_image_path = ""
        self.collection_split_apply_job = None
        self.collection_pages = []
        self.collection_resize_refresh_job = None

        self.collection_search_var = tk.StringVar()
        self.collection_tag_var = tk.StringVar(value="全部")
        self.collection_page = 1
        self.collection_page_size = 12
        self.exam_tag_var = tk.StringVar(value="未分類")
        self.exam_mode_var = tk.StringVar(value="reading_input")
        self.exam_candidates = []
        self.exam_current_question = None
        self.exam_answer_shown = False
        self.exam_score = 0
        self.exam_total = 0

        self.window = tk.Toplevel(self.parent_window)
        self.window.title("字典主頁")
        self.window.geometry("1320x920+220+80")
        self.window.minsize(1180, 760)
        self.window.configure(bg="#F5EAD9")

        self.main_frame = tk.Frame(self.window, bg="#F5EAD9")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.build_home_page()

    # =========================================================
    # 共用
    # =========================================================
    def clear_page(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_soft_button(self, parent, text, command, width=12, big=False):
        font_size = 11 if not big else 15
        pady = 8 if not big else 14
        padx = 14 if not big else 20

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Microsoft JhengHei", font_size, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=padx,
            pady=pady,
            width=width,
            cursor="hand2"
        )

    def create_footer_button(self, parent, text, command, primary=False):
        return self.create_soft_button(
            parent,
            text,
            command,
            width=14 if primary else 12,
            big=True
        )

    def is_katakana_only(self, text):
        text = str(text).strip()
        if not text:
            return False

        has_katakana = False
        for char in text:
            if char in " 　・ー":
                continue

            code = ord(char)
            if 0x30A0 <= code <= 0x30FF:
                has_katakana = True
                continue

            return False

        return has_katakana

    def to_hiragana(self, text):
        result = []
        for char in str(text):
            code = ord(char)
            if 0x30A1 <= code <= 0x30F6:
                result.append(chr(code - 0x60))
            else:
                result.append(char)
        return "".join(result)

    def kana_to_romaji(self, text):
        text = self.to_hiragana(text).strip()
        if not text:
            return ""

        digraph_map = {
            "きゃ": "kya", "きゅ": "kyu", "きょ": "kyo",
            "ぎゃ": "gya", "ぎゅ": "gyu", "ぎょ": "gyo",
            "しゃ": "sha", "しゅ": "shu", "しょ": "sho",
            "じゃ": "jya", "じゅ": "jyu", "じょ": "jyo",
            "ちゃ": "cha", "ちゅ": "chu", "ちょ": "cho",
            "にゃ": "nya", "にゅ": "nyu", "にょ": "nyo",
            "ひゃ": "hya", "ひゅ": "hyu", "ひょ": "hyo",
            "びゃ": "bya", "びゅ": "byu", "びょ": "byo",
            "ぴゃ": "pya", "ぴゅ": "pyu", "ぴょ": "pyo",
            "みゃ": "mya", "みゅ": "myu", "みょ": "myo",
            "りゃ": "rya", "りゅ": "ryu", "りょ": "ryo",
            "ゔぁ": "va", "ゔぃ": "vi", "ゔぇ": "ve", "ゔぉ": "vo",
            "ふぁ": "fa", "ふぃ": "fi", "ふぇ": "fe", "ふぉ": "fo",
            "てぃ": "ti", "でぃ": "di", "とぅ": "tu", "どぅ": "du",
            "つぁ": "tsa", "つぃ": "tsi", "つぇ": "tse", "つぉ": "tso",
            "しぇ": "she", "じぇ": "je", "ちぇ": "che"
        }
        base_map = {
            "あ": "a", "い": "i", "う": "u", "え": "e", "お": "o",
            "か": "ka", "き": "ki", "く": "ku", "け": "ke", "こ": "ko",
            "が": "ga", "ぎ": "gi", "ぐ": "gu", "げ": "ge", "ご": "go",
            "さ": "sa", "し": "shi", "す": "su", "せ": "se", "そ": "so",
            "ざ": "za", "じ": "ji", "ず": "zu", "ぜ": "ze", "ぞ": "zo",
            "た": "ta", "ち": "chi", "つ": "tsu", "て": "te", "と": "to",
            "だ": "da", "ぢ": "ji", "づ": "zu", "で": "de", "ど": "do",
            "な": "na", "に": "ni", "ぬ": "nu", "ね": "ne", "の": "no",
            "は": "ha", "ひ": "hi", "ふ": "fu", "へ": "he", "ほ": "ho",
            "ば": "ba", "び": "bi", "ぶ": "bu", "べ": "be", "ぼ": "bo",
            "ぱ": "pa", "ぴ": "pi", "ぷ": "pu", "ぺ": "pe", "ぽ": "po",
            "ま": "ma", "み": "mi", "む": "mu", "め": "me", "も": "mo",
            "や": "ya", "ゆ": "yu", "よ": "yo",
            "ら": "ra", "り": "ri", "る": "ru", "れ": "re", "ろ": "ro",
            "わ": "wa", "を": "o", "ん": "n",
            "ぁ": "a", "ぃ": "i", "ぅ": "u", "ぇ": "e", "ぉ": "o",
            "ゔ": "vu"
        }

        parts = []
        i = 0
        pending_sokuon = False

        while i < len(text):
            char = text[i]

            if char in " 　":
                i += 1
                continue

            if char == "っ":
                pending_sokuon = True
                i += 1
                continue

            if char == "ー":
                if parts:
                    last = parts[-1]
                    if last[-1] in "aeiou":
                        parts[-1] = last + last[-1]
                i += 1
                continue

            kana = text[i:i + 2] if i + 1 < len(text) else ""
            if kana in digraph_map:
                romaji = digraph_map[kana]
                i += 2
            else:
                romaji = base_map.get(char, char)
                i += 1

            if pending_sokuon and romaji:
                romaji = romaji[0] + romaji
                pending_sokuon = False

            parts.append(romaji)

        compact = "".join(parts)
        compact = compact.replace("ouei", "ou ei")

        compact = re.sub(r"([aeiou])([kgsztdnhbpmrywjfvc][a-z]+)$", r"\1 \2", compact)
        compact = compact.replace("nn", "n n")
        compact = re.sub(r"([aeiou])\s+n([aeiou])", r"\1n \2", compact)
        compact = re.sub(r"([aeiou])\s+n([kgsztdnhbpmrywjfvc])", r"\1n \2", compact)
        compact = re.sub(r"\s+", " ", compact).strip()
        return compact

    def normalize_exam_reading(self, text):
        text = str(text).strip().lower()
        if not text:
            return ""

        text = self.to_hiragana(text)
        text = re.sub(r"[^a-z0-9ぁ-ん]", "", text)
        return text

    def split_exam_readings(self, text):
        raw = str(text).strip()
        if not raw:
            return []

        parts = re.split(r"\s*[/／;,；，]\s*", raw)
        return [part.strip() for part in parts if part.strip()]

    def build_exam_reading_answers(self, reading_text):
        answers = set()

        for reading in self.split_exam_readings(reading_text):
            normalized_hiragana = self.normalize_exam_reading(reading)
            if normalized_hiragana:
                answers.add(normalized_hiragana)

            romaji = self.kana_to_romaji(reading)
            normalized_romaji = self.normalize_exam_reading(romaji)
            if normalized_romaji:
                answers.add(normalized_romaji)

        return answers

    def sanitize_english_text(self, text, limit=4):
        raw = str(text).strip()
        if not raw:
            return ""

        parts = [part.strip() for part in raw.split(";") if part.strip()]
        english_parts = []

        for part in parts:
            if re.fullmatch(r"[A-Za-z0-9 ,.'/(){}\[\]\-:+?!&%]+", part):
                english_parts.append(part)

        if not english_parts:
            fallback = raw[:120].strip()
            return fallback + "..." if len(raw) > 120 else fallback

        return "; ".join(english_parts[:limit])

    def format_reading_with_romaji(self, reading):
        readings = self.split_exam_readings(reading)
        if not readings:
            return "未填寫"

        formatted = []
        for item in readings:
            hira = self.to_hiragana(item)
            romaji = self.kana_to_romaji(item)
            if romaji:
                formatted.append(f"{hira} ({romaji})")
            else:
                formatted.append(hira)

        return " / ".join(formatted)

    def set_exam_choice(self, value):
        self.exam_choice_var.set(value)

        for btn in self.exam_choice_buttons:
            option = getattr(btn, "option_value", "")
            is_selected = option == value
            marker = "◎" if is_selected else "○"
            btn.config(
                text=f"{marker}  {option}",
                fg="#8B5E3C" if is_selected else "#6A4A35"
            )

    def get_language_name(self, code):
        mapping = {
            "ja": "日文字典",
            "en": "英文字典",
            "zh": "中文字典",
            "new": "新增字典"
        }
        return mapping.get(code, "字典")

    def build_index_page_callback(self):
        language_name = self.get_language_name(self.selected_language)
        self.build_index_page(language_name)

    def hide_toolbar(self):
        try:
            self.parent_window.withdraw()
        except Exception:
            messagebox.showwarning("提示", "目前無法隱藏工具列")

    def get_external_translation_context(self):
        if hasattr(self.parent, "get_current_translation_context"):
            try:
                context = self.parent.get_current_translation_context()
                if isinstance(context, dict):
                    source_text = str(context.get("source_text", "")).strip()
                    translated_text = str(context.get("translated_text", "")).strip()
                    if source_text or translated_text:
                        return {
                            "source_text": source_text,
                            "translated_text": translated_text
                        }
            except Exception:
                pass

        clipboard_text = ""
        try:
            clipboard_text = pyperclip.paste().strip()
        except Exception:
            clipboard_text = ""

        return {
            "source_text": clipboard_text,
            "translated_text": ""
        }

    def refresh_external_context(self):
        if hasattr(self, "translation_source_text") and hasattr(self, "translation_result_text"):
            self.populate_translation_area()

    def populate_translation_area(self):
        if not hasattr(self, "translation_source_text") or not hasattr(self, "translation_result_text"):
            return

        context = self.get_external_translation_context()
        source_text = str(context.get("source_text", "")).strip()
        translated_text = str(context.get("translated_text", "")).strip()

        self.translation_source_text.delete("1.0", tk.END)
        self.translation_result_text.delete("1.0", tk.END)

        self.translation_source_text.insert("1.0", source_text or "目前沒有可顯示的原文")
        self.translation_result_text.insert("1.0", translated_text or "目前沒有可顯示的翻譯")

    def get_selected_text_from_widget(self, widget):
        try:
            return widget.get("sel.first", "sel.last").strip()
        except Exception:
            return ""

    def add_selected_translation_text_to_dict(self, widget):
        selected_text = self.get_selected_text_from_widget(widget)
        if not selected_text:
            messagebox.showinfo("字典", "請先反白要加入字典的文字", parent=self.window)
            return

        try:
            result = add_word_fast(selected_text)
            if result.startswith("已加入字典"):
                enrich_word_data_async(selected_text)
                messagebox.showinfo(
                    "字典",
                    f"{result}\n背景正在補充讀音 / 中文 / 英文 / 詞性",
                    parent=self.window
                )
            else:
                messagebox.showinfo("字典", result, parent=self.window)
        except Exception as e:
            messagebox.showerror("錯誤", f"加入字典失敗：{e}", parent=self.window)

    def copy_selected_text_from_widget(self, widget):
        selected_text = self.get_selected_text_from_widget(widget)
        if not selected_text:
            return

        self.window.clipboard_clear()
        self.window.clipboard_append(selected_text)
        self.window.update()

    def show_translation_menu(self, event, widget):
        self.translation_context_widget = widget
        self.translation_menu.tk_popup(event.x_root, event.y_root)
        self.translation_menu.grab_release()

    def handle_translation_ctrl_c(self, event, widget):
        self.copy_selected_text_from_widget(widget)
        return "break"

    # =========================================================
    # 首頁
    # =========================================================
    def build_home_page(self):
        self.clear_page()

        outer = tk.Frame(self.main_frame, bg="#F5EAD9")
        outer.pack(fill=tk.BOTH, expand=True, padx=28, pady=28)

        header = tk.Frame(outer, bg="#E7D6BE", bd=0)
        header.pack(fill=tk.X, pady=(0, 20))

        title = tk.Label(
            header,
            text="歡迎使用字典",
            font=("Microsoft JhengHei", 24, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=18
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="請先選擇要開啟的字典",
            font=("Microsoft JhengHei", 12),
            bg="#E7D6BE",
            fg="#6A4A35",
            pady=4
        )
        subtitle.pack()

        lang_area = tk.Frame(outer, bg="#F5EAD9")
        lang_area.pack(fill=tk.BOTH, expand=True)

        lang_title = tk.Label(
            lang_area,
            text="字典入口",
            font=("Microsoft JhengHei", 16, "bold"),
            bg="#F5EAD9",
            fg="#4A2F21",
            anchor="w"
        )
        lang_title.pack(anchor="w", pady=(0, 14))

        card_grid = tk.Frame(lang_area, bg="#F5EAD9")
        card_grid.pack(fill=tk.BOTH, expand=True)

        languages = [
            ("日文字典", "ja", "適合 OCR 日文、讀音、詞性、例句"),
            ("英文字典", "en", "適合單字查詢、片語與基本分類"),
            ("中文字典", "zh", "適合中文詞語收藏與整理"),
            ("新增字典", "new", "預留未來建立新的語言字典或分類")
        ]

        for i, (title_text, code, desc) in enumerate(languages):
            card = tk.Frame(
                card_grid,
                bg="#E7D6BE",
                bd=0,
                highlightthickness=0,
                padx=18,
                pady=18
            )
            r = i // 2
            c = i % 2
            card.grid(row=r, column=c, sticky="nsew", padx=12, pady=12)

            card_title = tk.Label(
                card,
                text=title_text,
                font=("Microsoft JhengHei", 16, "bold"),
                bg="#E7D6BE",
                fg="#4A2F21"
            )
            card_title.pack(anchor="w")

            card_desc = tk.Label(
                card,
                text=desc,
                font=("Microsoft JhengHei", 11),
                bg="#E7D6BE",
                fg="#6A4A35",
                justify="left",
                wraplength=340,
                pady=10
            )
            card_desc.pack(anchor="w")

            open_btn = self.create_soft_button(
                card,
                text="開啟",
                command=lambda lang=code, name=title_text: self.open_index_page(lang, name),
                width=10
            )
            open_btn.pack(anchor="w", pady=(8, 0))

        card_grid.grid_rowconfigure(0, weight=1)
        card_grid.grid_rowconfigure(1, weight=1)
        card_grid.grid_columnconfigure(0, weight=1)
        card_grid.grid_columnconfigure(1, weight=1)

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X, pady=(14, 0))

        close_btn = self.create_footer_button(bottom, "關閉", self.window.destroy)
        close_btn.pack(side=tk.RIGHT)

    # =========================================================
    # 索引頁
    # =========================================================
    def open_index_page(self, lang_code, lang_name):
        self.selected_language = lang_code
        self.build_index_page(lang_name)

    def build_index_page(self, lang_name):
        self.clear_page()

        outer = tk.Frame(self.main_frame, bg="#F5EAD9")
        outer.pack(fill=tk.BOTH, expand=True, padx=28, pady=28)

        header = tk.Frame(outer, bg="#E7D6BE", bd=0)
        header.pack(fill=tk.X, pady=(0, 20))

        title = tk.Label(
            header,
            text=f"{lang_name}・索引",
            font=("Microsoft JhengHei", 22, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=18
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="請選擇要進入的功能區",
            font=("Microsoft JhengHei", 11),
            bg="#E7D6BE",
            fg="#6A4A35",
            pady=4
        )
        subtitle.pack()

        center = tk.Frame(outer, bg="#F5EAD9")
        center.pack(fill=tk.BOTH, expand=True)

        options = [
            ("1. 翻譯區", "只顯示原文與翻譯，可作為輕量閱讀區", self.open_translation_area),
            ("2. 單字收藏", "像一本字典一樣翻閱收藏內容", self.open_collection_area),
            ("3. 考試區", "之後用來測驗自己，目前先保留架構", self.open_exam_area),
        ]

        for title_text, desc, command in options:
            card = tk.Frame(
                center,
                bg="#EADCC8",
                bd=0,
                highlightthickness=0,
                padx=24,
                pady=24
            )
            card.pack(fill=tk.X, pady=10)

            title_label = tk.Label(
                card,
                text=title_text,
                font=("Microsoft JhengHei", 17, "bold"),
                bg="#EADCC8",
                fg="#4A2F21",
                anchor="w"
            )
            title_label.pack(anchor="w")

            desc_label = tk.Label(
                card,
                text=desc,
                font=("Microsoft JhengHei", 11),
                bg="#EADCC8",
                fg="#6A4A35",
                justify="left",
                wraplength=860,
                pady=8
            )
            desc_label.pack(anchor="w")

            enter_btn = self.create_soft_button(card, "進入", command, width=10)
            enter_btn.pack(anchor="w", pady=(8, 0))

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X, pady=(16, 0))

        back_btn = self.create_footer_button(bottom, "返回語言選擇", self.build_home_page, primary=True)
        back_btn.pack(side=tk.LEFT)

        close_btn = self.create_footer_button(bottom, "關閉", self.window.destroy)
        close_btn.pack(side=tk.RIGHT)

    # =========================================================
    # 1. 翻譯區
    # =========================================================
    def open_translation_area(self):
        self.clear_page()

        outer = tk.Frame(self.main_frame, bg="#F5EAD9")
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        header = tk.Frame(outer, bg="#E7D6BE")
        header.pack(fill=tk.X, pady=(0, 18))

        title = tk.Label(
            header,
            text="翻譯區",
            font=("Microsoft JhengHei", 22, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=18
        )
        title.pack()

        content = tk.PanedWindow(
            outer,
            orient=tk.HORIZONTAL,
            bg="#F5EAD9",
            sashwidth=10,
            sashrelief="flat",
            bd=0,
            highlightthickness=0
        )
        content.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(content, bg="#EADCC8", bd=0)
        right_panel = tk.Frame(content, bg="#EADCC8", bd=0)

        content.add(left_panel, minsize=260)
        content.add(right_panel, minsize=260)

        left_title = tk.Label(
            left_panel,
            text="原文區",
            font=("Microsoft JhengHei", 15, "bold"),
            bg="#EADCC8",
            fg="#4A2F21",
            padx=14,
            pady=12,
            anchor="w"
        )
        left_title.pack(fill=tk.X)

        self.translation_source_text = tk.Text(
            left_panel,
            font=("Microsoft JhengHei", 12),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            wrap=tk.WORD
        )
        self.translation_source_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        right_title = tk.Label(
            right_panel,
            text="翻譯區",
            font=("Microsoft JhengHei", 15, "bold"),
            bg="#EADCC8",
            fg="#4A2F21",
            padx=14,
            pady=12,
            anchor="w"
        )
        right_title.pack(fill=tk.X)

        self.translation_result_text = tk.Text(
            right_panel,
            font=("Microsoft JhengHei", 12),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            wrap=tk.WORD
        )
        self.translation_result_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self.translation_context_widget = self.translation_source_text
        self.translation_menu = tk.Menu(self.window, tearoff=0)
        self.translation_menu.add_command(
            label="複製選取",
            command=lambda: self.copy_selected_text_from_widget(self.translation_context_widget)
        )
        self.translation_menu.add_command(
            label="加入字典",
            command=lambda: self.add_selected_translation_text_to_dict(self.translation_context_widget)
        )

        self.translation_source_text.bind(
            "<Button-3>",
            lambda event: self.show_translation_menu(event, self.translation_source_text)
        )
        self.translation_result_text.bind(
            "<Button-3>",
            lambda event: self.show_translation_menu(event, self.translation_result_text)
        )
        self.translation_source_text.bind(
            "<Control-c>",
            lambda event: self.handle_translation_ctrl_c(event, self.translation_source_text)
        )
        self.translation_result_text.bind(
            "<Control-c>",
            lambda event: self.handle_translation_ctrl_c(event, self.translation_result_text)
        )

        try:
            self.populate_translation_area()
        except Exception as e:
            self.translation_source_text.delete("1.0", tk.END)
            self.translation_result_text.delete("1.0", tk.END)
            self.translation_source_text.insert("1.0", "目前沒有可顯示的原文")
            self.translation_result_text.insert("1.0", f"翻譯區載入失敗：{e}")

        outer.after(120, lambda: content.sash_place(0, 520, 0))

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X, pady=(14, 0))

        left_actions = tk.Frame(bottom, bg="#F5EAD9")
        left_actions.pack(side=tk.LEFT)

        back_btn = self.create_footer_button(left_actions, "返回索引", self.build_index_page_callback, primary=True)
        back_btn.pack(side=tk.LEFT)

        hide_toolbar_btn = self.create_footer_button(left_actions, "隱藏工具列", self.hide_toolbar)
        hide_toolbar_btn.pack(side=tk.LEFT, padx=(12, 0))

        close_btn = self.create_footer_button(bottom, "關閉", self.window.destroy)
        close_btn.pack(side=tk.RIGHT)

    # =========================================================
    # 2. 單字收藏
    # =========================================================
    def open_collection_area(self):
        self.clear_page()
        self.load_dictionary_data()

        outer = tk.Frame(self.main_frame, bg="#F5EAD9")
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header = tk.Frame(outer, bg="#E7D6BE")
        header.pack(fill=tk.X, pady=(0, 18))

        title = tk.Label(
            header,
            text="單字收藏",
            font=("Microsoft JhengHei", 22, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=18
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="像一本字典一樣翻閱你收藏的單字",
            font=("Microsoft JhengHei", 11),
            bg="#E7D6BE",
            fg="#6A4A35",
            pady=4
        )
        subtitle.pack()

        body = tk.Frame(outer, bg="#F5EAD9")
        body.pack(fill=tk.BOTH, expand=True, pady=(0, 16))

        left_panel = tk.Frame(body, bg="#EADCC8", bd=0, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        left_title = tk.Label(
            left_panel,
            text="單字索引",
            font=("Microsoft JhengHei", 15, "bold"),
            bg="#EADCC8",
            fg="#4A2F21",
            pady=12
        )
        left_title.pack(fill=tk.X)

        search_frame = tk.Frame(left_panel, bg="#EADCC8")
        search_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.collection_search_var,
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="flat",
            bd=0
        )
        search_entry.pack(fill=tk.X, ipady=6)
        search_entry.bind("<KeyRelease>", self.on_collection_search_changed)

        tag_frame = tk.Frame(left_panel, bg="#EADCC8")
        tag_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        self.collection_tag_menu = tk.OptionMenu(tag_frame, self.collection_tag_var, "全部")
        self.collection_tag_menu.config(
            font=("Microsoft JhengHei", 10),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.collection_tag_menu["menu"].config(
            font=("Microsoft JhengHei", 10),
            bg="#FBF6EE",
            fg="#3A2A1F"
        )
        self.collection_tag_menu.pack(fill=tk.X)

        tree_frame = tk.Frame(left_panel, bg="#EADCC8")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        tree_scrollbar = tk.Scrollbar(tree_frame)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.collection_tree = ttk.Treeview(
            tree_frame,
            show="tree",
            yscrollcommand=tree_scrollbar.set,
            selectmode="browse"
        )
        self.collection_tree.pack(fill=tk.BOTH, expand=True)
        self.collection_tree.bind("<Configure>", self.on_collection_tree_resized)

        tree_scrollbar.config(command=self.collection_tree.yview)

        self.collection_tree.bind("<<TreeviewSelect>>", self.on_select_collection_word)

        page_bar = tk.Frame(left_panel, bg="#EADCC8")
        page_bar.pack(fill=tk.X, padx=12, pady=(0, 12))

        button_row = tk.Frame(page_bar, bg="#EADCC8")
        button_row.pack(fill=tk.X)

        prev_btn = self.create_soft_button(button_row, "上一頁", self.prev_collection_page, width=8)
        prev_btn.pack(side=tk.LEFT)

        next_btn = self.create_soft_button(button_row, "下一頁", self.next_collection_page, width=8)
        next_btn.pack(side=tk.RIGHT)

        self.collection_page_label = tk.Label(
            page_bar,
            text="第 1 頁 / 共 1 頁",
            font=("Microsoft JhengHei", 10),
            bg="#EADCC8",
            fg="#6A4A35"
        )
        self.collection_page_label.pack(pady=(6, 0))

        book_frame = tk.Frame(body, bg="#D8C2A2", bd=0)
        book_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        left_page = tk.Frame(book_frame, bg="#FBF6EE", bd=0, width=620)
        left_page.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 8), pady=16)
        left_page.pack_propagate(False)

        right_page = tk.Frame(book_frame, bg="#FBF6EE", bd=0, width=430)
        right_page.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(8, 16), pady=16)
        right_page.pack_propagate(False)

        left_page_title = tk.Label(
            left_page,
            text="左頁",
            font=("Microsoft JhengHei", 15, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            pady=12
        )
        left_page_title.pack()

        left_content = tk.Frame(left_page, bg="#FBF6EE")
        left_content.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        original_section = tk.Frame(left_content, bg="#FBF6EE", bd=0, height=90)
        original_section.pack(fill=tk.X, pady=(0, 10))
        original_section.pack_propagate(False)

        note_section = tk.Frame(left_content, bg="#FBF6EE", bd=0, height=180)
        note_section.pack(fill=tk.X, pady=(0, 10))
        note_section.pack_propagate(False)

        image_section = tk.Frame(left_content, bg="#FBF6EE", bd=0)
        image_section.pack(fill=tk.BOTH, expand=True)

        original_label = tk.Label(
            original_section,
            text="原文",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        original_label.pack(fill=tk.X, pady=(0, 4))

        self.collection_original_text = tk.Text(
            original_section,
            height=1,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            wrap=tk.WORD
        )
        self.collection_original_text.pack(fill=tk.BOTH, expand=True)

        note_label = tk.Label(
            note_section,
            text="補充",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        note_label.pack(fill=tk.X, pady=(0, 4))

        self.collection_note_text = tk.Text(
            note_section,
            height=5,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            wrap=tk.WORD
        )
        self.collection_note_text.pack(fill=tk.BOTH, expand=True)

        image_header = tk.Frame(image_section, bg="#FBF6EE")
        image_header.pack(fill=tk.X)

        image_label = tk.Label(
            image_header,
            text="圖片區",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        image_label.pack(side=tk.LEFT)

        image_add_btn = self.create_soft_button(image_header, "放入圖片", self.choose_collection_image, width=8)
        image_add_btn.pack(side=tk.RIGHT)

        image_clear_btn = self.create_soft_button(image_header, "清除圖片", self.clear_collection_image, width=8)
        image_clear_btn.pack(side=tk.RIGHT, padx=(0, 8))

        self.collection_image_info_label = tk.Label(
            image_section,
            text="可放入圖片或 GIF，會跟著這個單字一起保存",
            font=("Microsoft JhengHei", 10),
            bg="#FBF6EE",
            fg="#6A4A35",
            anchor="w"
        )
        self.collection_image_info_label.pack(fill=tk.X, pady=(6, 8))

        self.collection_image_preview_label = tk.Label(
            image_section,
            bg="#F8F1E7",
            fg="#6A4A35",
            text="尚未放入圖片",
            anchor="center",
            justify="center"
        )
        self.collection_image_preview_label.pack(fill=tk.BOTH, expand=True)

        right_page_title = tk.Label(
            right_page,
            text="右頁",
            font=("Microsoft JhengHei", 15, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            pady=12
        )
        right_page_title.pack()

        self.collection_translation_text = self.create_labeled_text(right_page, "中文", 4)
        self.collection_english_text = self.create_labeled_text(right_page, "英文", 3)
        self.collection_reading_entry = self.create_labeled_entry(right_page, "讀音")
        self.collection_pos_entry = self.create_labeled_entry(right_page, "詞性")
        self.collection_tag_entry = self.create_labeled_entry(right_page, "分類 tag（用逗號分隔）")
        self.collection_example_text = self.create_labeled_text(right_page, "例句（每行一個）", 5)
        self.collection_usage_text = self.create_labeled_text(right_page, "用法", 5)

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X)

        left_actions = tk.Frame(bottom, bg="#F5EAD9")
        left_actions.pack(side=tk.LEFT)

        back_btn = self.create_footer_button(left_actions, "返回索引", self.build_index_page_callback, primary=True)
        back_btn.pack(side=tk.LEFT)

        refresh_btn = self.create_footer_button(left_actions, "重新整理", self.reload_collection_area)
        refresh_btn.pack(side=tk.LEFT, padx=(12, 0))

        save_btn = self.create_footer_button(left_actions, "儲存內容", self.save_collection_entry)
        save_btn.pack(side=tk.LEFT, padx=(12, 0))

        middle_actions = tk.Frame(bottom, bg="#F5EAD9")
        middle_actions.pack(side=tk.LEFT, padx=18)

        delete_btn = self.create_footer_button(middle_actions, "刪除單字", self.delete_current_word)
        delete_btn.pack(side=tk.LEFT)

        change_lang_btn = self.create_footer_button(middle_actions, "切換語言", self.change_current_word_language)
        change_lang_btn.pack(side=tk.LEFT, padx=(12, 0))

        close_btn = self.create_footer_button(bottom, "關閉", self.window.destroy)
        close_btn.pack(side=tk.RIGHT)

        self.refresh_collection_list()
        self.show_empty_collection_detail()


    def create_labeled_entry(self, parent, label_text):
        label = tk.Label(
            parent,
            text=label_text,
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        label.pack(fill=tk.X, padx=14, pady=(6, 4))

        entry = tk.Entry(
            parent,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0
        )
        entry.pack(fill=tk.X, padx=14, pady=(0, 10), ipady=6)
        return entry

    def create_labeled_text(self, parent, label_text, height):
        label = tk.Label(
            parent,
            text=label_text,
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        label.pack(fill=tk.X, padx=14, pady=(6, 4))

        text_widget = tk.Text(
            parent,
            height=height,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            wrap=tk.WORD
        )
        text_widget.pack(fill=tk.X, padx=14, pady=(0, 10))
        return text_widget

    def normalize_collection_split(self, value):
        default = [0.18, 0.32, 0.50]
        if not isinstance(value, list) or len(value) != 3:
            return default

        try:
            result = [float(x) for x in value]
        except Exception:
            return default

        total = sum(result)
        if total <= 0:
            return default

        result = [max(0.1, x / total) for x in result]
        total = sum(result)
        return [x / total for x in result]

    def apply_collection_split(self, split_value):
        if not hasattr(self, "collection_left_pane"):
            return

        split_value = self.normalize_collection_split(split_value)
        pane_height = max(self.collection_left_pane.winfo_height(), 320)
        sash1 = int(pane_height * split_value[0])
        sash2 = int(pane_height * (split_value[0] + split_value[1]))

        try:
            self.collection_left_pane.sash_place(0, 1, sash1)
            self.collection_left_pane.sash_place(1, 1, sash2)
        except Exception:
            pass

    def schedule_apply_collection_split(self, split_value):
        if not hasattr(self, "collection_left_pane"):
            return

        if self.collection_split_apply_job is not None:
            try:
                self.window.after_cancel(self.collection_split_apply_job)
            except Exception:
                pass

        self.collection_split_apply_job = self.window.after(
            80, lambda: self.apply_collection_split(split_value)
        )

    def get_current_collection_split(self):
        if not hasattr(self, "collection_left_pane"):
            return [0.18, 0.32, 0.50]

        pane_height = max(self.collection_left_pane.winfo_height(), 320)
        try:
            sash1 = self.collection_left_pane.sash_coord(0)[1]
            sash2 = self.collection_left_pane.sash_coord(1)[1]
        except Exception:
            return [0.18, 0.32, 0.50]

        top = max(0.1, sash1 / pane_height)
        middle = max(0.1, (sash2 - sash1) / pane_height)
        bottom = max(0.1, (pane_height - sash2) / pane_height)
        return self.normalize_collection_split([top, middle, bottom])

    def on_collection_pane_resize(self, event=None):
        if self.current_entry is None:
            return
        self.current_entry["左頁分割"] = self.get_current_collection_split()

    def choose_collection_image(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先從左邊選一個單字")
            return

        path = filedialog.askopenfilename(
            parent=self.window,
            title="選擇圖片",
            filetypes=[
                ("圖片檔", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp"),
                ("所有檔案", "*.*")
            ]
        )
        if not path:
            return

        self.collection_current_image_path = path
        self.show_collection_image(path)

    def clear_collection_image(self):
        self.collection_current_image_path = ""
        self.collection_image_preview = None
        if hasattr(self, "collection_image_preview_label"):
            self.collection_image_preview_label.config(image="", text="尚未放入圖片")
        if hasattr(self, "collection_image_info_label"):
            self.collection_image_info_label.config(text="可放入圖片或 GIF，會跟著這個單字一起保存")

    def show_collection_image(self, path):
        path = str(path).strip()
        if not path:
            self.clear_collection_image()
            return

        try:
            image = Image.open(path)
            image.thumbnail((420, 260))
            self.collection_image_preview = ImageTk.PhotoImage(image)
            self.collection_image_preview_label.config(image=self.collection_image_preview, text="")
            self.collection_image_info_label.config(text=path)
            self.collection_current_image_path = path
        except Exception:
            self.collection_image_preview = None
            self.collection_image_preview_label.config(image="", text="圖片載入失敗")
            self.collection_image_info_label.config(text=path)


    # =========================================================
    # 3. 考試區
    # =========================================================
    def open_exam_area(self):
        self.clear_page()
        self.load_dictionary_data()

        outer = tk.Frame(self.main_frame, bg="#F5EAD9")
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        header = tk.Frame(outer, bg="#E7D6BE")
        header.pack(fill=tk.X, pady=(0, 18))

        title = tk.Label(
            header,
            text="日文考試",
            font=("Microsoft JhengHei", 22, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=18
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="依照目前字典分類出題，適合用來快速練讀音與字義辨識",
            font=("Microsoft JhengHei", 11),
            bg="#E7D6BE",
            fg="#6A4A35",
            pady=4
        )
        subtitle.pack()

        body = tk.Frame(outer, bg="#F5EAD9")
        body.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(body, bg="#EADCC8", bd=0, width=320)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(body, bg="#EADCC8", bd=0)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        control_title = tk.Label(
            left_panel,
            text="出題設定",
            font=("Microsoft JhengHei", 15, "bold"),
            bg="#EADCC8",
            fg="#4A2F21",
            pady=12
        )
        control_title.pack(fill=tk.X)

        tag_label = tk.Label(
            left_panel,
            text="分類",
            font=("Microsoft JhengHei", 11, "bold"),
            bg="#EADCC8",
            fg="#4A2F21",
            anchor="w"
        )
        tag_label.pack(fill=tk.X, padx=14, pady=(8, 6))

        exam_tag_options = self.get_exam_tag_options()
        if self.exam_tag_var.get() not in exam_tag_options:
            self.exam_tag_var.set(exam_tag_options[0])

        self.exam_tag_menu = tk.OptionMenu(
            left_panel,
            self.exam_tag_var,
            *exam_tag_options,
            command=lambda _value: self.on_exam_filter_changed()
        )
        self.exam_tag_menu.config(
            font=("Microsoft JhengHei", 10),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.exam_tag_menu["menu"].config(
            font=("Microsoft JhengHei", 10),
            bg="#FBF6EE",
            fg="#3A2A1F"
        )
        self.exam_tag_menu.pack(fill=tk.X, padx=14)

        mode_label = tk.Label(
            left_panel,
            text="題型",
            font=("Microsoft JhengHei", 11, "bold"),
            bg="#EADCC8",
            fg="#4A2F21",
            anchor="w"
        )
        mode_label.pack(fill=tk.X, padx=14, pady=(14, 6))

        mode_frame = tk.Frame(left_panel, bg="#EADCC8")
        mode_frame.pack(fill=tk.X, padx=14)

        reading_radio = tk.Radiobutton(
            mode_frame,
            text="看單字輸入讀音",
            variable=self.exam_mode_var,
            value="reading_input",
            command=self.on_exam_filter_changed,
            font=("Microsoft JhengHei", 10),
            bg="#EADCC8",
            fg="#6A4A35",
            selectcolor="#FBF6EE",
            activebackground="#EADCC8",
            activeforeground="#6A4A35",
            highlightthickness=0,
            bd=0,
            anchor="w",
            justify="left"
        )
        reading_radio.pack(fill=tk.X, pady=(0, 6))

        meaning_radio = tk.Radiobutton(
            mode_frame,
            text="看中文選單字",
            variable=self.exam_mode_var,
            value="meaning_choice",
            command=self.on_exam_filter_changed,
            font=("Microsoft JhengHei", 10),
            bg="#EADCC8",
            fg="#6A4A35",
            selectcolor="#FBF6EE",
            activebackground="#EADCC8",
            activeforeground="#6A4A35",
            highlightthickness=0,
            bd=0,
            anchor="w",
            justify="left"
        )
        meaning_radio.pack(fill=tk.X)

        self.exam_pool_label = tk.Label(
            left_panel,
            text="可出題數：0",
            font=("Microsoft JhengHei", 10),
            bg="#EADCC8",
            fg="#6A4A35",
            anchor="w",
            justify="left"
        )
        self.exam_pool_label.pack(fill=tk.X, padx=14, pady=(18, 4))

        self.exam_score_label = tk.Label(
            left_panel,
            text="作答進度：0 / 0",
            font=("Microsoft JhengHei", 10),
            bg="#EADCC8",
            fg="#6A4A35",
            anchor="w"
        )
        self.exam_score_label.pack(fill=tk.X, padx=14, pady=(0, 12))

        left_button_row = tk.Frame(left_panel, bg="#EADCC8")
        left_button_row.pack(fill=tk.X, padx=14, pady=(4, 0))

        new_question_btn = self.create_soft_button(left_button_row, "下一題", self.next_exam_question, width=10)
        new_question_btn.pack(side=tk.LEFT)

        reset_score_btn = self.create_soft_button(left_button_row, "重置成績", self.reset_exam_score, width=10)
        reset_score_btn.pack(side=tk.RIGHT)

        quiz_title = tk.Label(
            right_panel,
            text="題目區",
            font=("Microsoft JhengHei", 15, "bold"),
            bg="#EADCC8",
            fg="#4A2F21",
            pady=12
        )
        quiz_title.pack(fill=tk.X)

        quiz_card = tk.Frame(right_panel, bg="#FBF6EE", bd=0)
        quiz_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        self.exam_question_type_label = tk.Label(
            quiz_card,
            text="",
            font=("Microsoft JhengHei", 11, "bold"),
            bg="#FBF6EE",
            fg="#8B5E3C",
            anchor="w"
        )
        self.exam_question_type_label.pack(fill=tk.X, padx=18, pady=(18, 8))

        self.exam_prompt_label = tk.Label(
            quiz_card,
            text="",
            font=("Microsoft JhengHei", 22, "bold"),
            bg="#FBF6EE",
            fg="#3A2A1F",
            wraplength=760,
            justify="left",
            anchor="w"
        )
        self.exam_prompt_label.pack(fill=tk.X, padx=18, pady=(0, 12))

        self.exam_hint_label = tk.Label(
            quiz_card,
            text="",
            font=("Microsoft JhengHei", 10),
            bg="#FBF6EE",
            fg="#7A6555",
            wraplength=760,
            justify="left",
            anchor="w"
        )
        self.exam_hint_label.pack(fill=tk.X, padx=18, pady=(0, 12))

        self.exam_answer_entry = tk.Entry(
            quiz_card,
            font=("Microsoft JhengHei", 14),
            bg="#FFFDF8",
            fg="#2E231B",
            relief="flat",
            bd=0
        )
        self.exam_answer_entry.pack(fill=tk.X, padx=18, pady=(0, 12), ipady=8)
        self.exam_answer_entry.bind("<Return>", self.submit_exam_answer)

        self.exam_choice_var = tk.StringVar(value="")
        self.exam_choice_buttons = []
        choice_frame = tk.Frame(quiz_card, bg="#FBF6EE")
        choice_frame.pack(fill=tk.X, padx=18, pady=(0, 12))
        for _ in range(4):
            btn = tk.Button(
                choice_frame,
                text="",
                font=("Microsoft JhengHei", 11),
                bg="#FBF6EE",
                fg="#6A4A35",
                activebackground="#FBF6EE",
                activeforeground="#6A4A35",
                highlightthickness=0,
                bd=0,
                anchor="w",
                justify="left",
                relief="flat",
                cursor="hand2",
                padx=0,
                pady=4
            )
            btn.pack(fill=tk.X, pady=3)
            self.exam_choice_buttons.append(btn)

        action_row = tk.Frame(quiz_card, bg="#FBF6EE")
        action_row.pack(fill=tk.X, padx=18, pady=(2, 10))

        submit_btn = self.create_soft_button(action_row, "送出答案", self.submit_exam_answer, width=10)
        submit_btn.pack(side=tk.LEFT)

        reveal_btn = self.create_soft_button(action_row, "看答案", self.reveal_exam_answer, width=10)
        reveal_btn.pack(side=tk.LEFT, padx=10)

        next_btn = self.create_soft_button(action_row, "換一題", self.next_exam_question, width=10)
        next_btn.pack(side=tk.LEFT)

        self.exam_feedback_label = tk.Label(
            quiz_card,
            text="",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#8B5E3C",
            justify="left",
            anchor="w",
            wraplength=760
        )
        self.exam_feedback_label.pack(fill=tk.X, padx=18, pady=(0, 10))

        self.exam_answer_label = tk.Label(
            quiz_card,
            text="",
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#4A2F21",
            justify="left",
            anchor="w",
            wraplength=760
        )
        self.exam_answer_label.pack(fill=tk.X, padx=18, pady=(0, 18))

        self.on_exam_filter_changed()

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X, pady=(14, 0))

        back_btn = self.create_footer_button(bottom, "返回索引", self.build_index_page_callback, primary=True)
        back_btn.pack(side=tk.LEFT)

        close_btn = self.create_footer_button(bottom, "關閉", self.window.destroy)
        close_btn.pack(side=tk.RIGHT)

    def get_exam_tag_options(self):
        tags = set()
        has_unclassified = False

        for item in self.dictionary_data:
            if str(item.get("language", "")).strip() != "ja":
                continue

            normalized_tags = self.get_normalized_tags(item)
            if normalized_tags == ["未分類"]:
                has_unclassified = True
            else:
                for tag in normalized_tags:
                    tags.add(tag)

        ordered_tags = []
        if has_unclassified:
            ordered_tags.append("未分類")

        ordered_tags.extend(sorted(tags))
        return ordered_tags or ["未分類"]

    def on_exam_filter_changed(self):
        self.exam_candidates = self.get_exam_candidates()
        self.exam_current_question = None
        self.exam_answer_shown = False
        self.exam_choice_var.set("")

        self.update_exam_score_label()

        if hasattr(self, "exam_pool_label"):
            mode_text = "讀音輸入" if self.exam_mode_var.get() == "reading_input" else "中文選字"
            self.exam_pool_label.config(
                text=f"可出題數：{len(self.exam_candidates)}\n目前題型：{mode_text}"
            )

        self.next_exam_question()

    def get_exam_candidates(self):
        selected_tag = self.exam_tag_var.get().strip()
        mode = self.exam_mode_var.get().strip()
        result = []

        for item in self.dictionary_data:
            if str(item.get("language", "")).strip() != "ja":
                continue

            normalized_tags = self.get_normalized_tags(item)
            if selected_tag not in normalized_tags:
                continue

            word = str(item.get("單字", "")).strip()
            reading = str(item.get("讀音", "")).strip()
            chinese = str(item.get("中文", "")).strip()

            if not word:
                continue

            if mode == "reading_input" and not reading:
                continue

            if mode == "reading_input" and self.is_katakana_only(word):
                continue

            if mode == "meaning_choice" and not chinese:
                continue

            result.append(item)

        return result

    def next_exam_question(self):
        if not hasattr(self, "exam_prompt_label"):
            return

        self.exam_feedback_label.config(text="")
        self.exam_answer_label.config(text="")
        self.exam_answer_shown = False
        self.exam_choice_var.set("")
        self.exam_answer_entry.delete(0, tk.END)

        if not self.exam_candidates:
            self.exam_current_question = None
            self.exam_question_type_label.config(text="目前無法出題")
            self.exam_prompt_label.config(text="這個分類目前沒有可用的日文題目")
            self.exam_hint_label.config(text="提示：你可以先去單字收藏補上讀音或中文，再回來練習。")
            self.exam_answer_entry.pack_forget()
            for btn in self.exam_choice_buttons:
                btn.pack_forget()
            return

        mode = self.exam_mode_var.get().strip()
        item = random.choice(self.exam_candidates)
        self.exam_current_question = item

        if mode == "reading_input":
            self.exam_question_type_label.config(text="題型：看單字輸入讀音")
            self.exam_prompt_label.config(text=item.get("單字", ""))
            chinese = str(item.get("中文", "")).strip()
            hint_text = f"中文提示：{chinese}" if chinese else "中文提示：目前沒有中文，可直接憑記憶作答"
            hint_text += "\n請輸入羅馬讀音或平假名"
            self.exam_hint_label.config(text=hint_text)
            for btn in self.exam_choice_buttons:
                btn.pack_forget()
            self.exam_answer_entry.pack(fill=tk.X, padx=18, pady=(0, 12), ipady=8)
            self.exam_answer_entry.focus_set()
            return

        self.exam_question_type_label.config(text="題型：看中文選單字")
        self.exam_prompt_label.config(text=str(item.get("中文", "")).strip())
        reading = str(item.get("讀音", "")).strip()
        self.exam_hint_label.config(
            text=f"讀音提示：{self.format_reading_with_romaji(reading)}" if reading else "讀音提示：無"
        )
        self.exam_answer_entry.pack_forget()

        options = self.build_exam_choices(item)
        for btn in self.exam_choice_buttons:
            btn.pack_forget()

        for btn, option in zip(self.exam_choice_buttons, options):
            btn.option_value = option
            btn.config(command=lambda value=option: self.set_exam_choice(value))
            btn.pack(fill=tk.X, pady=3)

        self.set_exam_choice("")

    def build_exam_choices(self, correct_item):
        correct_word = str(correct_item.get("單字", "")).strip()

        pool = []
        for item in self.exam_candidates:
            word = str(item.get("單字", "")).strip()
            if word and word != correct_word:
                pool.append(word)

        unique_pool = []
        seen = set()
        for word in pool:
            if word in seen:
                continue
            seen.add(word)
            unique_pool.append(word)

        random.shuffle(unique_pool)
        options = unique_pool[:3] + [correct_word]
        random.shuffle(options)
        return options

    def submit_exam_answer(self, event=None):
        if not self.exam_current_question:
            return

        if self.exam_answer_shown:
            self.next_exam_question()
            return

        mode = self.exam_mode_var.get().strip()
        correct_answer = ""
        user_answer = ""

        if mode == "reading_input":
            correct_answer = str(self.exam_current_question.get("讀音", "")).strip()
            user_answer = self.exam_answer_entry.get().strip()
        else:
            correct_answer = str(self.exam_current_question.get("單字", "")).strip()
            user_answer = self.exam_choice_var.get().strip()

        if not user_answer:
            self.exam_feedback_label.config(text="請先作答再送出", fg="#A14A2A")
            return

        if mode == "reading_input":
            normalized_user_answer = self.normalize_exam_reading(user_answer)
            accepted_answers = self.build_exam_reading_answers(correct_answer)
            is_correct = normalized_user_answer in accepted_answers
        else:
            is_correct = user_answer == correct_answer

        self.exam_total += 1
        if is_correct:
            self.exam_score += 1

        self.update_exam_score_label()
        self.exam_answer_shown = True

        if is_correct:
            self.exam_feedback_label.config(text="答對了", fg="#2E7D32")
        else:
            self.exam_feedback_label.config(text=f"答錯了，你的答案：{user_answer}", fg="#A14A2A")

        self.exam_answer_label.config(text=self.format_exam_answer_text())

    def reveal_exam_answer(self):
        if not self.exam_current_question:
            return

        self.exam_answer_shown = True
        self.exam_feedback_label.config(text="答案已顯示，這題不計分", fg="#8B5E3C")
        self.exam_answer_label.config(text=self.format_exam_answer_text())

    def format_exam_answer_text(self):
        if not self.exam_current_question:
            return ""

        word = str(self.exam_current_question.get("單字", "")).strip()
        reading = str(self.exam_current_question.get("讀音", "")).strip()
        chinese = str(self.exam_current_question.get("中文", "")).strip()
        english = self.sanitize_english_text(self.exam_current_question.get("英文", ""))
        tags = ", ".join(self.get_normalized_tags(self.exam_current_question))

        return (
            f"正解：{word}\n"
            f"讀音：{self.format_reading_with_romaji(reading)}\n"
            f"中文：{chinese or '未填寫'}\n"
            f"英文：{english or '未填寫'}\n"
            f"分類：{tags}"
        )

    def reset_exam_score(self):
        self.exam_score = 0
        self.exam_total = 0
        self.update_exam_score_label()
        if hasattr(self, "exam_feedback_label"):
            self.exam_feedback_label.config(text="成績已重置", fg="#8B5E3C")

    def update_exam_score_label(self):
        if not hasattr(self, "exam_score_label"):
            return

        accuracy = 0
        if self.exam_total:
            accuracy = round((self.exam_score / self.exam_total) * 100)

        self.exam_score_label.config(
            text=f"作答進度：{self.exam_score} / {self.exam_total}\n正確率：{accuracy}%"
        )

    # =========================================================
    # 單字收藏資料
    # =========================================================
    def load_dictionary_data(self):
        try:
            data = load_dictionary()

            if not isinstance(data, list):
                self.dictionary_data = []
                return

            cleaned = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                word = str(item.get("單字", "")).strip()
                if not word:
                    continue

                cleaned.append({
                    "language": str(item.get("language", "unknown")).strip() or "unknown",
                    "單字": str(item.get("單字", "")).strip(),
                    "讀音": str(item.get("讀音", "")).strip(),
                    "中文": str(item.get("中文", "")).strip(),
                    "英文": str(item.get("英文", "")).strip(),
                    "詞性": str(item.get("詞性", "")).strip(),
                    "分類": item.get("分類", []) if isinstance(item.get("分類", []), list) else [],
                    "例句": item.get("例句", []) if isinstance(item.get("例句", []), list) else [],
                    "用法": str(item.get("用法", "")).strip(),
                    "補充": str(item.get("補充", "")).strip(),
                    "圖片": str(item.get("圖片", "")).strip(),
                    "左頁分割": item.get("左頁分割", [0.18, 0.42, 0.40]) if isinstance(item.get("左頁分割", [0.18, 0.42, 0.40]), list) else [0.18, 0.42, 0.40]
                })

            self.dictionary_data = cleaned

        except Exception as e:
            print("load_dictionary_data error:", e)
            self.dictionary_data = []

    def get_all_tags(self):
        tags = set()
        has_unclassified = False

        for item in self.dictionary_data:
            item_tags = item.get("分類", [])
            if isinstance(item_tags, list) and item_tags:
                for tag in item_tags:
                    tag_text = str(tag).strip()
                    if tag_text:
                        tags.add(tag_text)
            else:
                has_unclassified = True

        if has_unclassified:
            tags.add("未分類")

        return ["全部"] + sorted(tags)

    def get_entry_sort_key(self, item):
        normalized_tags = self.get_normalized_tags(item)
        first_tag = normalized_tags[0] if normalized_tags else "未分類"

        return (
            1 if first_tag == "未分類" else 0,
            first_tag.lower(),
            str(item.get("單字", "")).lower()
        )

    def get_normalized_tags(self, item):
        tags = item.get("分類", [])
        if not isinstance(tags, list):
            tags = []

        normalized_tags = []
        for tag in tags:
            tag_text = str(tag).strip()
            if tag_text:
                normalized_tags.append(tag_text)

        if not normalized_tags:
            normalized_tags = ["未分類"]

        return normalized_tags

    def refresh_collection_tag_menu(self):
        if not hasattr(self, "collection_tag_menu"):
            return

        menu = self.collection_tag_menu["menu"]
        menu.delete(0, "end")

        tag_list = self.get_all_tags()

        for tag in tag_list:
            menu.add_command(
                label=tag,
                command=lambda value=tag: self.set_collection_tag(value)
            )

        if self.collection_tag_var.get() not in tag_list:
            self.collection_tag_var.set("全部")

    def set_collection_tag(self, value):
        self.collection_tag_var.set(value)
        self.collection_page = 1
        self.refresh_collection_list()

    def apply_collection_filters(self):
        keyword = self.collection_search_var.get().strip().lower()
        selected_tag = self.collection_tag_var.get().strip()
        selected_language = (self.selected_language or "").strip()

        result = []
        unclassified_items = []

        for item in self.dictionary_data:
            language = str(item.get("language", "unknown")).strip()
            word = str(item.get("單字", "")).strip()
            chinese = str(item.get("中文", "")).strip()
            reading = str(item.get("讀音", "")).strip()
            english = str(item.get("英文", "")).strip()

            # 入口先決定語言
            if selected_language and selected_language != "new":
                if language != selected_language:
                    continue

            normalized_tags = self.get_normalized_tags(item)

            full_text = f"{word} {chinese} {reading} {english} {' '.join(normalized_tags)}".lower()

            if keyword and keyword not in full_text:
                continue

            if selected_tag != "全部" and selected_tag not in normalized_tags:
                continue

            if normalized_tags == ["未分類"]:
                unclassified_items.append(item)
            else:
                result.append(item)

        sorted_unclassified_items = sorted(unclassified_items, key=self.get_entry_sort_key)
        sorted_result = sorted(result, key=self.get_entry_sort_key)

        if selected_tag == "未分類":
            self.collection_flat_items = sorted_unclassified_items
            self.filtered_dictionary_data = list(self.collection_flat_items)
            return

        self.collection_flat_items = sorted_result + sorted_unclassified_items
        self.filtered_dictionary_data = list(self.collection_flat_items)

    def get_collection_total_pages(self):
        if not self.collection_pages:
            return 1
        return len(self.collection_pages)

    def get_collection_page_data(self):
        if not self.collection_pages:
            return [], None

        page_index = max(0, min(self.collection_page - 1, len(self.collection_pages) - 1))
        page_info = self.collection_pages[page_index]
        return page_info["items"], page_info["previous_tag"]

    def get_collection_item_tag(self, item):
        normalized_tags = self.get_normalized_tags(item)
        return normalized_tags[0] if normalized_tags else "未分類"

    def get_collection_row_budget(self):
        if not hasattr(self, "collection_tree"):
            return self.collection_page_size

        tree_height = self.collection_tree.winfo_height()
        try:
            row_height = int(ttk.Style().lookup("Treeview", "rowheight") or 20)
        except Exception:
            row_height = 20

        if row_height <= 0:
            row_height = 20

        if tree_height <= 1:
            return max(self.collection_page_size, 18)

        visible_rows = max(8, (tree_height - 8) // row_height)
        return visible_rows

    def build_collection_pages(self):
        row_budget = self.get_collection_row_budget()
        selected_tag = self.collection_tag_var.get().strip()

        if not self.collection_flat_items:
            self.collection_pages = []
            return

        pages = []
        current_items = []
        current_rows = 0
        previous_tag_global = None
        page_previous_tag = None

        for item in self.collection_flat_items:
            item_tag = "未分類" if selected_tag == "未分類" else self.get_collection_item_tag(item)
            header_needed = previous_tag_global != item_tag
            needed_rows = 1 + (1 if header_needed else 0)

            if current_items and current_rows + needed_rows > row_budget:
                pages.append({
                    "items": current_items,
                    "previous_tag": page_previous_tag
                })
                current_items = []
                current_rows = 0
                page_previous_tag = previous_tag_global

            if not current_items:
                page_previous_tag = previous_tag_global

            current_items.append(item)
            current_rows += needed_rows
            previous_tag_global = item_tag

        if current_items:
            pages.append({
                "items": current_items,
                "previous_tag": page_previous_tag
            })

        self.collection_pages = pages

    def on_collection_tree_resized(self, event=None):
        if not hasattr(self, "collection_tree"):
            return

        new_budget = self.get_collection_row_budget()
        if new_budget == self.collection_page_size:
            return

        self.collection_page_size = new_budget

        if self.collection_resize_refresh_job is not None:
            try:
                self.window.after_cancel(self.collection_resize_refresh_job)
            except Exception:
                pass

        self.collection_resize_refresh_job = self.window.after(80, self.refresh_collection_list)

    def on_collection_search_changed(self, event=None):
        self.collection_page = 1
        self.refresh_collection_list()

    def prev_collection_page(self):
        if self.collection_page > 1:
            self.collection_page -= 1
            self.refresh_collection_list()

    def next_collection_page(self):
        total_pages = self.get_collection_total_pages()
        if self.collection_page < total_pages:
            self.collection_page += 1
            self.refresh_collection_list()

    def build_collection_tree(self, page_data, previous_tag=None):
        if not hasattr(self, "collection_tree"):
            return

        self.collection_tree.delete(*self.collection_tree.get_children())
        self.tree_item_to_entry = {}

        selected_tag = self.collection_tag_var.get().strip()
        if selected_tag == "未分類":
            unclassified_node = ""
            if previous_tag != "未分類":
                unclassified_node = self.collection_tree.insert(
                    "",
                    "end",
                    text="未分類",
                    open=True
                )

            for item in page_data:
                word = str(item.get("單字", "")).strip()
                reading = str(item.get("讀音", "")).strip()
                chinese = str(item.get("中文", "")).strip()

                if reading:
                    display_text = f"{word} ({reading})"
                elif chinese:
                    display_text = f"{word} - {chinese}"
                else:
                    display_text = word

                item_id = self.collection_tree.insert(
                    unclassified_node,
                    "end",
                    text=display_text,
                    open=False
                )

                self.tree_item_to_entry[item_id] = item

            return

        category_nodes = {}

        for item in page_data:
            first_tag = self.get_collection_item_tag(item)

            if first_tag not in category_nodes:
                if previous_tag == first_tag and not category_nodes:
                    category_nodes[first_tag] = ""
                else:
                    category_nodes[first_tag] = self.collection_tree.insert(
                        "",
                        "end",
                        text=first_tag,
                        open=True
                    )

            parent_category_id = category_nodes[first_tag]

            word = str(item.get("單字", "")).strip()
            reading = str(item.get("讀音", "")).strip()
            chinese = str(item.get("中文", "")).strip()

            if reading:
                display_text = f"{word} ({reading})"
            elif chinese:
                display_text = f"{word} - {chinese}"
            else:
                display_text = word

            item_id = self.collection_tree.insert(
                parent_category_id,
                "end",
                text=display_text,
                open=False
            )

            self.tree_item_to_entry[item_id] = item

    def refresh_collection_list(self):
        if not hasattr(self, "collection_tree"):
            return

        self.load_dictionary_data()
        self.refresh_collection_tag_menu()
        self.apply_collection_filters()
        self.build_collection_pages()

        total_pages = self.get_collection_total_pages()
        if self.collection_page > total_pages:
            self.collection_page = total_pages

        page_data, previous_tag = self.get_collection_page_data()

        print("dictionary_data =", len(self.dictionary_data))
        print("filtered_dictionary_data =", len(self.filtered_dictionary_data))
        print("page_data =", len(page_data))

        self.build_collection_tree(page_data, previous_tag)

        self.collection_page_label.config(
            text=f"第 {self.collection_page} 頁 / 共 {total_pages} 頁"
        )

    def on_select_collection_word(self, event=None):
        if not hasattr(self, "collection_tree"):
            return

        selection = self.collection_tree.selection()
        if not selection:
            return

        selected_id = selection[0]

        if selected_id not in self.tree_item_to_entry:
            return

        self.current_entry = self.tree_item_to_entry[selected_id]
        self.show_collection_detail(self.current_entry)

    def show_collection_detail(self, item):
        if not hasattr(self, "collection_original_text"):
            return

        self.collection_original_text.delete("1.0", tk.END)
        self.collection_note_text.delete("1.0", tk.END)
        self.collection_translation_text.delete("1.0", tk.END)
        self.collection_english_text.delete("1.0", tk.END)
        self.collection_reading_entry.delete(0, tk.END)
        self.collection_pos_entry.delete(0, tk.END)
        self.collection_tag_entry.delete(0, tk.END)
        self.collection_example_text.delete("1.0", tk.END)
        self.collection_usage_text.delete("1.0", tk.END)

        self.collection_original_text.insert("1.0", item.get("單字", ""))
        self.collection_note_text.insert("1.0", item.get("補充", ""))
        self.collection_translation_text.insert("1.0", item.get("中文", ""))
        self.collection_english_text.insert("1.0", item.get("英文", ""))
        self.collection_reading_entry.insert(0, item.get("讀音", ""))
        self.collection_pos_entry.insert(0, item.get("詞性", ""))

        tags = item.get("分類", [])
        if isinstance(tags, list):
            self.collection_tag_entry.insert(0, ", ".join(tags))

        examples = item.get("例句", [])
        if isinstance(examples, list):
            self.collection_example_text.insert("1.0", "\n".join(examples))

        self.collection_usage_text.insert("1.0", item.get("用法", ""))
        self.show_collection_image(item.get("圖片", ""))
        self.schedule_apply_collection_split(item.get("左頁分割", [0.18, 0.32, 0.50]))

    def show_empty_collection_detail(self):
        if not hasattr(self, "collection_original_text"):
            return

        self.collection_original_text.delete("1.0", tk.END)
        self.collection_note_text.delete("1.0", tk.END)
        self.collection_translation_text.delete("1.0", tk.END)
        self.collection_english_text.delete("1.0", tk.END)
        self.collection_reading_entry.delete(0, tk.END)
        self.collection_pos_entry.delete(0, tk.END)
        self.collection_tag_entry.delete(0, tk.END)
        self.collection_example_text.delete("1.0", tk.END)
        self.collection_usage_text.delete("1.0", tk.END)

        self.collection_original_text.insert("1.0", "請先從左邊選一個單字")
        self.collection_note_text.insert("1.0", "可在這裡記錄補充筆記")
        self.collection_translation_text.insert("1.0", "")
        self.collection_english_text.insert("1.0", "")
        self.clear_collection_image()
        self.schedule_apply_collection_split([0.18, 0.32, 0.50])

    def save_collection_entry(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先從左邊選一個單字")
            return

        original = self.collection_original_text.get("1.0", tk.END).strip()
        note = self.collection_note_text.get("1.0", tk.END).strip()
        chinese = self.collection_translation_text.get("1.0", tk.END).strip()
        english = self.collection_english_text.get("1.0", tk.END).strip()
        reading = self.collection_reading_entry.get().strip()
        pos = self.collection_pos_entry.get().strip()
        tag_raw = self.collection_tag_entry.get().strip()
        example_raw = self.collection_example_text.get("1.0", tk.END).strip()
        usage = self.collection_usage_text.get("1.0", tk.END).strip()
        image_path = self.collection_current_image_path.strip()
        split_value = self.get_current_collection_split()

        if not original:
            messagebox.showwarning("提示", "單字不能空白")
            return

        tags = [x.strip() for x in tag_raw.split(",") if x.strip()]
        examples = [x.strip() for x in example_raw.splitlines() if x.strip()]

        data = load_dictionary()

        target_index = None
        for i, item in enumerate(data):
            if item.get("單字", "") == self.current_entry.get("單字", ""):
                target_index = i
                break

        if target_index is None:
            messagebox.showerror("錯誤", "找不到要儲存的單字")
            return

        data[target_index]["單字"] = original
        data[target_index]["中文"] = chinese
        data[target_index]["英文"] = english
        data[target_index]["讀音"] = reading
        data[target_index]["詞性"] = pos
        data[target_index]["分類"] = tags
        data[target_index]["例句"] = examples
        data[target_index]["用法"] = usage
        data[target_index]["補充"] = note
        data[target_index]["圖片"] = image_path
        data[target_index]["左頁分割"] = split_value

        save_dictionary(data)

        self.current_entry = data[target_index]
        self.refresh_collection_list()
        messagebox.showinfo("成功", "已儲存單字內容")

    def reload_collection_area(self):
        self.collection_search_var.set("")
        self.collection_tag_var.set("全部")
        self.collection_page = 1
        self.current_entry = None
        self.refresh_collection_list()
        self.show_empty_collection_detail()
    
    def delete_current_word(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先從左邊選一個單字")
            return

        word = self.current_entry.get("單字", "").strip()
        if not word:
            messagebox.showwarning("提示", "目前沒有可刪除的單字")
            return

        confirm = messagebox.askyesno("確認刪除", f"確定要刪除「{word}」嗎？")
        if not confirm:
            return

        result = delete_word(word)

        if result == "已刪除單字":
            self.current_entry = None
            self.refresh_collection_list()
            self.show_empty_collection_detail()
            messagebox.showinfo("成功", result)
        else:
            messagebox.showerror("錯誤", result)

    def change_current_word_language(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先從左邊選一個單字")
            return

        word = self.current_entry.get("單字", "").strip()
        current_language = self.current_entry.get("language", "unknown").strip()

        if not word:
            messagebox.showwarning("提示", "目前沒有可切換的單字")
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("切換語言")
        dialog.geometry("380x180")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.configure(bg="#F5EAD9")

        label = tk.Label(
            dialog,
            text=f"「{word}」目前語言：{current_language}\n請選擇要改成哪個語言：",
            font=("Microsoft JhengHei", 11),
            bg="#F5EAD9",
            fg="#4A2F21",
            justify="center"
        )
        label.pack(pady=(20, 16))

        button_frame = tk.Frame(dialog, bg="#F5EAD9")
        button_frame.pack()

        options = [
            ("ja", "日文"),
            ("zh", "中文"),
            ("en", "英文"),
            ("ko", "韓文")
        ]

        for code, text in options:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Microsoft JhengHei", 10, "bold"),
                bg="#8B5E3C",
                fg="#FFF8EE",
                activebackground="#A06A43",
                activeforeground="#FFF8EE",
                relief="flat",
                bd=0,
                padx=14,
                pady=8,
                command=lambda c=code: self.apply_language_change(c, dialog)
            )
            btn.pack(side=tk.LEFT, padx=6)
    
    def apply_language_change(self, new_language, dialog):
        if self.current_entry is None:
            dialog.destroy()
            return

        word = self.current_entry.get("單字", "").strip()
        if not word:
            dialog.destroy()
            return

        data = load_dictionary()

        target_index = None
        for i, item in enumerate(data):
            if item.get("單字", "") == word:
                target_index = i
                break

        if target_index is None:
            dialog.destroy()
            messagebox.showerror("錯誤", "找不到要修改的單字")
            return

        data[target_index]["language"] = new_language
        save_dictionary(data)

        self.current_entry = data[target_index]
        dialog.destroy()
        self.refresh_collection_list()
        self.show_collection_detail(self.current_entry)
        messagebox.showinfo("成功", f"已切換為 {new_language}")
