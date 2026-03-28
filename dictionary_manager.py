import json
import os

FILE_PATH = "dictionary.json"


def create_empty_entry(word):
    return {
        "單字": word,
        "讀音": "",
        "中文": "",
        "英文": "",
        "詞性": "",
        "分類": [],
        "例句": [],
        "用法": ""
    }


def normalize_entry(item):
    """
    Convert old dictionary format to new format.

    Old format example:
    {
        "word": "専門",
        "meaning": "專門",
        "tag": "N2"
    }

    New format example:
    {
        "單字": "専門",
        "讀音": "",
        "中文": "專門",
        "英文": "",
        "詞性": "",
        "分類": [],
        "例句": [],
        "用法": ""
    }
    """

    # Already new format
    if "單字" in item:
        return {
            "單字": str(item.get("單字", "")).strip(),
            "讀音": str(item.get("讀音", "")).strip(),
            "中文": str(item.get("中文", "")).strip(),
            "英文": str(item.get("英文", "")).strip(),
            "詞性": str(item.get("詞性", "")).strip(),
            "分類": item.get("分類", []) if isinstance(item.get("分類", []), list) else [],
            "例句": item.get("例句", []) if isinstance(item.get("例句", []), list) else [],
            "用法": str(item.get("用法", "")).strip()
        }

    # Convert old format to new format
    word = str(item.get("word", "")).strip()
    meaning = str(item.get("meaning", "")).strip()
    tag = str(item.get("tag", "")).strip()

    return {
        "單字": word,
        "讀音": "",
        "中文": meaning,
        "英文": "",
        "詞性": "",
        "分類": [tag] if tag else [],
        "例句": [],
        "用法": ""
    }


def load_dictionary():
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return []

    if not isinstance(data, list):
        return []

    new_data = []
    has_old_format = False

    for item in data:
        if not isinstance(item, dict):
            continue

        if "word" in item or "meaning" in item or "tag" in item:
            has_old_format = True

        new_data.append(normalize_entry(item))

    # Auto-save if old format was found
    if has_old_format:
        save_dictionary(new_data)

    return new_data


def save_dictionary(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_word(word):
    word = word.strip()

    if not word:
        return "不能加入空白文字"

    data = load_dictionary()

    for item in data:
        if item["單字"] == word:
            return "已存在"

    new_entry = create_empty_entry(word)
    data.append(new_entry)
    save_dictionary(data)

    return "已加入字典"


def update_word(word, reading=None, chinese=None, english=None, part_of_speech=None,
                categories=None, examples=None, usage=None):
    data = load_dictionary()

    for item in data:
        if item["單字"] == word:
            if reading is not None:
                item["讀音"] = str(reading).strip()

            if chinese is not None:
                item["中文"] = str(chinese).strip()

            if english is not None:
                item["英文"] = str(english).strip()

            if part_of_speech is not None:
                item["詞性"] = str(part_of_speech).strip()

            if categories is not None:
                if isinstance(categories, list):
                    item["分類"] = categories
                else:
                    item["分類"] = []

            if examples is not None:
                if isinstance(examples, list):
                    item["例句"] = examples
                else:
                    item["例句"] = []

            if usage is not None:
                item["用法"] = str(usage).strip()

            save_dictionary(data)
            return "已更新"

    return "找不到單字"


def get_word(word):
    data = load_dictionary()

    for item in data:
        if item["單字"] == word:
            return item

    return None


def delete_word(word):
    data = load_dictionary()
    new_data = []

    for item in data:
        if item["單字"] != word:
            new_data.append(item)

    if len(new_data) == len(data):
        return "找不到單字"

    save_dictionary(new_data)
    return "已刪除"