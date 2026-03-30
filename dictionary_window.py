import tkinter as tk
from tkinter import messagebox


class DictionaryWindow:
    def __init__(self, parent, load_dictionary_func, save_dictionary_func):
        self.parent = parent
        self.load_dictionary = load_dictionary_func
        self.save_dictionary = save_dictionary_func

        self.current_page = 1
        self.page_size = 12
        self.selected_index_in_filtered = None

        self.search_var = tk.StringVar()
        self.tag_var = tk.StringVar(value="全部")

        self.window = tk.Toplevel(self.parent)
        self.window.title("古書字典")
        self.window.geometry("1180x720")
        self.window.minsize(980, 580)
        self.window.configure(bg="#F5EAD9")

        self.filtered_data = []
        self.current_entry = None

        self.build_ui()
        self.refresh_tag_options()
        self.refresh_list()

    # =========================================================
    # UI
    # =========================================================
    def build_ui(self):
        # ===== 最外層 =====
        self.main_frame = tk.Frame(self.window, bg="#F5EAD9")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        # ===== 標題 =====
        header = tk.Frame(
            self.main_frame,
            bg="#E7D6BE",
            bd=2,
            relief="solid",
            highlightbackground="#8B6A4E",
            highlightthickness=1
        )
        header.pack(fill=tk.X, pady=(0, 12))

        title_label = tk.Label(
            header,
            text="古書字典",
            font=("Microsoft JhengHei", 20, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=10
        )
        title_label.pack()

        # ===== 搜尋 / 篩選 / 分頁 =====
        top_bar = tk.Frame(
            self.main_frame,
            bg="#E7D6BE",
            bd=2,
            relief="solid",
            highlightbackground="#8B6A4E",
            highlightthickness=1
        )
        top_bar.pack(fill=tk.X, pady=(0, 12), ipady=8)

        search_label = tk.Label(
            top_bar,
            text="搜尋",
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21"
        )
        search_label.pack(side=tk.LEFT, padx=(12, 6))

        self.search_entry = tk.Entry(
            top_bar,
            textvariable=self.search_var,
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="solid",
            bd=1,
            width=24
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda e: self.on_filter_changed())

        tag_label = tk.Label(
            top_bar,
            text="分類",
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21"
        )
        tag_label.pack(side=tk.LEFT, padx=(0, 6))

        self.tag_menu = tk.OptionMenu(top_bar, self.tag_var, "全部")
        self.tag_menu.config(
            font=("Microsoft JhengHei", 10),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        self.tag_menu["menu"].config(
            font=("Microsoft JhengHei", 10),
            bg="#FBF6EE",
            fg="#3A2A1F"
        )
        self.tag_menu.pack(side=tk.LEFT, padx=(0, 12))

        filter_button = tk.Button(
            top_bar,
            text="套用",
            command=self.on_filter_changed,
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
        filter_button.pack(side=tk.LEFT, padx=(0, 10))

        clear_button = tk.Button(
            top_bar,
            text="清除搜尋",
            command=self.clear_filters,
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
        clear_button.pack(side=tk.LEFT)

        spacer = tk.Frame(top_bar, bg="#E7D6BE")
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.page_info_label = tk.Label(
            top_bar,
            text="第 1 頁 / 共 1 頁",
            font=("Microsoft JhengHei", 10),
            bg="#E7D6BE",
            fg="#6A4A35"
        )
        self.page_info_label.pack(side=tk.LEFT, padx=8)

        prev_button = tk.Button(
            top_bar,
            text="上一頁",
            command=self.prev_page,
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
        prev_button.pack(side=tk.LEFT, padx=4)

        next_button = tk.Button(
            top_bar,
            text="下一頁",
            command=self.next_page,
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
        next_button.pack(side=tk.LEFT, padx=(4, 12))

        # ===== 中間主體：左右區 =====
        body = tk.Frame(self.main_frame, bg="#F5EAD9")
        body.pack(fill=tk.BOTH, expand=True)

        # 左側清單
        left_panel = tk.Frame(
            body,
            bg="#E7D6BE",
            bd=2,
            relief="solid",
            highlightbackground="#8B6A4E",
            highlightthickness=1
        )
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 8), expand=False)
        left_panel.config(width=320)
        left_panel.pack_propagate(False)

        list_title = tk.Label(
            left_panel,
            text="單字列表",
            font=("Microsoft JhengHei", 14, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=10
        )
        list_title.pack(fill=tk.X)

        self.word_listbox = tk.Listbox(
            left_panel,
            font=("Microsoft JhengHei", 13),
            bg="#FBF6EE",
            fg="#3A2A1F",
            selectbackground="#C89B3C",
            selectforeground="#3A2A1F",
            relief="flat",
            bd=0
        )
        self.word_listbox.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.word_listbox.bind("<<ListboxSelect>>", self.on_select_word)

        # 右側詳細
        right_panel = tk.Frame(
            body,
            bg="#E7D6BE",
            bd=2,
            relief="solid",
            highlightbackground="#8B6A4E",
            highlightthickness=1
        )
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        detail_title = tk.Label(
            right_panel,
            text="單字內容",
            font=("Microsoft JhengHei", 14, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            pady=10
        )
        detail_title.pack(fill=tk.X)

        form = tk.Frame(right_panel, bg="#E7D6BE")
        form.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))

        # 單字
        self.word_entry = self.create_labeled_entry(form, "單字", 0)

        # 讀音
        self.reading_entry = self.create_labeled_entry(form, "讀音", 1)

        # 中文
        self.chinese_entry = self.create_labeled_entry(form, "中文", 2)

        # 英文
        self.english_entry = self.create_labeled_entry(form, "英文", 3)

        # 詞性
        self.pos_entry = self.create_labeled_entry(form, "詞性", 4)

        # 分類
        self.tags_entry = self.create_labeled_entry(form, "分類（用逗號分隔）", 5)

        # 例句
        example_label = tk.Label(
            form,
            text="例句（每行一個）",
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            anchor="w"
        )
        example_label.grid(row=6, column=0, sticky="nw", padx=(0, 8), pady=8)

        self.example_text = tk.Text(
            form,
            height=8,
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="solid",
            bd=1,
            wrap=tk.WORD
        )
        self.example_text.grid(row=6, column=1, sticky="nsew", pady=8)

        # 用法
        usage_label = tk.Label(
            form,
            text="用法",
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            anchor="w"
        )
        usage_label.grid(row=7, column=0, sticky="nw", padx=(0, 8), pady=8)

        self.usage_text = tk.Text(
            form,
            height=7,
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="solid",
            bd=1,
            wrap=tk.WORD
        )
        self.usage_text.grid(row=7, column=1, sticky="nsew", pady=8)

        form.grid_columnconfigure(1, weight=1)
        form.grid_rowconfigure(6, weight=1)
        form.grid_rowconfigure(7, weight=1)

        # ===== 底部操作按鈕 =====
        bottom_bar = tk.Frame(
            self.main_frame,
            bg="#E7D6BE",
            bd=2,
            relief="solid",
            highlightbackground="#8B6A4E",
            highlightthickness=1
        )
        bottom_bar.pack(fill=tk.X, pady=(12, 0), ipady=8)

        save_button = tk.Button(
            bottom_bar,
            text="儲存修改",
            command=self.save_current_entry,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2"
        )
        save_button.pack(side=tk.LEFT, padx=(12, 8))

        new_button = tk.Button(
            bottom_bar,
            text="新增空白單字",
            command=self.create_new_entry,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2"
        )
        new_button.pack(side=tk.LEFT, padx=8)

        delete_button = tk.Button(
            bottom_bar,
            text="刪除目前單字",
            command=self.delete_current_entry,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2"
        )
        delete_button.pack(side=tk.LEFT, padx=8)

        refresh_button = tk.Button(
            bottom_bar,
            text="重新整理",
            command=self.reload_all,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2"
        )
        refresh_button.pack(side=tk.LEFT, padx=8)

        close_button = tk.Button(
            bottom_bar,
            text="關閉",
            command=self.window.destroy,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#8B5E3C",
            fg="#FFF8EE",
            activebackground="#A06A43",
            activeforeground="#FFF8EE",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2"
        )
        close_button.pack(side=tk.RIGHT, padx=(8, 12))

    def create_labeled_entry(self, parent, label_text, row):
        label = tk.Label(
            parent,
            text=label_text,
            font=("Microsoft JhengHei", 10, "bold"),
            bg="#E7D6BE",
            fg="#4A2F21",
            anchor="w"
        )
        label.grid(row=row, column=0, sticky="w", padx=(0, 8), pady=8)

        entry = tk.Entry(
            parent,
            font=("Microsoft JhengHei", 11),
            bg="#FBF6EE",
            fg="#3A2A1F",
            relief="solid",
            bd=1
        )
        entry.grid(row=row, column=1, sticky="ew", pady=8)
        return entry

    # =========================================================
    # 資料處理
    # =========================================================
    def get_all_data(self):
        data = self.load_dictionary()
        if not isinstance(data, list):
            return []
        return data

    def refresh_tag_options(self):
        data = self.get_all_data()

        all_tags = set()
        for item in data:
            tags = item.get("分類", [])
            if isinstance(tags, list):
                for tag in tags:
                    if str(tag).strip():
                        all_tags.add(str(tag).strip())

        tag_list = ["全部"] + sorted(all_tags)

        menu = self.tag_menu["menu"]
        menu.delete(0, "end")

        for tag in tag_list:
            menu.add_command(
                label=tag,
                command=lambda value=tag: self.set_tag_filter(value)
            )

        if self.tag_var.get() not in tag_list:
            self.tag_var.set("全部")

    def set_tag_filter(self, value):
        self.tag_var.set(value)
        self.on_filter_changed()

    def apply_filters(self):
        data = self.get_all_data()
        keyword = self.search_var.get().strip().lower()
        selected_tag = self.tag_var.get().strip()

        result = []

        for item in data:
            word = str(item.get("單字", ""))
            reading = str(item.get("讀音", ""))
            chinese = str(item.get("中文", ""))
            english = str(item.get("英文", ""))
            pos = str(item.get("詞性", ""))
            usage = str(item.get("用法", ""))
            tags = item.get("分類", [])
            examples = item.get("例句", [])

            if not isinstance(tags, list):
                tags = []

            if not isinstance(examples, list):
                examples = []

            if keyword:
                whole_text = " ".join([
                    word, reading, chinese, english, pos, usage,
                    " ".join(tags),
                    " ".join([str(x) for x in examples])
                ]).lower()

                if keyword not in whole_text:
                    continue

            if selected_tag != "全部":
                if selected_tag not in tags:
                    continue

            result.append(item)

        self.filtered_data = result

    def get_total_pages(self):
        if not self.filtered_data:
            return 1
        return (len(self.filtered_data) - 1) // self.page_size + 1

    def get_current_page_data(self):
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return self.filtered_data[start:end]

    def refresh_list(self):
        self.apply_filters()

        total_pages = self.get_total_pages()
        if self.current_page > total_pages:
            self.current_page = total_pages

        self.word_listbox.delete(0, tk.END)

        page_data = self.get_current_page_data()

        for item in page_data:
            word = item.get("單字", "").strip()
            reading = item.get("讀音", "").strip()

            if reading:
                display_text = f"{word}　({reading})"
            else:
                display_text = word

            self.word_listbox.insert(tk.END, display_text)

        self.page_info_label.config(
            text=f"第 {self.current_page} 頁 / 共 {total_pages} 頁"
        )

        self.selected_index_in_filtered = None
        self.clear_detail_fields()

    def on_filter_changed(self):
        self.current_page = 1
        self.refresh_list()

    def clear_filters(self):
        self.search_var.set("")
        self.tag_var.set("全部")
        self.current_page = 1
        self.refresh_list()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_list()

    def next_page(self):
        total_pages = self.get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_list()

    def on_select_word(self, event=None):
        selection = self.word_listbox.curselection()
        if not selection:
            return

        index_on_page = selection[0]
        absolute_index = (self.current_page - 1) * self.page_size + index_on_page

        if absolute_index < 0 or absolute_index >= len(self.filtered_data):
            return

        self.selected_index_in_filtered = absolute_index
        self.current_entry = self.filtered_data[absolute_index]
        self.fill_detail_fields(self.current_entry)

    def fill_detail_fields(self, item):
        self.clear_detail_fields()

        self.word_entry.insert(0, item.get("單字", ""))
        self.reading_entry.insert(0, item.get("讀音", ""))
        self.chinese_entry.insert(0, item.get("中文", ""))
        self.english_entry.insert(0, item.get("英文", ""))
        self.pos_entry.insert(0, item.get("詞性", ""))

        tags = item.get("分類", [])
        if isinstance(tags, list):
            self.tags_entry.insert(0, ", ".join(tags))

        examples = item.get("例句", [])
        if isinstance(examples, list):
            self.example_text.insert("1.0", "\n".join(examples))

        self.usage_text.insert("1.0", item.get("用法", ""))

    def clear_detail_fields(self):
        for entry in [
            self.word_entry,
            self.reading_entry,
            self.chinese_entry,
            self.english_entry,
            self.pos_entry,
            self.tags_entry
        ]:
            entry.delete(0, tk.END)

        self.example_text.delete("1.0", tk.END)
        self.usage_text.delete("1.0", tk.END)

    def save_current_entry(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先從左側選一個單字")
            return

        new_word = self.word_entry.get().strip()
        if not new_word:
            messagebox.showwarning("提示", "單字不能是空白")
            return

        data = self.get_all_data()

        target_index = None
        for i, item in enumerate(data):
            if item is self.current_entry:
                target_index = i
                break

        if target_index is None:
            for i, item in enumerate(data):
                if (
                    item.get("單字", "") == self.current_entry.get("單字", "") and
                    item.get("讀音", "") == self.current_entry.get("讀音", "")
                ):
                    target_index = i
                    break

        if target_index is None:
            messagebox.showerror("錯誤", "找不到目前編輯的單字資料")
            return

        tags_raw = self.tags_entry.get().strip()
        tags_list = [x.strip() for x in tags_raw.split(",") if x.strip()]

        examples_raw = self.example_text.get("1.0", tk.END).strip()
        examples_list = [x.strip() for x in examples_raw.splitlines() if x.strip()]

        data[target_index] = {
            "單字": new_word,
            "讀音": self.reading_entry.get().strip(),
            "中文": self.chinese_entry.get().strip(),
            "英文": self.english_entry.get().strip(),
            "詞性": self.pos_entry.get().strip(),
            "分類": tags_list,
            "例句": examples_list,
            "用法": self.usage_text.get("1.0", tk.END).strip()
        }

        self.save_dictionary(data)
        messagebox.showinfo("成功", "已儲存修改")

        self.refresh_tag_options()
        self.refresh_list()

    def create_new_entry(self):
        data = self.get_all_data()

        new_item = {
            "單字": "新單字",
            "讀音": "",
            "中文": "",
            "英文": "",
            "詞性": "",
            "分類": [],
            "例句": [],
            "用法": ""
        }

        data.append(new_item)
        self.save_dictionary(data)

        self.refresh_tag_options()
        self.refresh_list()
        messagebox.showinfo("成功", "已新增空白單字")

    def delete_current_entry(self):
        if self.current_entry is None:
            messagebox.showwarning("提示", "請先選擇要刪除的單字")
            return

        confirm = messagebox.askyesno("確認刪除", "確定要刪除目前單字嗎？")
        if not confirm:
            return

        data = self.get_all_data()
        new_data = []

        removed = False
        for item in data:
            if not removed and item == self.current_entry:
                removed = True
                continue
            new_data.append(item)

        if not removed:
            # 備援：用欄位比對
            current_word = self.current_entry.get("單字", "")
            current_reading = self.current_entry.get("讀音", "")

            new_data = []
            removed = False
            for item in data:
                if (not removed and
                        item.get("單字", "") == current_word and
                        item.get("讀音", "") == current_reading):
                    removed = True
                    continue
                new_data.append(item)

        if not removed:
            messagebox.showerror("錯誤", "刪除失敗，找不到資料")
            return

        self.save_dictionary(new_data)
        self.current_entry = None
        self.refresh_tag_options()
        self.refresh_list()
        messagebox.showinfo("成功", "已刪除單字")

    def reload_all(self):
        self.current_page = 1
        self.current_entry = None
        self.refresh_tag_options()
        self.refresh_list()
        messagebox.showinfo("完成", "字典已重新整理")