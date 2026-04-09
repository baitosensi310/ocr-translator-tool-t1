import random
import tkinter as tk
from tkinter import messagebox, ttk
from dictionary_manager import load_dictionary, save_dictionary, delete_word


class DictionaryHome:
    def __init__(self, parent):
        self.parent = parent
        self.selected_language = None

        self.dictionary_data = []
        self.filtered_dictionary_data = []
        self.collection_flat_items = []
        self.current_entry = None
        self.tree_item_to_entry = {}

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

        self.window = tk.Toplevel(self.parent)
        self.window.title("字典主頁")
        self.window.geometry("1280x780+260+120")
        self.window.minsize(1080, 680)
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
            self.parent.withdraw()
        except Exception:
            messagebox.showwarning("提示", "目前無法隱藏工具列")

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

        close_btn = self.create_soft_button(bottom, "關閉", self.window.destroy, width=10)
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

        back_btn = self.create_soft_button(bottom, "返回語言選擇", self.build_home_page, width=12)
        back_btn.pack(side=tk.LEFT)

        close_btn = self.create_soft_button(bottom, "關閉", self.window.destroy, width=10)
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

        outer.after(120, lambda: content.sash_place(0, 520, 0))

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X, pady=(14, 0))

        back_btn = self.create_soft_button(bottom, "返回索引", self.build_index_page_callback, width=10)
        back_btn.pack(side=tk.LEFT)

        hide_toolbar_btn = self.create_soft_button(bottom, "隱藏工具列", self.hide_toolbar, width=10)
        hide_toolbar_btn.pack(side=tk.LEFT, padx=10)

        close_btn = self.create_soft_button(bottom, "關閉", self.window.destroy, width=10)
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

        upload_hint = tk.Label(
            left_page,
            text="這裡之後可放圖片\n可讓使用者上傳插圖，或先留白",
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#6A4A35",
            justify="center",
            pady=20
        )
        upload_hint.pack()

        original_label = tk.Label(
            left_page,
            text="原文",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        original_label.pack(fill=tk.X, padx=14, pady=(12, 4))

        self.collection_original_text = tk.Text(
            left_page,
            height=8,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            wrap=tk.WORD
        )
        self.collection_original_text.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

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

        refresh_btn = self.create_soft_button(bottom, "重新整理", self.reload_collection_area, width=10)
        refresh_btn.pack(side=tk.LEFT)

        save_btn = self.create_soft_button(bottom, "儲存內容", self.save_collection_entry, width=10)
        save_btn.pack(side=tk.LEFT, padx=10)

        back_btn = self.create_soft_button(bottom, "返回索引", self.build_index_page_callback, width=10)
        back_btn.pack(side=tk.LEFT, padx=10)

        close_btn = self.create_soft_button(bottom, "關閉", self.window.destroy, width=10)
        close_btn.pack(side=tk.RIGHT)

        self.refresh_collection_list()
        self.show_empty_collection_detail()

        delete_btn = self.create_soft_button(bottom, "刪除單字", self.delete_current_word, width=10)
        delete_btn.pack(side=tk.LEFT, padx=10)

        change_lang_btn = self.create_soft_button(bottom, "切換語言", self.change_current_word_language, width=10)
        change_lang_btn.pack(side=tk.LEFT, padx=10)


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
            fg="#3A2A1F",
            selectcolor="#FBF6EE",
            activebackground="#EADCC8",
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
            fg="#3A2A1F",
            selectcolor="#FBF6EE",
            activebackground="#EADCC8",
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
            btn = tk.Radiobutton(
                choice_frame,
                text="",
                variable=self.exam_choice_var,
                value="",
                font=("Microsoft JhengHei", 11),
                bg="#FBF6EE",
                fg="#3A2A1F",
                selectcolor="#FFF7E8",
                activebackground="#FBF6EE",
                anchor="w",
                justify="left"
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

        back_btn = self.create_soft_button(bottom, "返回索引", self.build_index_page_callback, width=10)
        back_btn.pack(side=tk.LEFT)

        close_btn = self.create_soft_button(bottom, "關閉", self.window.destroy, width=10)
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
            self.exam_hint_label.config(text=hint_text)
            for btn in self.exam_choice_buttons:
                btn.pack_forget()
            self.exam_answer_entry.pack(fill=tk.X, padx=18, pady=(0, 12), ipady=8)
            self.exam_answer_entry.focus_set()
            return

        self.exam_question_type_label.config(text="題型：看中文選單字")
        self.exam_prompt_label.config(text=str(item.get("中文", "")).strip())
        reading = str(item.get("讀音", "")).strip()
        self.exam_hint_label.config(text=f"讀音提示：{reading}" if reading else "讀音提示：無")
        self.exam_answer_entry.pack_forget()

        options = self.build_exam_choices(item)
        for btn in self.exam_choice_buttons:
            btn.pack_forget()

        for btn, option in zip(self.exam_choice_buttons, options):
            btn.config(text=option, value=option)
            btn.pack(fill=tk.X, pady=3)

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
        english = str(self.exam_current_question.get("英文", "")).strip()
        tags = ", ".join(self.get_normalized_tags(self.exam_current_question))

        return (
            f"正解：{word}\n"
            f"讀音：{reading or '未填寫'}\n"
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
                    "用法": str(item.get("用法", "")).strip()
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
        if not self.collection_flat_items:
            return 1
        return (len(self.collection_flat_items) - 1) // self.collection_page_size + 1

    def get_collection_page_data(self):
        start = (self.collection_page - 1) * self.collection_page_size
        end = start + self.collection_page_size
        return self.collection_flat_items[start:end]

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

    def build_collection_tree(self, page_data):
        if not hasattr(self, "collection_tree"):
            return

        self.collection_tree.delete(*self.collection_tree.get_children())
        self.tree_item_to_entry = {}

        selected_tag = self.collection_tag_var.get().strip()
        if selected_tag == "未分類":
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
            normalized_tags = self.get_normalized_tags(item)
            first_tag = normalized_tags[0] if normalized_tags else "未分類"

            if first_tag not in category_nodes:
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

        total_pages = self.get_collection_total_pages()
        if self.collection_page > total_pages:
            self.collection_page = total_pages

        page_data = self.get_collection_page_data()

        print("dictionary_data =", len(self.dictionary_data))
        print("filtered_dictionary_data =", len(self.filtered_dictionary_data))
        print("page_data =", len(page_data))

        self.build_collection_tree(page_data)

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
        self.collection_translation_text.delete("1.0", tk.END)
        self.collection_english_text.delete("1.0", tk.END)
        self.collection_reading_entry.delete(0, tk.END)
        self.collection_pos_entry.delete(0, tk.END)
        self.collection_tag_entry.delete(0, tk.END)
        self.collection_example_text.delete("1.0", tk.END)
        self.collection_usage_text.delete("1.0", tk.END)

        self.collection_original_text.insert("1.0", item.get("單字", ""))
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

    def show_empty_collection_detail(self):
        if not hasattr(self, "collection_original_text"):
            return

        self.collection_original_text.delete("1.0", tk.END)
        self.collection_translation_text.delete("1.0", tk.END)
        self.collection_english_text.delete("1.0", tk.END)
        self.collection_reading_entry.delete(0, tk.END)
        self.collection_pos_entry.delete(0, tk.END)
        self.collection_tag_entry.delete(0, tk.END)
        self.collection_example_text.delete("1.0", tk.END)
        self.collection_usage_text.delete("1.0", tk.END)

        self.collection_original_text.insert("1.0", "請先從左邊選一個單字")
        self.collection_translation_text.insert("1.0", "")
        self.collection_english_text.insert("1.0", "")

    def save_collection_entry(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先從左邊選一個單字")
            return

        original = self.collection_original_text.get("1.0", tk.END).strip()
        chinese = self.collection_translation_text.get("1.0", tk.END).strip()
        english = self.collection_english_text.get("1.0", tk.END).strip()
        reading = self.collection_reading_entry.get().strip()
        pos = self.collection_pos_entry.get().strip()
        tag_raw = self.collection_tag_entry.get().strip()
        example_raw = self.collection_example_text.get("1.0", tk.END).strip()
        usage = self.collection_usage_text.get("1.0", tk.END).strip()

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
