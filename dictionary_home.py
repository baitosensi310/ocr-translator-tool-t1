import tkinter as tk
from tkinter import messagebox
from dictionary_manager import load_dictionary, save_dictionary


class DictionaryHome:
    def __init__(self, parent):
        self.parent = parent
        self.selected_language = None

        self.dictionary_data = []
        self.filtered_dictionary_data = []
        self.current_entry = None

        self.collection_search_var = tk.StringVar()
        self.collection_tag_var = tk.StringVar(value="全部")
        self.collection_page = 1
        self.collection_page_size = 12

        self.window = tk.Toplevel(self.parent)
        self.window.title("字典主頁")
        self.window.geometry("1180x760+260+120")
        self.window.minsize(980, 620)
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
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

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

        # 左側：單字清單
        left_panel = tk.Frame(body, bg="#EADCC8", bd=0)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.config(width=280)
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

        self.collection_listbox = tk.Listbox(
            left_panel,
            font=("Microsoft JhengHei", 12),
            bg="#FBF6EE",
            fg="#3A2A1F",
            selectbackground="#C89B3C",
            selectforeground="#3A2A1F",
            relief="flat",
            bd=0
        )
        self.collection_listbox.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.collection_listbox.bind("<<ListboxSelect>>", self.on_select_collection_word)

        page_bar = tk.Frame(left_panel, bg="#EADCC8", height=40)
        page_bar.pack(fill=tk.X, padx=12, pady=(0, 12))
        page_bar.pack_propagate(False)

        prev_btn = self.create_soft_button(page_bar, "上一頁", self.prev_collection_page, width=8)
        prev_btn.pack(side=tk.LEFT)

        self.collection_page_label = tk.Label(
            page_bar,
            text="第 1 頁 / 共 1 頁",
            font=("Microsoft JhengHei", 10),
            bg="#EADCC8",
            fg="#6A4A35"
        )
        self.collection_page_label.pack(side=tk.LEFT, padx=10)

        next_btn = self.create_soft_button(page_bar, "下一頁", self.next_collection_page, width=8)
        next_btn.pack(side=tk.RIGHT)

        # 右側：書本雙頁
        book_frame = tk.Frame(body, bg="#D8C2A2", bd=0)
        book_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        left_page = tk.Frame(book_frame, bg="#FBF6EE", bd=0)
        left_page.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 8), pady=16)

        right_page = tk.Frame(book_frame, bg="#FBF6EE", bd=0)
        right_page.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 16), pady=16)

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

        translation_label = tk.Label(
            right_page,
            text="翻譯",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        translation_label.pack(fill=tk.X, padx=14, pady=(8, 4))

        self.collection_translation_text = tk.Text(
            right_page,
            height=6,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0,
            wrap=tk.WORD
        )
        self.collection_translation_text.pack(fill=tk.X, padx=14, pady=(0, 10))

        reading_label = tk.Label(
            right_page,
            text="讀音",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        reading_label.pack(fill=tk.X, padx=14, pady=(6, 4))

        self.collection_reading_entry = tk.Entry(
            right_page,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0
        )
        self.collection_reading_entry.pack(fill=tk.X, padx=14, pady=(0, 12), ipady=6)

        tag_label = tk.Label(
            right_page,
            text="分類 tag（用逗號分隔）",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        tag_label.pack(fill=tk.X, padx=14, pady=(6, 4))

        self.collection_tag_entry = tk.Entry(
            right_page,
            font=("Microsoft JhengHei", 11),
            bg="#F8F1E7",
            fg="#3A2A1F",
            relief="flat",
            bd=0
        )
        self.collection_tag_entry.pack(fill=tk.X, padx=14, pady=(0, 12), ipady=6)

        suggestion_title = tk.Label(
            right_page,
            text="建議",
            font=("Microsoft JhengHei", 12, "bold"),
            bg="#FBF6EE",
            fg="#4A2F21",
            anchor="w"
        )
        suggestion_title.pack(fill=tk.X, padx=14, pady=(8, 4))

        suggestion_text = tk.Label(
            right_page,
            text=(
                "目前核心欄位：\n"
                "1. 原文\n"
                "2. 翻譯\n"
                "3. 讀音\n"
                "4. 分類 tag\n\n"
                "之後可補：\n"
                "5. 詞性\n"
                "6. 例句\n"
                "7. 圖片"
            ),
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#6A4A35",
            justify="left",
            anchor="w"
        )
        suggestion_text.pack(fill=tk.X, padx=14, pady=(0, 10))

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X)

        refresh_btn = self.create_soft_button(bottom, "重新整理", self.refresh_collection_list, width=10)
        refresh_btn.pack(side=tk.LEFT)

        save_btn = self.create_soft_button(bottom, "儲存內容", self.save_collection_entry, width=10)
        save_btn.pack(side=tk.LEFT, padx=10)

        back_btn = self.create_soft_button(bottom, "返回索引", self.build_index_page_callback, width=10)
        back_btn.pack(side=tk.LEFT, padx=10)

        close_btn = self.create_soft_button(bottom, "關閉", self.window.destroy, width=10)
        close_btn.pack(side=tk.RIGHT)

        self.refresh_collection_list()

    # =========================================================
    # 3. 考試區（預留）
    # =========================================================
    def open_exam_area(self):
        self.clear_page()

        outer = tk.Frame(self.main_frame, bg="#F5EAD9")
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        header = tk.Frame(outer, bg="#E7D6BE")
        header.pack(fill=tk.X, pady=(0, 18))

        title = tk.Label(
            header,
            text="考試區",
            font=("Microsoft JhengHei", 22, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=18
        )
        title.pack()

        body = tk.Frame(outer, bg="#EADCC8", bd=0)
        body.pack(fill=tk.BOTH, expand=True)

        info = tk.Label(
            body,
            text=(
                "這裡先保留給未來的測驗系統。\n\n"
                "之後可以考慮放：\n"
                "• 看原文選翻譯\n"
                "• 看翻譯回想原文\n"
                "• 聽讀音選單字\n"
                "• 分類 tag 測驗\n"
                "• 錯題重練\n"
                "• 分頁或章節測驗"
            ),
            font=("Microsoft JhengHei", 13),
            bg="#EADCC8",
            fg="#4A2F21",
            justify="left",
            pady=40
        )
        info.pack()

        bottom = tk.Frame(outer, bg="#F5EAD9")
        bottom.pack(fill=tk.X, pady=(14, 0))

        back_btn = self.create_soft_button(bottom, "返回索引", self.build_index_page_callback, width=10)
        back_btn.pack(side=tk.LEFT)

        close_btn = self.create_soft_button(bottom, "關閉", self.window.destroy, width=10)
        close_btn.pack(side=tk.RIGHT)

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

                if "分類" not in item or not isinstance(item.get("分類"), list):
                    item["分類"] = []

                if "讀音" not in item:
                    item["讀音"] = ""

                if "中文" not in item:
                    item["中文"] = ""

                if "英文" not in item:
                    item["英文"] = ""

                if "詞性" not in item:
                    item["詞性"] = ""

                if "例句" not in item or not isinstance(item.get("例句"), list):
                    item["例句"] = []

                if "用法" not in item:
                    item["用法"] = ""

                cleaned.append(item)

            self.dictionary_data = cleaned

        except Exception as e:
            print("load_dictionary_data error:", e)
            self.dictionary_data = []

    def get_all_tags(self):
        tags = set()

        for item in self.dictionary_data:
            item_tags = item.get("分類", [])
            if isinstance(item_tags, list):
                for tag in item_tags:
                    tag_text = str(tag).strip()
                    if tag_text:
                        tags.add(tag_text)

        return ["全部"] + sorted(tags)

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

        result = []

        for item in self.dictionary_data:
            word = str(item.get("單字", "")).strip()
            chinese = str(item.get("中文", "")).strip()
            reading = str(item.get("讀音", "")).strip()
            english = str(item.get("英文", "")).strip()
            tags = item.get("分類", [])

            if not isinstance(tags, list):
                tags = []

            full_text = f"{word} {chinese} {reading} {english} {' '.join(tags)}".lower()

            if keyword and keyword not in full_text:
                continue

            if selected_tag != "全部" and selected_tag not in tags:
                continue

            result.append(item)

        self.filtered_dictionary_data = result

    def get_collection_total_pages(self):
        if not self.filtered_dictionary_data:
            return 1
        return (len(self.filtered_dictionary_data) - 1) // self.collection_page_size + 1

    def get_collection_page_data(self):
        start = (self.collection_page - 1) * self.collection_page_size
        end = start + self.collection_page_size
        return self.filtered_dictionary_data[start:end]

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

    def refresh_collection_list(self):
        if not hasattr(self, "collection_listbox"):
            return

        self.load_dictionary_data()
        self.refresh_collection_tag_menu()
        self.apply_collection_filters()

        total_pages = self.get_collection_total_pages()
        if self.collection_page > total_pages:
            self.collection_page = total_pages

        self.collection_listbox.delete(0, tk.END)

        page_data = self.get_collection_page_data()

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

            self.collection_listbox.insert(tk.END, display_text)

        if hasattr(self, "collection_page_label"):
            self.collection_page_label.config(
                text=f"第 {self.collection_page} 頁 / 共 {total_pages} 頁"
            )

        print("dictionary_data =", len(self.dictionary_data))
        print("filtered_dictionary_data =", len(self.filtered_dictionary_data))

    def on_select_collection_word(self, event=None):
        if not hasattr(self, "collection_listbox"):
            return

        selection = self.collection_listbox.curselection()
        if not selection:
            return

        index_on_page = selection[0]
        absolute_index = (self.collection_page - 1) * self.collection_page_size + index_on_page

        if absolute_index < 0 or absolute_index >= len(self.filtered_dictionary_data):
            return

        self.current_entry = self.filtered_dictionary_data[absolute_index]
        self.show_collection_detail(self.current_entry)

    def show_collection_detail(self, item):
        if not hasattr(self, "collection_original_text"):
            return

        self.collection_original_text.delete("1.0", tk.END)
        self.collection_translation_text.delete("1.0", tk.END)
        self.collection_reading_entry.delete(0, tk.END)
        self.collection_tag_entry.delete(0, tk.END)

        self.collection_original_text.insert("1.0", item.get("單字", ""))
        self.collection_translation_text.insert("1.0", item.get("中文", ""))
        self.collection_reading_entry.insert(0, item.get("讀音", ""))

        tags = item.get("分類", [])
        if isinstance(tags, list):
            self.collection_tag_entry.insert(0, ", ".join(tags))

    def save_collection_entry(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先從左邊選一個單字")
            return

        original = self.collection_original_text.get("1.0", tk.END).strip()
        translation = self.collection_translation_text.get("1.0", tk.END).strip()
        reading = self.collection_reading_entry.get().strip()
        tag_raw = self.collection_tag_entry.get().strip()

        tags = [x.strip() for x in tag_raw.split(",") if x.strip()]

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
        data[target_index]["中文"] = translation
        data[target_index]["讀音"] = reading
        data[target_index]["分類"] = tags

        save_dictionary(data)

        self.current_entry = data[target_index]
        self.refresh_collection_list()
        messagebox.showinfo("成功", "已儲存單字內容")