import json
import os

FILE_PATH = "dictionary.json"


def create_empty_entry(word: str) -> dict:
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


def normalize_entry(item: dict) -> dict:
    # 新格式
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

    # 舊格式轉新格式
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


def load_dictionary() -> list:
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
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

    if has_old_format:
        save_dictionary(new_data)

    return new_data


def save_dictionary(data: list) -> None:
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_word(word: str) -> str:
    word = word.strip()

    if not word:
        return "不能加入空白文字"

    data = load_dictionary()

    for item in data:
        if item["單字"] == word:
            return "已存在"

    data.append(create_empty_entry(word))
    save_dictionary(data)
    return "已加入字典"


def update_word(
    old_word: str,
    new_word: str,
    reading: str,
    chinese: str,
    english: str,
    part_of_speech: str,
    categories: list,
    examples: list,
    usage: str
) -> str:
    data = load_dictionary()

    for item in data:
        if item["單字"] == old_word:
            item["單字"] = new_word.strip()
            item["讀音"] = reading.strip()
            item["中文"] = chinese.strip()
            item["英文"] = english.strip()
            item["詞性"] = part_of_speech.strip()
            item["分類"] = categories if isinstance(categories, list) else []
            item["例句"] = examples if isinstance(examples, list) else []
            item["用法"] = usage.strip()

            save_dictionary(data)
            return "已更新"

    return "找不到單字"


def delete_word(word: str) -> str:
    data = load_dictionary()
    new_data = [item for item in data if item.get("單字", "") != word]

    if len(new_data) == len(data):
        return "找不到單字"

    save_dictionary(new_data)
    return "已刪除"